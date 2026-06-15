from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|attach|pragma|create|replace|vacuum|reindex)\b",
    re.I,
)


def is_safe_select(sql: str) -> bool:
    s = sql.strip().rstrip(";")
    if not s:
        return False
    if ";" in s:
        return False
    if not re.match(r"(?is)^\s*(select|with)\b", s):
        return False
    return FORBIDDEN.search(s) is None


def _ensure_limit(sql: str, max_rows: int) -> str:
    s = sql.strip().rstrip(";")
    if re.search(r"(?is)\blimit\s+\d+", s):
        return s
    return f"{s} LIMIT {max_rows}"


def run_readonly(
    db_path: Path,
    sql: str,
    *,
    max_rows: int = 1000,
) -> tuple[list[str], list[dict[str, Any]], int, bool]:
    if not is_safe_select(sql):
        raise ValueError("Разрешены только SELECT-запросы без изменения данных")

    limited_sql = _ensure_limit(sql, max_rows)
    uri = f"file:{db_path.resolve()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=10)
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(limited_sql)
        columns = [d[0] for d in (cur.description or [])]
        rows = [dict(row) for row in cur.fetchmany(max_rows + 1)]
        truncated = len(rows) > max_rows
        if truncated:
            rows = rows[:max_rows]
        return columns, rows, len(rows), truncated
    finally:
        conn.close()
