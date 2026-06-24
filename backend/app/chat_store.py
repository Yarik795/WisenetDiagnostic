from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Optional

import sqlite3

from .state_store import DEFAULT_DB_PATH


@dataclass
class ChatSessionRow:
    id: str
    title: str
    created_at: datetime


@dataclass
class ChatMessageRow:
    id: int
    session_id: str
    role: str
    content: str
    sql: Optional[str]
    chart_json: Optional[str]
    table_json: Optional[str]
    created_at: datetime


class ChatStore:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or DEFAULT_DB_PATH

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT 'Новый чат',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    sql TEXT,
                    chart_json TEXT,
                    table_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
                );

                CREATE INDEX IF NOT EXISTS idx_chat_messages_session
                    ON chat_messages(session_id, created_at);
                """
            )

    def create_session(self, title: str = "Новый чат") -> ChatSessionRow:
        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO chat_sessions (id, title, created_at) VALUES (?, ?, ?)",
                (session_id, title, now),
            )
        return ChatSessionRow(id=session_id, title=title, created_at=_parse_dt(now))

    def list_sessions(self, limit: int = 50) -> list[ChatSessionRow]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, title, created_at FROM chat_sessions
                ORDER BY created_at DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            ChatSessionRow(
                id=row["id"],
                title=row["title"],
                created_at=_parse_dt(row["created_at"]),
            )
            for row in rows
        ]

    def list_sessions_with_messages(self, limit: int = 50) -> list[ChatSessionRow]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT s.id, s.title, s.created_at
                FROM chat_sessions s
                WHERE EXISTS (
                    SELECT 1 FROM chat_messages m WHERE m.session_id = s.id
                )
                ORDER BY (
                    SELECT MAX(m.created_at) FROM chat_messages m WHERE m.session_id = s.id
                ) DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            ChatSessionRow(
                id=row["id"],
                title=row["title"],
                created_at=_parse_dt(row["created_at"]),
            )
            for row in rows
        ]

    def get_latest_session(self) -> Optional[ChatSessionRow]:
        sessions = self.list_sessions_with_messages(limit=1)
        return sessions[0] if sessions else None

    def delete_empty_sessions(self) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                DELETE FROM chat_sessions
                WHERE id NOT IN (
                    SELECT DISTINCT session_id FROM chat_messages
                )
                """
            )
            return cur.rowcount

    def get_message(self, message_id: int) -> Optional[ChatMessageRow]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, session_id, role, content, sql, chart_json, table_json, created_at
                FROM chat_messages WHERE id = ?
                """,
                (message_id,),
            ).fetchone()
        if row is None:
            return None
        return _row_to_message(row)

    def has_assistant_reply_after(self, session_id: str, user_message_id: int) -> bool:
        messages = self.list_messages(session_id)
        found = False
        for msg in messages:
            if msg.id == user_message_id:
                found = True
                continue
            if found and msg.role == "assistant":
                return True
        return False

    def get_session(self, session_id: str) -> Optional[ChatSessionRow]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, title, created_at FROM chat_sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return ChatSessionRow(
            id=row["id"],
            title=row["title"],
            created_at=_parse_dt(row["created_at"]),
        )

    def update_session_title(self, session_id: str, title: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE chat_sessions SET title = ? WHERE id = ?",
                (title, session_id),
            )

    def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        *,
        sql: Optional[str] = None,
        chart_json: Optional[str] = None,
        table_json: Optional[str] = None,
    ) -> ChatMessageRow:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO chat_messages
                    (session_id, role, content, sql, chart_json, table_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (session_id, role, content, sql, chart_json, table_json, now),
            )
            msg_id = cur.lastrowid
        return ChatMessageRow(
            id=msg_id,
            session_id=session_id,
            role=role,
            content=content,
            sql=sql,
            chart_json=chart_json,
            table_json=table_json,
            created_at=_parse_dt(now),
        )

    def list_messages(self, session_id: str) -> list[ChatMessageRow]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, session_id, role, content, sql, chart_json, table_json, created_at
                FROM chat_messages WHERE session_id = ?
                ORDER BY created_at ASC, id ASC
                """,
                (session_id,),
            ).fetchall()
        return [_row_to_message(row) for row in rows]

    def history_for_llm(
        self,
        session_id: str,
        *,
        max_messages: int,
    ) -> list[dict[str, str]]:
        messages = self.list_messages(session_id)
        if len(messages) > max_messages:
            messages = messages[-max_messages:]
        return [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.role in ("user", "assistant")
        ]


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _row_to_message(row: sqlite3.Row) -> ChatMessageRow:
    return ChatMessageRow(
        id=row["id"],
        session_id=row["session_id"],
        role=row["role"],
        content=row["content"],
        sql=row["sql"],
        chart_json=row["chart_json"],
        table_json=row["table_json"],
        created_at=_parse_dt(row["created_at"]),
    )
