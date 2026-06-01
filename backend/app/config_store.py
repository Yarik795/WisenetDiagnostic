from __future__ import annotations

import json
import os
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from .exclusions import migrate_config_raw, prune_exclusions
from .models import AppConfig, CheckStatus, Credentials, ExclusionSettings, Recorder, RecorderCreate, RecorderUpdate

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.json"
_CONFIG_LOCKS: dict[str, threading.Lock] = {}
_CONFIG_LOCKS_GUARD = threading.Lock()
_REPLACE_RETRIES = 8
_REPLACE_RETRY_DELAY_S = 0.05


@dataclass(frozen=True)
class RecorderStatusUpdate:
    recorder_id: str
    status: CheckStatus
    checked_at: datetime
    error: Optional[str] = None


class ConfigStore:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or Path(os.environ.get("CONFIG_PATH", DEFAULT_CONFIG_PATH))

    def _file_lock(self) -> threading.Lock:
        key = str(self.path.resolve())
        with _CONFIG_LOCKS_GUARD:
            lock = _CONFIG_LOCKS.get(key)
            if lock is None:
                lock = threading.Lock()
                _CONFIG_LOCKS[key] = lock
            return lock

    def load(self) -> AppConfig:
        with self._file_lock():
            return self._load_unlocked()

    def _load_unlocked(self) -> AppConfig:
        if not self.path.exists():
            return AppConfig()
        with open(self.path, encoding="utf-8") as f:
            data = json.load(f)
        data = migrate_config_raw(data)
        return AppConfig.model_validate(data)

    def save(self, config: AppConfig) -> None:
        with self._file_lock():
            self._save_unlocked(prune_exclusions(config))

    def _save_unlocked(self, config: AppConfig) -> None:
        config = prune_exclusions(config)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = config.model_dump(mode="json")
        fd, tmp_path = tempfile.mkstemp(
            dir=self.path.parent,
            prefix=".config.",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
                f.write("\n")
            self._replace_with_retry(tmp_path, self.path)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    @staticmethod
    def _replace_with_retry(src: str, dst: Path) -> None:
        last_error: Optional[BaseException] = None
        for attempt in range(_REPLACE_RETRIES):
            try:
                os.replace(src, dst)
                return
            except PermissionError as exc:
                last_error = exc
                time.sleep(_REPLACE_RETRY_DELAY_S * (attempt + 1))
        if last_error is not None:
            raise last_error

    def list_recorders(self) -> list[Recorder]:
        return self.load().recorders

    def get_recorder(self, recorder_id: str) -> Optional[Recorder]:
        for r in self.load().recorders:
            if r.id == recorder_id:
                return r
        return None

    def create_recorder(self, data: RecorderCreate) -> Recorder:
        config = self.load()
        recorder = Recorder(id=_new_id(), **data.model_dump())
        config.recorders.append(recorder)
        self.save(config)
        return recorder

    def update_recorder(self, recorder_id: str, data: RecorderUpdate) -> Optional[Recorder]:
        config = self.load()
        for i, r in enumerate(config.recorders):
            if r.id == recorder_id:
                updated = Recorder(
                    id=r.id,
                    last_status=r.last_status,
                    last_check_at=r.last_check_at,
                    last_error=r.last_error,
                    **data.model_dump(),
                )
                config.recorders[i] = updated
                self.save(config)
                return updated
        return None

    def delete_recorder(self, recorder_id: str) -> bool:
        config = self.load()
        before = len(config.recorders)
        config.recorders = [r for r in config.recorders if r.id != recorder_id]
        if len(config.recorders) == before:
            return False
        ids = [rid for rid in config.exclusions.recorder_ids if rid != recorder_id]
        config.exclusions = config.exclusions.model_copy(update={"recorder_ids": ids})
        self.save(config)
        return True

    def list_exclusion_ids(self) -> list[str]:
        return list(self.load().exclusions.recorder_ids)

    def add_exclusion(self, recorder_id: str) -> bool:
        if self.get_recorder(recorder_id) is None:
            return False
        with self._file_lock():
            config = self._load_unlocked()
            ids = list(config.exclusions.recorder_ids)
            if recorder_id in ids:
                return True
            ids.append(recorder_id)
            config.exclusions = config.exclusions.model_copy(
                update={"recorder_ids": ids}
            )
            self._save_unlocked(config)
        return True

    def remove_exclusion(self, recorder_id: str) -> bool:
        with self._file_lock():
            config = self._load_unlocked()
            ids = list(config.exclusions.recorder_ids)
            if recorder_id not in ids:
                return False
            ids = [rid for rid in ids if rid != recorder_id]
            config.exclusions = config.exclusions.model_copy(
                update={"recorder_ids": ids}
            )
            self._save_unlocked(config)
        return True

    def set_exclusions(self, recorder_ids: list[str]) -> ExclusionSettings:
        valid = {r.id for r in self.load().recorders}
        unique: list[str] = []
        seen: set[str] = set()
        for rid in recorder_ids:
            if rid in valid and rid not in seen:
                unique.append(rid)
                seen.add(rid)
        with self._file_lock():
            config = self._load_unlocked()
            config.exclusions = ExclusionSettings(recorder_ids=unique)
            self._save_unlocked(config)
            return config.exclusions

    def update_recorder_status(
        self,
        recorder_id: str,
        status: CheckStatus,
        checked_at,
        error: Optional[str] = None,
    ) -> Optional[Recorder]:
        self.update_recorder_statuses(
            [
                RecorderStatusUpdate(
                    recorder_id=recorder_id,
                    status=status,
                    checked_at=checked_at,
                    error=error,
                )
            ]
        )
        return self.get_recorder(recorder_id)

    def update_recorder_statuses(
        self, updates: list[RecorderStatusUpdate]
    ) -> None:
        if not updates:
            return
        by_id = {u.recorder_id: u for u in updates}
        with self._file_lock():
            config = self._load_unlocked()
            changed = False
            for i, r in enumerate(config.recorders):
                update = by_id.get(r.id)
                if update is None:
                    continue
                config.recorders[i] = r.model_copy(
                    update={
                        "last_status": update.status,
                        "last_check_at": update.checked_at,
                        "last_error": update.error,
                    }
                )
                changed = True
            if changed:
                self._save_unlocked(config)

    def get_credentials(self) -> Credentials:
        return self.load().credentials

    def update_credentials(self, username: str, password: str) -> Credentials:
        config = self.load()
        config.credentials = Credentials(username=username, password=password)
        self.save(config)
        return config.credentials


def _new_id() -> str:
    return f"nvr-{uuid.uuid4().hex[:8]}"
