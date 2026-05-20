from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlencode

import httpx

from .logging_config import get_logger
from .models import CheckStatus, Credentials, Recorder

logger = get_logger("sunapi")


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


def _log_check_result(
    recorder: Recorder,
    outcome: SunapiCheckOutcome,
    *,
    duration_ms: int,
    url: str | None = None,
    http_status: int | None = None,
) -> None:
    extra: dict = {
        "event": "sunapi_check_done",
        "extra_recorder_id": recorder.id,
        "extra_host": recorder.host,
        "extra_port": recorder.port,
        "extra_use_https": recorder.use_https,
        "extra_enabled": recorder.enabled,
        "extra_status": outcome.status.value,
        "extra_duration_ms": duration_ms,
        "extra_error": outcome.error,
    }
    if url:
        extra["extra_url"] = url
    if http_status is not None:
        extra["extra_http_status"] = http_status
    if outcome.device and outcome.device.model:
        extra["extra_model"] = outcome.device.model
    level = logging.INFO if outcome.status == CheckStatus.ONLINE else logging.WARNING
    logger.log(level, "sunapi check finished", extra=extra)


async def check_recorder(
    recorder: Recorder,
    credentials: Credentials,
    timeout: float = 15.0,
) -> SunapiCheckOutcome:
    checked_at = datetime.now(timezone.utc)
    start = time.perf_counter()

    def finish(outcome: SunapiCheckOutcome, **kwargs) -> SunapiCheckOutcome:
        duration_ms = round((time.perf_counter() - start) * 1000)
        _log_check_result(recorder, outcome, duration_ms=duration_ms, **kwargs)
        return outcome

    if not recorder.enabled:
        return finish(
            SunapiCheckOutcome(
                status=CheckStatus.DISABLED,
                checked_at=checked_at,
                error=None,
            )
        )

    if not credentials.username or not credentials.password:
        return finish(
            SunapiCheckOutcome(
                status=CheckStatus.OFFLINE,
                checked_at=checked_at,
                error="Не заданы учётные данные API. Укажите логин и пароль в настройках.",
            )
        )

    url = build_deviceinfo_url(recorder)
    logger.info(
        "sunapi request",
        extra={
            "event": "sunapi_request",
            "extra_recorder_id": recorder.id,
            "extra_url": url,
            "extra_timeout_s": timeout,
        },
    )

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
        return finish(
            SunapiCheckOutcome(
                status=CheckStatus.OFFLINE,
                checked_at=checked_at,
                error="Превышено время ожидания ответа устройства",
            ),
            url=url,
        )
    except httpx.ConnectError:
        return finish(
            SunapiCheckOutcome(
                status=CheckStatus.OFFLINE,
                checked_at=checked_at,
                error="Не удалось установить соединение с устройством",
            ),
            url=url,
        )
    except httpx.RequestError as exc:
        return finish(
            SunapiCheckOutcome(
                status=CheckStatus.OFFLINE,
                checked_at=checked_at,
                error=f"Ошибка сети: {exc}",
            ),
            url=url,
        )

    if response.status_code == 401:
        return finish(
            SunapiCheckOutcome(
                status=CheckStatus.OFFLINE,
                checked_at=checked_at,
                error="Ошибка аутентификации (401). Проверьте логин и пароль.",
            ),
            url=url,
            http_status=response.status_code,
        )

    if response.status_code >= 400:
        return finish(
            SunapiCheckOutcome(
                status=CheckStatus.OFFLINE,
                checked_at=checked_at,
                error=f"HTTP {response.status_code}: устройство вернуло ошибку",
            ),
            url=url,
            http_status=response.status_code,
        )

    body = response.text
    if not body.strip():
        return finish(
            SunapiCheckOutcome(
                status=CheckStatus.OFFLINE,
                checked_at=checked_at,
                error="Пустой ответ от SUNAPI",
            ),
            url=url,
            http_status=response.status_code,
        )

    if re.search(r"(?i)(error|fail|denied)", body) and "Model=" not in body:
        return finish(
            SunapiCheckOutcome(
                status=CheckStatus.OFFLINE,
                checked_at=checked_at,
                error=body.strip()[:500],
            ),
            url=url,
            http_status=response.status_code,
        )

    device = parse_deviceinfo_response(body)
    if not device.model and not device.device_type:
        return finish(
            SunapiCheckOutcome(
                status=CheckStatus.OFFLINE,
                checked_at=checked_at,
                error="Ответ получен, но не распознан как deviceinfo",
            ),
            url=url,
            http_status=response.status_code,
        )

    return finish(
        SunapiCheckOutcome(
            status=CheckStatus.ONLINE,
            checked_at=checked_at,
            device=device,
        ),
        url=url,
        http_status=response.status_code,
    )
