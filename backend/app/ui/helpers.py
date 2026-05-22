from __future__ import annotations

from datetime import datetime
from urllib.parse import quote

from ..models import Credentials, Recorder


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


def device_web_interface_url(
    recorder: Recorder,
    *,
    credentials: Credentials | None = None,
    device_auth: str = "",
) -> str:
    """URL web-интерфейса NVR. device_auth=userinfo — экспериментальная автоавторизация."""
    base = format_host_port(recorder.host, recorder.port, recorder.use_https)
    if device_auth != "userinfo" or credentials is None:
        return base
    if not credentials.username.strip() or not credentials.password:
        return base
    scheme = "https" if recorder.use_https else "http"
    default_port = 443 if recorder.use_https else 80
    user = quote(credentials.username, safe="")
    password = quote(credentials.password, safe="")
    host_part = (
        recorder.host
        if recorder.port == default_port
        else f"{recorder.host}:{recorder.port}"
    )
    return f"{scheme}://{user}:{password}@{host_part}"


def device_web_link_title(recorder: Recorder) -> str:
    return f"Открыть web-интерфейс NVR: {display_recorder_name(recorder)}"


def format_time(value: datetime | None) -> str:
    if value is None:
        return "—"
    return value.strftime("%H:%M:%S")


def format_datetime(value: datetime | None) -> str:
    if value is None:
        return "—"
    return value.strftime("%d.%m.%Y %H:%M:%S")
