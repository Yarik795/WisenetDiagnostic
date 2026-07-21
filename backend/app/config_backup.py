"""Выгрузка конфигурации устройств Hanwha через SUNAPI configbackup."""

from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass
from typing import Literal
from urllib.parse import quote, urlencode

import httpx

from .models import Credentials

CONFIG_BACKUP_TIMEOUT = 90.0
_SUNAPI_ERROR_MARKERS = (b"Error Code:", b"NG")


class ConfigBackupError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


@dataclass(frozen=True)
class ConfigBackupTarget:
    object_name: str
    kind: Literal["nvr", "spd"]
    host: str
    port: int = 80
    use_https: bool = False


def build_config_backup_url(host: str, port: int, use_https: bool) -> str:
    scheme = "https" if use_https else "http"
    base = f"{scheme}://{host}:{port}/stw-cgi/system.cgi"
    query = urlencode({"msubmenu": "configbackup", "action": "control"})
    return f"{base}?{query}"


def sanitize_filename_part(value: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\s]+', "_", (value or "").strip())
    cleaned = cleaned.strip("._")
    return cleaned or "unknown"


def config_backup_filename(object_name: str, kind: str, host: str) -> str:
    obj = sanitize_filename_part(object_name)
    host_part = sanitize_filename_part(host.replace(".", "-"))
    return f"{obj}_{kind}_{host_part}.bin"


def object_zip_filename(object_name: str) -> str:
    return f"{sanitize_filename_part(object_name)}_configs.zip"


def attachment_content_disposition(filename: str) -> str:
    ascii_name = re.sub(r"[^\w.\-]+", "_", filename, flags=re.ASCII).strip("._")
    if not ascii_name:
        ascii_name = "download.bin" if filename.endswith(".bin") else "download.zip"
    encoded = quote(filename, safe="")
    return f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{encoded}"


def _looks_like_sunapi_error(content: bytes) -> bool:
    if not content:
        return True
    head = content[:500]
    if head.startswith(b"Error"):
        return True
    return any(marker in head for marker in _SUNAPI_ERROR_MARKERS)


async def fetch_config_backup(
    host: str,
    port: int,
    use_https: bool,
    credentials: Credentials,
    *,
    timeout: float = CONFIG_BACKUP_TIMEOUT,
) -> bytes:
    if not credentials.username or not credentials.password:
        raise ConfigBackupError("Не заданы учётные данные в настройках")

    url = build_config_backup_url(host, port, use_https)
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            verify=False,
            follow_redirects=True,
        ) as client:
            response = await client.get(
                url,
                auth=httpx.DigestAuth(credentials.username, credentials.password),
            )
    except httpx.TimeoutException as exc:
        raise ConfigBackupError(f"Таймаут при обращении к {host}") from exc
    except httpx.RequestError as exc:
        raise ConfigBackupError(f"Устройство {host} недоступно: {exc}") from exc

    if response.status_code == 401:
        raise ConfigBackupError(
            f"Ошибка авторизации на {host}",
            status_code=401,
        )
    if response.status_code != 200:
        raise ConfigBackupError(
            f"Устройство {host} вернуло код {response.status_code}",
            status_code=response.status_code,
        )

    content = response.content
    if _looks_like_sunapi_error(content):
        text = content[:500].decode("utf-8", errors="replace")
        raise ConfigBackupError(f"SUNAPI ошибка на {host}: {text[:200]}")

    return content


async def fetch_config_backup_for_target(
    target: ConfigBackupTarget,
    credentials: Credentials,
) -> bytes:
    return await fetch_config_backup(
        target.host,
        target.port,
        target.use_https,
        credentials,
    )


async def build_object_config_zip(
    targets: list[ConfigBackupTarget],
    credentials: Credentials,
) -> tuple[bytes, list[str]]:
    buffer = io.BytesIO()
    errors: list[str] = []

    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for target in targets:
            filename = config_backup_filename(target.object_name, target.kind, target.host)
            try:
                content = await fetch_config_backup_for_target(target, credentials)
            except ConfigBackupError as exc:
                errors.append(f"{filename}: {exc.message}")
                continue
            archive.writestr(filename, content)

        if errors:
            archive.writestr("errors.txt", "\n".join(errors) + "\n")

    if not targets:
        raise ConfigBackupError("Нет устройств для выгрузки")

    return buffer.getvalue(), errors
