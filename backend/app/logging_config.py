from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

LOG_DIR: Path = PROJECT_ROOT / "logs"
LOG_FILE: Path = LOG_DIR / "wisenet.log"

_CONFIGURED = False


class JsonLineFormatter(logging.Formatter):
    """Одна строка JSON на событие — удобно копировать в чат для диагностики."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "event"):
            payload["event"] = record.event
        for key, value in record.__dict__.items():
            if key.startswith("_") or key in {
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "exc_info",
                "exc_text",
                "thread",
                "threadName",
                "taskName",
                "event",
            }:
                continue
            if key.startswith("extra_"):
                payload[key[6:]] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def _can_write_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def resolve_log_paths() -> tuple[Path, Path]:
    """Выбирает каталог логов: env → корень проекта → backend → текущая папка."""
    global LOG_DIR, LOG_FILE

    env_dir = os.environ.get("WISENET_LOG_DIR", "").strip()
    if env_dir:
        candidate = Path(env_dir).expanduser().resolve()
        if _can_write_dir(candidate):
            LOG_DIR = candidate
            LOG_FILE = LOG_DIR / "wisenet.log"
            return LOG_DIR, LOG_FILE

    candidates = [
        PROJECT_ROOT / "logs",
        BACKEND_DIR / "logs",
        Path.cwd() / "logs",
    ]
    for candidate in candidates:
        if _can_write_dir(candidate):
            LOG_DIR = candidate.resolve()
            LOG_FILE = LOG_DIR / "wisenet.log"
            return LOG_DIR, LOG_FILE

    raise RuntimeError(
        "Не удалось создать каталог для логов. "
        "Задайте переменную WISENET_LOG_DIR с путём к доступной для записи папке."
    )


def get_log_file_path() -> Path:
    setup_logging()
    return LOG_FILE


def _print_startup_banner(log_file: Path, log_dir: Path) -> None:
    # Явный вывод в консоль — виден даже при старом uvicorn без наших log-строк.
    msg = (
        f"Wisenet: логи -> {log_file}\n"
        f"         (каталог: {log_dir}; корень проекта: {PROJECT_ROOT})"
    )
    print(msg, file=sys.stderr, flush=True)


def setup_logging() -> logging.Logger:
    global _CONFIGURED
    root_logger = logging.getLogger("wisenet")
    if _CONFIGURED:
        return root_logger

    log_dir, log_file = resolve_log_paths()

    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(JsonLineFormatter())

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    )

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.propagate = False

    _CONFIGURED = True
    _print_startup_banner(log_file, log_dir)
    root_logger.info(
        "logging started",
        extra={
            "event": "startup",
            "extra_log_file": str(log_file),
            "extra_log_dir": str(log_dir),
            "extra_project_root": str(PROJECT_ROOT),
        },
    )
    return root_logger


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(f"wisenet.{name}")
