from __future__ import annotations

from datetime import datetime

from ..models import Recorder


def display_recorder_name(recorder: Recorder) -> str:
    if recorder.name and recorder.name.strip():
        return recorder.name.strip()
    return recorder.host


def format_host_port(host: str, port: int, use_https: bool) -> str:
    scheme = "https" if use_https else "http"
    default_port = 443 if use_https else 80
    if port == default_port:
        return f"{scheme}://{host}"
    return f"{scheme}://{host}:{port}"


def format_time(value: datetime | None) -> str:
    if value is None:
        return "—"
    return value.strftime("%H:%M:%S")


def format_datetime(value: datetime | None) -> str:
    if value is None:
        return "—"
    return value.strftime("%d.%m.%Y %H:%M:%S")
