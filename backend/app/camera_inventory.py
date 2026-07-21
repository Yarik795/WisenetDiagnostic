"""Прямой опрос IP-камер с регистраторов: бренд, S/N, дата для отчёта."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .config_store import ConfigStore
from .dahua_cgi import probe_dahua
from .hanwha_camera import probe_hanwha_camera
from .models import Credentials
from .onvif_deviceinfo import get_device_information
from .state_store import ChannelRow, StateStore


@dataclass(frozen=True)
class CameraInventoryTarget:
    recorder_id: str
    channel_no: int
    host: str
    port: int
    username: str
    password: str
    protocol_hint: Optional[str]
    model_hint: Optional[str]


@dataclass
class CameraInventoryOutcome:
    manufacturer: str
    camera_serial: Optional[str] = None
    manufacture_date: Optional[str] = None
    manufacture_date_source: Optional[str] = None
    camera_model: Optional[str] = None
    error: Optional[str] = None


def resolve_camera_credentials(
    channel: ChannelRow,
    defaults: Credentials,
) -> tuple[str, str]:
    username = (channel.camera_user_id or "").strip() or defaults.username
    password = defaults.password
    return username, password


def resolve_camera_port(channel: ChannelRow) -> int:
    if channel.camera_http_port and 1 <= channel.camera_http_port <= 65535:
        return channel.camera_http_port
    return 80


def build_inventory_targets(
    config_store: ConfigStore,
    state_store: StateStore,
) -> list[CameraInventoryTarget]:
    config = config_store.load()
    defaults = config.credentials
    seen_ips: set[str] = set()
    targets: list[CameraInventoryTarget] = []
    for channel in state_store.list_ip_camera_channels():
        ip = (channel.camera_ip or "").strip()
        if not ip or ip in seen_ips:
            continue
        seen_ips.add(ip)
        username, password = resolve_camera_credentials(channel, defaults)
        targets.append(
            CameraInventoryTarget(
                recorder_id=channel.recorder_id,
                channel_no=channel.channel_no,
                host=ip,
                port=resolve_camera_port(channel),
                username=username,
                password=password,
                protocol_hint=channel.camera_protocol,
                model_hint=channel.camera_model,
            )
        )
    return targets


def channels_for_ip(state_store: StateStore, ip: str) -> list[ChannelRow]:
    ip_norm = ip.strip()
    return [
        ch
        for ch in state_store.list_ip_camera_channels()
        if (ch.camera_ip or "").strip() == ip_norm
    ]


async def probe_camera_inventory(target: CameraInventoryTarget) -> CameraInventoryOutcome:
    """Каскад: Dahua CGI → Hanwha SUNAPI → ONVIF."""
    dahua = await probe_dahua(
        target.host,
        target.port,
        target.username,
        target.password,
    )
    if dahua.is_dahua:
        return CameraInventoryOutcome(
            manufacturer="dahua",
            camera_serial=dahua.serial_number,
            manufacture_date=dahua.manufacture_date,
            manufacture_date_source="firmware_build" if dahua.manufacture_date else None,
            camera_model=dahua.device_type,
        )

    hanwha = await probe_hanwha_camera(
        target.host,
        target.port,
        target.username,
        target.password,
    )
    if hanwha.is_hanwha:
        return CameraInventoryOutcome(
            manufacturer="hanwha",
            camera_serial=hanwha.serial_number,
            manufacture_date=hanwha.manufacture_date,
            manufacture_date_source="serial_decode" if hanwha.manufacture_date else None,
            camera_model=hanwha.model,
        )

    onvif = await get_device_information(
        target.host,
        target.port,
        target.username,
        target.password,
    )
    if onvif.ok and onvif.brand == "dahua":
        dahua = await probe_dahua(
            target.host,
            target.port,
            target.username,
            target.password,
        )
        return CameraInventoryOutcome(
            manufacturer="dahua",
            camera_serial=onvif.serial_number or dahua.serial_number,
            manufacture_date=dahua.manufacture_date,
            manufacture_date_source="firmware_build" if dahua.manufacture_date else None,
            camera_model=onvif.model or dahua.device_type,
        )

    if onvif.ok and onvif.brand == "hanwha":
        serial = onvif.serial_number
        mfg: Optional[str] = None
        source: Optional[str] = None
        if serial:
            from .serial_manufacture_date import decode_samsung_manufacture_date

            decoded = decode_samsung_manufacture_date(serial)
            if decoded:
                mfg = decoded.strftime("%Y-%m")
                source = "serial_decode"
        return CameraInventoryOutcome(
            manufacturer="hanwha",
            camera_serial=serial,
            manufacture_date=mfg,
            manufacture_date_source=source,
            camera_model=onvif.model,
        )

    if onvif.ok:
        return CameraInventoryOutcome(
            manufacturer=onvif.brand or "other",
            camera_serial=onvif.serial_number,
            camera_model=onvif.model,
        )

    errors = [e for e in (dahua.error, hanwha.error, onvif.error) if e]
    return CameraInventoryOutcome(
        manufacturer="unknown",
        error="; ".join(errors) if errors else "Камера не ответила",
    )


async def apply_inventory_outcome(
    state_store: StateStore,
    ip: str,
    outcome: CameraInventoryOutcome,
    *,
    polled_at: Optional[datetime] = None,
) -> None:
    ts = polled_at or datetime.now(timezone.utc)
    for channel in channels_for_ip(state_store, ip):
        state_store.update_camera_inventory(
            channel.recorder_id,
            channel.channel_no,
            manufacturer=outcome.manufacturer,
            camera_serial=outcome.camera_serial,
            manufacture_date=outcome.manufacture_date,
            manufacture_date_source=outcome.manufacture_date_source,
            camera_model=outcome.camera_model,
            camera_inventory_at=ts,
            camera_inventory_error=outcome.error,
        )
