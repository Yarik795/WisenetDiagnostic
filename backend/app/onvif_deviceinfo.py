"""Минимальный ONVIF GetDeviceInformation для идентификации камеры."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from xml.etree import ElementTree as ET

import httpx


def _local_tag(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def _extract_device_info_xml(xml_text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return result
    for elem in root.iter():
        tag = _local_tag(elem.tag)
        if tag in (
            "Manufacturer",
            "Model",
            "FirmwareVersion",
            "SerialNumber",
            "HardwareId",
        ) and elem.text:
            result[tag] = elem.text.strip()
    return result


def _normalize_brand(manufacturer: Optional[str]) -> Optional[str]:
    if not manufacturer:
        return None
    lower = manufacturer.strip().lower()
    if "dahua" in lower:
        return "dahua"
    if "hanwha" in lower or "samsung" in lower or "wisenet" in lower:
        return "hanwha"
    return "other"


@dataclass
class OnvifDeviceInfo:
    ok: bool
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    serial_number: Optional[str] = None
    brand: Optional[str] = None
    error: Optional[str] = None


_GET_DEVICE_INFO_BODY = """<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
            xmlns:tds="http://www.onvif.org/ver10/device/wsdl">
  <s:Body>
    <tds:GetDeviceInformation/>
  </s:Body>
</s:Envelope>"""


async def get_device_information(
    host: str,
    port: int,
    username: str,
    password: str,
    *,
    timeout: float = 8.0,
) -> OnvifDeviceInfo:
    if not username or not password:
        return OnvifDeviceInfo(ok=False, error="Не заданы учётные данные")

    url = f"http://{host}:{port}/onvif/device_service"
    headers = {
        "Content-Type": "application/soap+xml; charset=utf-8",
    }
    auth = httpx.DigestAuth(username, password)
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            verify=False,
            follow_redirects=True,
        ) as client:
            response = await client.post(
                url,
                content=_GET_DEVICE_INFO_BODY.encode("utf-8"),
                headers=headers,
                auth=auth,
            )
            if response.status_code == 401:
                return OnvifDeviceInfo(ok=False, error="Ошибка аутентификации (401)")
            if response.status_code >= 400:
                return OnvifDeviceInfo(
                    ok=False,
                    error=f"HTTP {response.status_code}",
                )
            info = _extract_device_info_xml(response.text)
            if not info:
                return OnvifDeviceInfo(ok=False, error="Пустой ответ ONVIF")
            brand = _normalize_brand(info.get("Manufacturer"))
            return OnvifDeviceInfo(
                ok=True,
                manufacturer=info.get("Manufacturer"),
                model=info.get("Model"),
                firmware_version=info.get("FirmwareVersion"),
                serial_number=info.get("SerialNumber"),
                brand=brand,
            )
    except httpx.TimeoutException:
        return OnvifDeviceInfo(ok=False, error="Таймаут")
    except httpx.ConnectError:
        return OnvifDeviceInfo(ok=False, error="Нет соединения")
    except httpx.RequestError as exc:
        return OnvifDeviceInfo(ok=False, error=f"Ошибка сети: {exc}")
