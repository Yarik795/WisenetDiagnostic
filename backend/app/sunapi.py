from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlencode

import httpx

from .models import CheckStatus, Credentials, Recorder


@dataclass
class DeviceInfo:
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    device_type: Optional[str] = None


@dataclass
class SunapiCheckOutcome:
    status: CheckStatus
    checked_at: datetime
    error: Optional[str] = None
    device: Optional[DeviceInfo] = None


def build_deviceinfo_url(recorder: Recorder) -> str:
    scheme = "https" if recorder.use_https else "http"
    base = f"{scheme}://{recorder.host}:{recorder.port}/stw-cgi/system.cgi"
    query = urlencode({"msubmenu": "deviceinfo", "action": "view"})
    return f"{base}?{query}"


def parse_deviceinfo_response(text: str) -> DeviceInfo:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if "=" in line:
            key, _, value = line.partition("=")
            fields[key.strip()] = value.strip()
    return DeviceInfo(
        model=fields.get("Model"),
        firmware_version=fields.get("FirmwareVersion"),
        device_type=fields.get("DeviceType"),
    )


async def check_recorder(
    recorder: Recorder,
    credentials: Credentials,
    timeout: float = 15.0,
) -> SunapiCheckOutcome:
    checked_at = datetime.now(timezone.utc)

    if not recorder.enabled:
        return SunapiCheckOutcome(
            status=CheckStatus.DISABLED,
            checked_at=checked_at,
            error=None,
        )

    if not credentials.username or not credentials.password:
        return SunapiCheckOutcome(
            status=CheckStatus.OFFLINE,
            checked_at=checked_at,
            error="Не заданы учётные данные API. Укажите логин и пароль в настройках.",
        )

    url = build_deviceinfo_url(recorder)

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
    except httpx.TimeoutException:
        return SunapiCheckOutcome(
            status=CheckStatus.OFFLINE,
            checked_at=checked_at,
            error="Превышено время ожидания ответа устройства",
        )
    except httpx.ConnectError:
        return SunapiCheckOutcome(
            status=CheckStatus.OFFLINE,
            checked_at=checked_at,
            error="Не удалось установить соединение с устройством",
        )
    except httpx.RequestError as exc:
        return SunapiCheckOutcome(
            status=CheckStatus.OFFLINE,
            checked_at=checked_at,
            error=f"Ошибка сети: {exc}",
        )

    if response.status_code == 401:
        return SunapiCheckOutcome(
            status=CheckStatus.OFFLINE,
            checked_at=checked_at,
            error="Ошибка аутентификации (401). Проверьте логин и пароль.",
        )

    if response.status_code >= 400:
        return SunapiCheckOutcome(
            status=CheckStatus.OFFLINE,
            checked_at=checked_at,
            error=f"HTTP {response.status_code}: устройство вернуло ошибку",
        )

    body = response.text
    if not body.strip():
        return SunapiCheckOutcome(
            status=CheckStatus.OFFLINE,
            checked_at=checked_at,
            error="Пустой ответ от SUNAPI",
        )

    if re.search(r"(?i)(error|fail|denied)", body) and "Model=" not in body:
        return SunapiCheckOutcome(
            status=CheckStatus.OFFLINE,
            checked_at=checked_at,
            error=body.strip()[:500],
        )

    device = parse_deviceinfo_response(body)
    if not device.model and not device.device_type:
        return SunapiCheckOutcome(
            status=CheckStatus.OFFLINE,
            checked_at=checked_at,
            error="Ответ получен, но не распознан как deviceinfo",
        )

    return SunapiCheckOutcome(
        status=CheckStatus.ONLINE,
        checked_at=checked_at,
        device=device,
    )
