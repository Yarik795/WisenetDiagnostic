"""Прямой опрос камер Hanwha/Samsung по SUNAPI deviceinfo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode

import httpx

from .serial_manufacture_date import decode_samsung_manufacture_date
from .sunapi import parse_deviceinfo_response


@dataclass
class HanwhaCameraProbeResult:
    ok: bool
    is_hanwha: bool = False
    model: Optional[str] = None
    serial_number: Optional[str] = None
    manufacture_date: Optional[str] = None
    error: Optional[str] = None


def _deviceinfo_url(host: str, port: int) -> str:
    query = urlencode({"msubmenu": "deviceinfo", "action": "view"})
    return f"http://{host}:{port}/stw-cgi/system.cgi?{query}"


def _is_hanwha_device(model: Optional[str], device_type: Optional[str]) -> bool:
    combined = f"{model or ''} {device_type or ''}".upper()
    if not combined.strip():
        return False
    markers = ("QND", "XNO", "PNM", "PNO", "SNV", "SND", "QNO", "Hanwha", "Samsung")
    return any(m.upper() in combined for m in markers)


async def probe_hanwha_camera(
    host: str,
    port: int,
    username: str,
    password: str,
    *,
    timeout: float = 8.0,
) -> HanwhaCameraProbeResult:
    if not username or not password:
        return HanwhaCameraProbeResult(ok=False, error="Не заданы учётные данные")

    url = _deviceinfo_url(host, port)
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            verify=False,
            follow_redirects=True,
        ) as client:
            response = await client.get(
                url,
                auth=httpx.DigestAuth(username, password),
            )
            if response.status_code == 401:
                return HanwhaCameraProbeResult(
                    ok=False,
                    error="Ошибка аутентификации (401)",
                )
            if response.status_code >= 400:
                return HanwhaCameraProbeResult(
                    ok=False,
                    error=f"HTTP {response.status_code}",
                )
            device = parse_deviceinfo_response(response.text)
            is_hanwha = _is_hanwha_device(device.model, device.device_type)
            if not is_hanwha:
                return HanwhaCameraProbeResult(
                    ok=True,
                    is_hanwha=False,
                    model=device.model,
                    serial_number=device.serial_number,
                )
            mfg: Optional[str] = None
            if device.serial_number:
                decoded = decode_samsung_manufacture_date(device.serial_number)
                if decoded:
                    mfg = decoded.strftime("%Y-%m")
            return HanwhaCameraProbeResult(
                ok=True,
                is_hanwha=True,
                model=device.model,
                serial_number=device.serial_number,
                manufacture_date=mfg,
            )
    except httpx.TimeoutException:
        return HanwhaCameraProbeResult(ok=False, error="Таймаут")
    except httpx.ConnectError:
        return HanwhaCameraProbeResult(ok=False, error="Нет соединения")
    except httpx.RequestError as exc:
        return HanwhaCameraProbeResult(ok=False, error=f"Ошибка сети: {exc}")
