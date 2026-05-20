from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "monitoring.db"


@dataclass
class ChannelRow:
    id: int
    recorder_id: str
    channel_no: int
    name: Optional[str]
    camera_ip: Optional[str]
    camera_model: Optional[str]
    source_state: Optional[str]
    health_status: str
    health_reason: Optional[str]
    video_loss: Optional[bool]
    last_polled_at: Optional[datetime]


@dataclass
class RecorderMetricsRow:
    recorder_id: str
    model: Optional[str]
    firmware_version: Optional[str]
    device_online: bool
    health_status: str
    health_reason: Optional[str]
    ntp_status: Optional[str]
    time_skew_seconds: Optional[float]
    storage_used_percent: Optional[float]
    storage_status: Optional[str]
    archive_start: Optional[str]
    archive_end: Optional[str]
    archive_days: Optional[float]
    channel_count: int
    channels_ok: int
    channels_warn: int
    channels_error: int
    channels_unknown: int
    last_polled_at: Optional[datetime]
    local_time: Optional[str] = None
    utc_time: Optional[str] = None
    sync_type: Optional[str] = None
    storage_used_mb: Optional[float] = None
    storage_total_mb: Optional[float] = None
    disks_json: Optional[str] = None


@dataclass
class HistoryRow:
    id: int
    entity_type: str
    entity_id: str
    status: str
    reason: Optional[str]
    recorded_at: datetime


