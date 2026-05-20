from __future__ import annotations

import json
import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from .models import AppConfig, CheckStatus, Credentials, Recorder, RecorderCreate, RecorderUpdate

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.json"


class ConfigStore:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or Path(os.environ.get("CONFIG_PATH", DEFAULT_CONFIG_PATH))

    def load(self) -> AppConfig:
        if not self.path.exists():
            return AppConfig()
        with open(self.path, encoding="utf-8") as f:
            data = json.load(f)
        return AppConfig.model_validate(data)

    def save(self, config: AppConfig) -> None:
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
            os.replace(tmp_path, self.path)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

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
        self.save(config)
        return True

    def update_recorder_status(
        self,
        recorder_id: str,
        status: CheckStatus,
        checked_at,
        error: Optional[str] = None,
    ) -> Optional[Recorder]:
        config = self.load()
        for i, r in enumerate(config.recorders):
            if r.id == recorder_id:
                updated = r.model_copy(
                    update={
                        "last_status": status,
                        "last_check_at": checked_at,
                        "last_error": error,
                    }
                )
                config.recorders[i] = updated
                self.save(config)
                return updated
        return None

    def get_credentials(self) -> Credentials:
        return self.load().credentials

    def update_credentials(self, username: str, password: str) -> Credentials:
        config = self.load()
        config.credentials = Credentials(username=username, password=password)
        self.save(config)
        return config.credentials


def _new_id() -> str:
    return f"nvr-{uuid.uuid4().hex[:8]}"
