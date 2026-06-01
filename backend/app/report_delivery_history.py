from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

DEFAULT_HISTORY_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "report_delivery_history.json"
)
_HISTORY_LOCKS: dict[str, threading.Lock] = {}
_HISTORY_LOCKS_GUARD = threading.Lock()

DeliveryStatus = Literal["success", "failed"]
DeliveryTrigger = Literal["scheduled", "catchup", "manual"]


@dataclass
class ReportDeliveryRecord:
    sent_at: datetime
    problem_count: int
    recorders_with_errors: int
    category_counts: dict[str, int]
    status: DeliveryStatus
    trigger: DeliveryTrigger = "scheduled"
    error: Optional[str] = None

    def to_json(self) -> dict:
        return {
            "sent_at": self.sent_at.astimezone(timezone.utc).isoformat(),
            "problem_count": self.problem_count,
            "recorders_with_errors": self.recorders_with_errors,
            "category_counts": self.category_counts,
            "status": self.status,
            "trigger": self.trigger,
            "error": self.error,
        }

    @classmethod
    def from_json(cls, data: dict) -> ReportDeliveryRecord:
        sent_raw = data["sent_at"]
        if isinstance(sent_raw, str):
            sent_at = datetime.fromisoformat(sent_raw.replace("Z", "+00:00"))
        else:
            raise ValueError("sent_at must be ISO string")
        if sent_at.tzinfo is None:
            sent_at = sent_at.replace(tzinfo=timezone.utc)
        return cls(
            sent_at=sent_at,
            problem_count=int(data.get("problem_count", 0)),
            recorders_with_errors=int(data.get("recorders_with_errors", 0)),
            category_counts=dict(data.get("category_counts") or {}),
            status=data.get("status", "failed"),
            trigger=data.get("trigger", "scheduled"),
            error=data.get("error"),
        )


@dataclass
class ReportDeliveryHistory:
    entries: list[ReportDeliveryRecord] = field(default_factory=list)

    def last_success(self) -> Optional[ReportDeliveryRecord]:
        for entry in reversed(self.entries):
            if entry.status == "success":
                return entry
        return None

    def last_entry(self) -> Optional[ReportDeliveryRecord]:
        if not self.entries:
            return None
        return self.entries[-1]

    def successful_entries(self) -> list[ReportDeliveryRecord]:
        return [e for e in self.entries if e.status == "success"]


class ReportDeliveryHistoryStore:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or Path(
            os.environ.get("REPORT_DELIVERY_HISTORY_PATH", DEFAULT_HISTORY_PATH)
        )

    def _file_lock(self) -> threading.Lock:
        key = str(self.path.resolve())
        with _HISTORY_LOCKS_GUARD:
            lock = _HISTORY_LOCKS.get(key)
            if lock is None:
                lock = threading.Lock()
                _HISTORY_LOCKS[key] = lock
            return lock

    def load(self) -> ReportDeliveryHistory:
        with self._file_lock():
            return self._load_unlocked()

    def _load_unlocked(self) -> ReportDeliveryHistory:
        if not self.path.exists():
            return ReportDeliveryHistory()
        with open(self.path, encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, list):
            return ReportDeliveryHistory()
        entries: list[ReportDeliveryRecord] = []
        for item in raw:
            if isinstance(item, dict):
                try:
                    entries.append(ReportDeliveryRecord.from_json(item))
                except (KeyError, ValueError, TypeError):
                    continue
        return ReportDeliveryHistory(entries=entries)

    def append(self, record: ReportDeliveryRecord, *, max_entries: int) -> None:
        with self._file_lock():
            history = self._load_unlocked()
            history.entries.append(record)
            if len(history.entries) > max_entries:
                history.entries = history.entries[-max_entries:]
            self._save_unlocked(history)

    def _save_unlocked(self, history: ReportDeliveryHistory) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [e.to_json() for e in history.entries]
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, self.path)