class StateStore:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or Path(os.environ.get("STATE_DB_PATH", DEFAULT_DB_PATH))

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recorder_id TEXT NOT NULL,
                    channel_no INTEGER NOT NULL,
                    name TEXT,
                    camera_ip TEXT,
                    camera_model TEXT,
                    source_state TEXT,
                    health_status TEXT NOT NULL DEFAULT 'unknown',
                    health_reason TEXT,
                    video_loss INTEGER,
                    last_polled_at TEXT,
                    UNIQUE(recorder_id, channel_no)
                );

                CREATE TABLE IF NOT EXISTS recorder_metrics (
                    recorder_id TEXT PRIMARY KEY,
                    model TEXT,
                    firmware_version TEXT,
                    device_online INTEGER NOT NULL DEFAULT 0,
                    health_status TEXT NOT NULL DEFAULT 'unknown',
                    health_reason TEXT,
                    ntp_status TEXT,
                    time_skew_seconds REAL,
                    storage_used_percent REAL,
                    storage_status TEXT,
                    archive_start TEXT,
                    archive_end TEXT,
                    archive_days REAL,
                    channel_count INTEGER NOT NULL DEFAULT 0,
                    channels_ok INTEGER NOT NULL DEFAULT 0,
                    channels_warn INTEGER NOT NULL DEFAULT 0,
                    channels_error INTEGER NOT NULL DEFAULT 0,
                    channels_unknown INTEGER NOT NULL DEFAULT 0,
                    last_polled_at TEXT
                );

                CREATE TABLE IF NOT EXISTS status_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    reason TEXT,
                    recorded_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_history_entity
                    ON status_history(entity_type, entity_id, recorded_at DESC);
                CREATE INDEX IF NOT EXISTS idx_channels_recorder
                    ON channels(recorder_id);
                """
            )
            self._migrate_schema(conn)

    def _migrate_schema(self, conn: sqlite3.Connection) -> None:
        columns = {
            row[1] for row in conn.execute("PRAGMA table_info(recorder_metrics)").fetchall()
        }
        additions = [
            ("local_time", "TEXT"),
            ("utc_time", "TEXT"),
            ("sync_type", "TEXT"),
            ("storage_used_mb", "REAL"),
            ("storage_total_mb", "REAL"),
            ("disks_json", "TEXT"),
        ]
        for name, col_type in additions:
            if name not in columns:
                conn.execute(
                    f"ALTER TABLE recorder_metrics ADD COLUMN {name} {col_type}"
                )

    def upsert_channel(
        self,
        recorder_id: str,
        channel_no: int,
        *,
        name: Optional[str] = None,
        camera_ip: Optional[str] = None,
        camera_model: Optional[str] = None,
        source_state: Optional[str] = None,
        health_status: str = "unknown",
        health_reason: Optional[str] = None,
        video_loss: Optional[bool] = None,
        last_polled_at: Optional[datetime] = None,
    ) -> None:
        polled = _iso(last_polled_at)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO channels (
                    recorder_id, channel_no, name, camera_ip, camera_model,
                    source_state, health_status, health_reason, video_loss, last_polled_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(recorder_id, channel_no) DO UPDATE SET
                    name=excluded.name,
                    camera_ip=excluded.camera_ip,
                    camera_model=excluded.camera_model,
                    source_state=excluded.source_state,
                    health_status=excluded.health_status,
                    health_reason=excluded.health_reason,
                    video_loss=excluded.video_loss,
                    last_polled_at=excluded.last_polled_at
                """,
                (
                    recorder_id,
                    channel_no,
                    name,
                    camera_ip,
                    camera_model,
                    source_state,
                    health_status,
                    health_reason,
                    _bool_int(video_loss),
                    polled,
                ),
            )

    def remove_channels_not_in(self, recorder_id: str, channel_nos: list[int]) -> None:
        with self._connect() as conn:
            if not channel_nos:
                conn.execute("DELETE FROM channels WHERE recorder_id = ?", (recorder_id,))
                return
            placeholders = ",".join("?" * len(channel_nos))
            conn.execute(
                f"DELETE FROM channels WHERE recorder_id = ? AND channel_no NOT IN ({placeholders})",
                (recorder_id, *channel_nos),
            )

    def list_channels(
        self,
        recorder_id: Optional[str] = None,
        health: Optional[str] = None,
    ) -> list[ChannelRow]:
        sql = "SELECT * FROM channels WHERE 1=1"
        params: list = []
        if recorder_id:
            sql += " AND recorder_id = ?"
            params.append(recorder_id)
        if health:
            sql += " AND health_status = ?"
            params.append(health)
        sql += " ORDER BY recorder_id, channel_no"
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_channel_from_row(r) for r in rows]

    def get_channel(self, recorder_id: str, channel_no: int) -> Optional[ChannelRow]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM channels WHERE recorder_id = ? AND channel_no = ?",
                (recorder_id, channel_no),
            ).fetchone()
        return _channel_from_row(row) if row else None

    def upsert_recorder_metrics(
        self,
        recorder_id: str,
        *,
        model: Optional[str] = None,
        firmware_version: Optional[str] = None,
        device_online: bool = False,
        health_status: str = "unknown",
        health_reason: Optional[str] = None,
        ntp_status: Optional[str] = None,
        time_skew_seconds: Optional[float] = None,
        storage_used_percent: Optional[float] = None,
        storage_status: Optional[str] = None,
        archive_start: Optional[str] = None,
        archive_end: Optional[str] = None,
        archive_days: Optional[float] = None,
        channel_count: int = 0,
        channels_ok: int = 0,
        channels_warn: int = 0,
        channels_error: int = 0,
        channels_unknown: int = 0,
        last_polled_at: Optional[datetime] = None,
        local_time: Optional[str] = None,
        utc_time: Optional[str] = None,
        sync_type: Optional[str] = None,
        storage_used_mb: Optional[float] = None,
        storage_total_mb: Optional[float] = None,
        disks: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        disks_json = json.dumps(disks, ensure_ascii=False) if disks else None
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO recorder_metrics (
                    recorder_id, model, firmware_version, device_online,
                    health_status, health_reason, ntp_status, time_skew_seconds,
                    storage_used_percent, storage_status, archive_start, archive_end,
                    archive_days, channel_count, channels_ok, channels_warn,
                    channels_error, channels_unknown, last_polled_at,
                    local_time, utc_time, sync_type,
                    storage_used_mb, storage_total_mb, disks_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                          ?, ?, ?, ?, ?, ?)
                ON CONFLICT(recorder_id) DO UPDATE SET
                    model=excluded.model,
                    firmware_version=excluded.firmware_version,
                    device_online=excluded.device_online,
                    health_status=excluded.health_status,
                    health_reason=excluded.health_reason,
                    ntp_status=excluded.ntp_status,
                    time_skew_seconds=excluded.time_skew_seconds,
                    storage_used_percent=excluded.storage_used_percent,
                    storage_status=excluded.storage_status,
                    archive_start=excluded.archive_start,
                    archive_end=excluded.archive_end,
                    archive_days=excluded.archive_days,
                    channel_count=excluded.channel_count,
                    channels_ok=excluded.channels_ok,
                    channels_warn=excluded.channels_warn,
                    channels_error=excluded.channels_error,
                    channels_unknown=excluded.channels_unknown,
                    last_polled_at=excluded.last_polled_at,
                    local_time=excluded.local_time,
                    utc_time=excluded.utc_time,
                    sync_type=excluded.sync_type,
                    storage_used_mb=excluded.storage_used_mb,
                    storage_total_mb=excluded.storage_total_mb,
                    disks_json=excluded.disks_json
                """,
                (
                    recorder_id,
                    model,
                    firmware_version,
                    int(device_online),
                    health_status,
                    health_reason,
                    ntp_status,
                    time_skew_seconds,
                    storage_used_percent,
                    storage_status,
                    archive_start,
                    archive_end,
                    archive_days,
                    channel_count,
                    channels_ok,
                    channels_warn,
                    channels_error,
                    channels_unknown,
                    _iso(last_polled_at),
                    local_time,
                    utc_time,
                    sync_type,
                    storage_used_mb,
                    storage_total_mb,
                    disks_json,
                ),
            )

    def get_recorder_metrics(self, recorder_id: str) -> Optional[RecorderMetricsRow]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM recorder_metrics WHERE recorder_id = ?",
                (recorder_id,),
            ).fetchone()
        return _metrics_from_row(row) if row else None

    def list_recorder_metrics(self) -> list[RecorderMetricsRow]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM recorder_metrics ORDER BY recorder_id"
            ).fetchall()
        return [_metrics_from_row(r) for r in rows]

    def record_history(
        self,
        entity_type: str,
        entity_id: str,
        status: str,
        reason: Optional[str] = None,
        recorded_at: Optional[datetime] = None,
    ) -> None:
        ts = recorded_at or datetime.now(timezone.utc)
        with self._connect() as conn:
            last = conn.execute(
                """
                SELECT status FROM status_history
                WHERE entity_type = ? AND entity_id = ?
                ORDER BY recorded_at DESC LIMIT 1
                """,
                (entity_type, entity_id),
            ).fetchone()
            if last and last["status"] == status:
                return
            conn.execute(
                """
                INSERT INTO status_history (entity_type, entity_id, status, reason, recorded_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (entity_type, entity_id, status, reason, _iso(ts)),
            )

    def list_history(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        limit: int = 200,
    ) -> list[HistoryRow]:
        sql = "SELECT * FROM status_history WHERE 1=1"
        params: list = []
        if entity_type:
            sql += " AND entity_type = ?"
            params.append(entity_type)
        if entity_id:
            sql += " AND entity_id = ?"
            params.append(entity_id)
        sql += " ORDER BY recorded_at DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_history_from_row(r) for r in rows]

    def delete_recorder_data(self, recorder_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM channels WHERE recorder_id = ?", (recorder_id,))
            conn.execute(
                "DELETE FROM recorder_metrics WHERE recorder_id = ?", (recorder_id,)
            )
            conn.execute(
                "DELETE FROM status_history WHERE entity_id LIKE ?",
                (f"{recorder_id}%",),
            )


def _iso(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _bool_int(value: Optional[bool]) -> Optional[int]:
    if value is None:
        return None
    return 1 if value else 0


def _channel_from_row(row: sqlite3.Row) -> ChannelRow:
    vl = row["video_loss"]
    return ChannelRow(
        id=row["id"],
        recorder_id=row["recorder_id"],
        channel_no=row["channel_no"],
        name=row["name"],
        camera_ip=row["camera_ip"],
        camera_model=row["camera_model"],
        source_state=row["source_state"],
        health_status=row["health_status"],
        health_reason=row["health_reason"],
        video_loss=None if vl is None else bool(vl),
        last_polled_at=_parse_iso(row["last_polled_at"]),
    )


def _metrics_from_row(row: sqlite3.Row) -> RecorderMetricsRow:
    return RecorderMetricsRow(
        recorder_id=row["recorder_id"],
        model=row["model"],
        firmware_version=row["firmware_version"],
        device_online=bool(row["device_online"]),
        health_status=row["health_status"],
        health_reason=row["health_reason"],
        ntp_status=row["ntp_status"],
        time_skew_seconds=row["time_skew_seconds"],
        storage_used_percent=row["storage_used_percent"],
        storage_status=row["storage_status"],
        archive_start=row["archive_start"],
        archive_end=row["archive_end"],
        archive_days=row["archive_days"],
        channel_count=row["channel_count"],
        channels_ok=row["channels_ok"],
        channels_warn=row["channels_warn"],
        channels_error=row["channels_error"],
        channels_unknown=row["channels_unknown"],
        last_polled_at=_parse_iso(row["last_polled_at"]),
        local_time=row["local_time"] if "local_time" in row.keys() else None,
        utc_time=row["utc_time"] if "utc_time" in row.keys() else None,
        sync_type=row["sync_type"] if "sync_type" in row.keys() else None,
        storage_used_mb=row["storage_used_mb"] if "storage_used_mb" in row.keys() else None,
        storage_total_mb=row["storage_total_mb"] if "storage_total_mb" in row.keys() else None,
        disks_json=row["disks_json"] if "disks_json" in row.keys() else None,
    )


def _history_from_row(row: sqlite3.Row) -> HistoryRow:
    return HistoryRow(
        id=row["id"],
        entity_type=row["entity_type"],
        entity_id=row["entity_id"],
        status=row["status"],
        reason=row["reason"],
        recorded_at=_parse_iso(row["recorded_at"]) or datetime.now(timezone.utc),
    )
