"""HTTP CGI Dahua (magicBox) — идентификация бренда и метаданные камеры."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode

import httpx

_FIRMWARE_BUILD_RE = re.compile(
    r"build\s*:\s*(\d{4})-(\d{2})-(\d{2})",
    re.IGNORECASE,
)
_DAHUA_MODEL_PREFIXES = ("IPC-", "DH-", "HDW-", "HFW-", "SD", "DHI-")


def parse_key_value_body(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in (text or "").splitlines():
        line = line.strip()
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
    return result


def looks_like_dahua_model(value: Optional[str]) -> bool:
    if not value:
        return False
    upper = value.strip().upper()
    if upper.startswith(_DAHUA_MODEL_PREFIXES):
        return True
    return "IPC" in upper and "-" in upper


def is_dahua_vendor(vendor: Optional[str]) -> bool:
    if not vendor:
        return False
    return "dahua" in vendor.strip().lower()


def parse_firmware_build_date(version_text: Optional[str]) -> Optional[str]:
    """YYYY-MM из строки version=…,build:YYYY-MM-DD."""
    if not version_text:
        return None
    m = _FIRMWARE_BUILD_RE.search(version_text)
    if not m:
        return None
    year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if month < 1 or month > 12 or day < 1 or day > 31:
        return None
    return f"{year:04d}-{month:02d}"


@dataclass
class DahuaProbeResult:
    ok: bool
    is_dahua: bool = False
    vendor: Optional[str] = None
    device_type: Optional[str] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    manufacture_date: Optional[str] = None
    error: Optional[str] = None


def _magicbox_url(host: str, port: int, action: str) -> str:
    query = urlencode({"action": action})
    return f"http://{host}:{port}/cgi-bin/magicBox.cgi?{query}"


async def probe_dahua(
    host: str,
    port: int,
    username: str,
    password: str,
    *,
    timeout: float = 8.0,
) -> DahuaProbeResult:
    if not username or not password:
        return DahuaProbeResult(ok=False, error="Не заданы учётные данные")

    auth = httpx.DigestAuth(username, password)
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            verify=False,
            follow_redirects=True,
        ) as client:
            vendor_resp = await client.get(
                _magicbox_url(host, port, "getVendor"),
                auth=auth,
            )
            if vendor_resp.status_code == 401:
                return DahuaProbeResult(ok=False, error="Ошибка аутентификации (401)")
            if vendor_resp.status_code >= 400:
                return DahuaProbeResult(
                    ok=False,
                    error=f"HTTP {vendor_resp.status_code}",
                )

            vendor_fields = parse_key_value_body(vendor_resp.text)
            vendor = vendor_fields.get("vendor")
            is_dahua = is_dahua_vendor(vendor)

            sys_resp = await client.get(
                _magicbox_url(host, port, "getSystemInfo"),
                auth=auth,
            )
            sys_fields = (
                parse_key_value_body(sys_resp.text)
                if sys_resp.status_code < 400
                else {}
            )
            device_type = (
                sys_fields.get("deviceType")
                or sys_fields.get("updateSerial")
            )
            serial = sys_fields.get("serialNumber")

            if not is_dahua and looks_like_dahua_model(device_type):
                is_dahua = True

            if not is_dahua:
                return DahuaProbeResult(
                    ok=True,
                    is_dahua=False,
                    vendor=vendor,
                    device_type=device_type,
                    serial_number=serial,
                )

            fw_resp = await client.get(
                _magicbox_url(host, port, "getSoftwareVersion"),
                auth=auth,
            )
            fw_text = fw_resp.text if fw_resp.status_code < 400 else ""
            fw_fields = parse_key_value_body(fw_text)
            firmware = fw_fields.get("version") or fw_text.strip() or None
            mfg_date = parse_firmware_build_date(firmware)

            if not serial:
                sn_resp = await client.get(
                    _magicbox_url(host, port, "getSerialNo"),
                    auth=auth,
                )
                if sn_resp.status_code < 400:
                    serial = parse_key_value_body(sn_resp.text).get("serialNumber")

            return DahuaProbeResult(
                ok=True,
                is_dahua=True,
                vendor=vendor or "Dahua",
                device_type=device_type,
                serial_number=serial,
                firmware_version=firmware,
                manufacture_date=mfg_date,
            )
    except httpx.TimeoutException:
        return DahuaProbeResult(ok=False, error="Таймаут")
    except httpx.ConnectError:
        return DahuaProbeResult(ok=False, error="Нет соединения")
    except httpx.RequestError as exc:
        return DahuaProbeResult(ok=False, error=f"Ошибка сети: {exc}")
