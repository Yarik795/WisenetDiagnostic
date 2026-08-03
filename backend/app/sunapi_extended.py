from __future__ import annotations

import asyncio
import html
import re
import socket
import struct
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlencode

import httpx

from .models import Credentials, Recorder
from .sunapi import DeviceInfo, SunapiCheckOutcome, build_deviceinfo_url, parse_deviceinfo_response
from .ui.metrics_helpers import aggregate_storage_from_disks
from .sunapi_parsing import (
    RECORD_FRAME_DROP_LOG_TYPE,
    find_frame_drop_lines,
    parse_channel_indexed,
    parse_datetime_local,
    parse_key_value_body,
    parse_storage_indexed,
    parse_systemlog_latest_timestamp,
    try_parse_json,
)

RECORD_FRAME_DROP_SCAN_DAYS = 90

# Часовой пояс GMT+3 для NVR (SUNAPI POSIXTimeZone)
DEFAULT_NTP_POSIX_TIMEZONE = "STWT-3STWST,M3.5.0/1:00:00,M10.5.0/1:00:00"
NTP_TIME_SKEW_APPLY_THRESHOLD_SECONDS = 1.0
NTP_EPOCH_DELTA = 2208988800  # секунды между 1900-01-01 и 1970-01-01
NTP_QUERY_TIMEOUT_SECONDS = 5.0
# Смещение локального времени устройства (GMT+3, POSIX STWT-3)
NTP_LOCAL_UTC_OFFSET = timedelta(hours=3)

# Модели с температурой в формате «35°C/95°F» — показываем только °C
MODELS_CELSIUS_ONLY_TEMPERATURE = frozenset(
    {"XRN-2010", "XRN-2010A", "XRN-2010P", "HRX-1620"}
)
# ConnectFail / AuthFail в cameraregister при живом потоке (eventstatus) — устаревшее поле Status
MODELS_STALE_REGISTER_STATUS_PREFIXES = ("HRX-1620", "XRN-2010")
_STALE_REGISTER_STATUSES = frozenset({"connectfail", "authfail"})

_CGI_VERSION_RE = re.compile(r"(\d+)\.(\d+)")
_SIZE_UNIT_RE = re.compile(
    r"^([\d.,]+)\s*(TB|GB|MB|КБ|МБ|ТБ)?$",
    re.IGNORECASE,
)
_DISKUTILITY_ERROR_MARKERS = ("NG", "Error Code:", "Submenu Not Found")
_SUNAPI_ERROR_CODE_RE = re.compile(r"Error\s+Code:\s*(\d+)", re.IGNORECASE)
_REGISTER_STATUS_ERROR = frozenset(
    {"connectfail", "disconnected", "fail", "failed", "error"}
)


def normalize_register_status(status: Optional[str]) -> str:
    if not status:
        return ""
    return status.strip().lower().replace(" ", "").replace("_", "")


def is_register_status_error(status: Optional[str]) -> bool:
    return normalize_register_status(status) in _REGISTER_STATUS_ERROR


def is_connectfail_register_status(status: Optional[str]) -> bool:
    return normalize_register_status(status) == "connectfail"


def is_stale_register_status(status: Optional[str]) -> bool:
    return normalize_register_status(status) in _STALE_REGISTER_STATUSES


def model_ignores_stale_register_status(model: Optional[str]) -> bool:
    if not model:
        return False
    model_upper = model.strip().upper()
    if model_upper in MODELS_CELSIUS_ONLY_TEMPERATURE:
        return True
    return any(
        model_upper.startswith(prefix)
        for prefix in MODELS_STALE_REGISTER_STATUS_PREFIXES
    )


def model_ignores_stale_connectfail(model: Optional[str]) -> bool:
    return model_ignores_stale_register_status(model)


def channel_stream_appears_live(
    ch: "ChannelInfo",
    event: Optional["EventChannelStatus"],
) -> bool:
    if event is None:
        return False
    if event.video_loss is True:
        return False
    if event.connected is not True:
        return False
    if ch.data_rate is not None and ch.data_rate <= 0:
        return False
    return True


def is_stale_register_status_on_live_channel(
    ch: "ChannelInfo",
    event: Optional["EventChannelStatus"],
    *,
    device_model: Optional[str] = None,
) -> bool:
    if not model_ignores_stale_register_status(device_model):
        return False
    if (ch.source_state or "").lower() != "on":
        return False
    if not is_stale_register_status(ch.register_status):
        return False
    return channel_stream_appears_live(ch, event)


def is_stale_connectfail_on_live_channel(
    ch: "ChannelInfo",
    event: Optional["EventChannelStatus"],
    *,
    device_model: Optional[str] = None,
) -> bool:
    return is_stale_register_status_on_live_channel(
        ch, event, device_model=device_model
    )


_COMBINED_TEMP_RE = re.compile(
    r"^(\d+)\s*(?:&#?\d+;|\u00b0|\°|.)?\s*C",
    re.IGNORECASE,
)


def _parse_optional_float(raw) -> Optional[float]:
    if raw is None:
        return None
    text = str(raw).strip().replace(",", ".")
    if not text:
        return None
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def channel_is_active(ch: "ChannelInfo") -> bool:
    state = (ch.source_state or ch.video_state or "").strip().lower()
    return state == "on"


def is_analog_channel(ch: "ChannelInfo") -> bool:
    """Аналоговый вход: в API модель/имя «Analog CAM», IP и битрейт IP-потока не применимы."""
    for raw in (ch.camera_model, ch.name):
        if raw and "analog" in raw.strip().lower():
            return True
    return False


@dataclass
class ChannelInfo:
    channel_no: int
    name: Optional[str] = None
    source_state: Optional[str] = None
    video_state: Optional[str] = None
    camera_ip: Optional[str] = None
    camera_model: Optional[str] = None
    camera_user_id: Optional[str] = None
    camera_http_port: Optional[int] = None
    camera_protocol: Optional[str] = None
    register_status: Optional[str] = None
    data_rate: Optional[float] = None
    cpu_usage: Optional[float] = None
    poe_status: Optional[bool] = None


@dataclass
class StorageInfo:
    used_space_mb: Optional[float] = None
    total_space_mb: Optional[float] = None
    used_percent: Optional[float] = None
    disks: list[dict] = field(default_factory=list)
    worst_status: Optional[str] = None
    storageinfo_ok: bool = False


@dataclass
class DateTimeInfo:
    local_time: Optional[str] = None
    utc_time: Optional[str] = None
    sync_type: Optional[str] = None
    ntp_status: Optional[str] = None
    ntp_url_list: Optional[str] = None
    skew_seconds: Optional[float] = None


@dataclass
class EnableNtpResult:
    success: bool
    error: Optional[str] = None
    date_time: Optional[DateTimeInfo] = None


@dataclass
class RecordingPeriodInfo:
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    archive_days: Optional[float] = None
    channel_no: Optional[int] = None


@dataclass
class EventChannelStatus:
    channel_no: int
    video_loss: Optional[bool] = None
    connected: Optional[bool] = None
    low_fps: Optional[bool] = None
    tampering: Optional[bool] = None
    defocus: Optional[bool] = None
    fog: Optional[bool] = None
    sd_fail: Optional[bool] = None
    sd_full: Optional[bool] = None


@dataclass
class EventStatusResult:
    channels: list[EventChannelStatus] = field(default_factory=list)
    system_events: dict[str, bool] = field(default_factory=dict)


@dataclass
class NvrApiProfile:
    """Возможности SUNAPI по модели и версии CGI (после deviceinfo)."""

    model: Optional[str] = None
    cgi_version: Optional[float] = None
    supports_diskutility: bool = True
    celsius_only_temperature: bool = False
    supports_poe_status: bool = False
    supports_modern_storage_metrics: bool = False

    @classmethod
    def from_device(cls, device: Optional[DeviceInfo]) -> "NvrApiProfile":
        model = (device.model or "").strip() if device else ""
        cgi_raw = device.cgi_version if device else None
        cgi_ver = _parse_cgi_version(cgi_raw)
        model_upper = model.upper()

        celsius_only = any(
            model_upper.startswith(prefix)
            for prefix in ("HRX-1620", "XRN-2010")
        ) or model_upper in MODELS_CELSIUS_ONLY_TEMPERATURE

        supports_diskutility = True
        if cgi_ver is not None and cgi_ver < 2.6:
            supports_diskutility = False
        if any(model_upper.startswith(p) for p in ("HRX-1620", "XRN-2010")):
            supports_diskutility = False

        supports_poe = cgi_ver is not None and cgi_ver >= 2.6
        supports_modern_storage = supports_poe

        return cls(
            model=model or None,
            cgi_version=cgi_ver,
            supports_diskutility=supports_diskutility,
            celsius_only_temperature=celsius_only,
            supports_poe_status=supports_poe,
            supports_modern_storage_metrics=supports_modern_storage,
        )


@dataclass
class RecorderPollData:
    device: Optional[DeviceInfo] = None
    online: bool = False
    error: Optional[str] = None
    channels_polled: bool = False
    storage: Optional[StorageInfo] = None
    date_time: Optional[DateTimeInfo] = None
    recording_period: Optional[RecordingPeriodInfo] = None
    channel_recording_periods: dict[int, RecordingPeriodInfo] = field(
        default_factory=dict
    )
    channels: list[ChannelInfo] = field(default_factory=list)
    events: list[EventChannelStatus] = field(default_factory=list)
    system_events: dict[str, bool] = field(default_factory=dict)
    recording_period_error: Optional[str] = None
    recording_storage_enable: Optional[bool] = None
    recording_storage_overwrite: Optional[bool] = None
    cpu_usage_max: Optional[float] = None
    cpu_usage_avg: Optional[float] = None
    data_rate_total_mbps: Optional[float] = None
    channels_zero_bitrate: int = 0
    channels_poe_off: int = 0
    system_event_times: dict[str, str] = field(default_factory=dict)


def build_base_url(recorder: Recorder, cgi: str) -> str:
    scheme = "https" if recorder.use_https else "http"
    return f"{scheme}://{recorder.host}:{recorder.port}/stw-cgi/{cgi}"


def build_url(recorder: Recorder, cgi: str, submenu: str, action: str = "view", **params: str) -> str:
    base = build_base_url(recorder, cgi)
    query: dict[str, str] = {"msubmenu": submenu, "action": action, **params}
    return f"{base}?{urlencode(query)}"


def _parse_cgi_version(raw: Optional[str]) -> Optional[float]:
    if not raw:
        return None
    m = _CGI_VERSION_RE.search(str(raw).strip())
    if not m:
        return None
    return float(f"{m.group(1)}.{m.group(2)}")


def _is_diskutility_error(body: str) -> bool:
    text = (body or "").strip()
    if not text:
        return True
    upper = text.upper()
    return any(marker.upper() in upper for marker in _DISKUTILITY_ERROR_MARKERS)


def parse_sunapi_error_body(body: str) -> Optional[str]:
    """Код ошибки SUNAPI (NG / Error Code: NNN) или None, если ответ не ошибка."""
    text = (body or "").strip()
    if not text:
        return None
    upper = text.upper()
    if not upper.startswith("NG") and "ERROR CODE:" not in upper:
        return None
    m = _SUNAPI_ERROR_CODE_RE.search(text)
    if m:
        return m.group(1)
    return "NG"


def parse_recording_storage(body: str) -> tuple[Optional[bool], Optional[bool]]:
    """Enable и OverWrite из recording.cgi?msubmenu=storage."""
    data = try_parse_json(body)
    if isinstance(data, dict):
        enable = (
            _parse_bool_value(data["Enable"])
            if "Enable" in data
            else None
        )
        overwrite = (
            _parse_bool_value(data["OverWrite"])
            if "OverWrite" in data
            else None
        )
        return enable, overwrite
    fields = parse_key_value_body(body)
    enable = (
        _parse_bool_value(fields["Enable"]) if "Enable" in fields else None
    )
    overwrite = (
        _parse_bool_value(fields["OverWrite"])
        if "OverWrite" in fields
        else None
    )
    return enable, overwrite


def _period_signature(period: Optional[RecordingPeriodInfo]) -> Optional[tuple[str, str]]:
    if not period or not period.start_time or not period.end_time:
        return None
    return (period.start_time.strip(), period.end_time.strip())


async def _fetch(
    recorder: Recorder,
    credentials: Credentials,
    url: str,
    timeout: float = 20.0,
) -> tuple[int, str, Optional[str]]:
    try:
        async with httpx.AsyncClient(
            timeout=timeout, verify=False, follow_redirects=True
        ) as client:
            response = await client.get(
                url,
                auth=httpx.DigestAuth(credentials.username, credentials.password),
            )
            return response.status_code, response.text, None
    except httpx.TimeoutException:
        return 0, "", "Превышено время ожидания"
    except httpx.ConnectError:
        return 0, "", "Нет соединения"
    except httpx.RequestError as exc:
        return 0, "", f"Ошибка сети: {exc}"


def parse_videosource_channels(body: str) -> list[ChannelInfo]:
    data = try_parse_json(body)
    if isinstance(data, dict) and "VideoSources" in data:
        channels = []
        for item in data["VideoSources"]:
            ch = item.get("Channel")
            if ch is None:
                continue
            channels.append(
                ChannelInfo(
                    channel_no=int(ch),
                    name=item.get("Name"),
                    source_state=item.get("State"),
                )
            )
        return channels

    fields = parse_key_value_body(body)
    indexed = parse_channel_indexed(fields, "Channel")
    return [
        ChannelInfo(
            channel_no=ch,
            name=attrs.get("Name"),
            source_state=attrs.get("State"),
        )
        for ch, attrs in sorted(indexed.items())
    ]


def _parse_data_rate(raw) -> Optional[float]:
    return _parse_optional_float(raw)


def _parse_http_port(raw) -> Optional[int]:
    if raw is None or raw == "":
        return None
    try:
        port = int(str(raw).strip())
        if 1 <= port <= 65535:
            return port
    except (TypeError, ValueError):
        return None
    return None


def _channel_from_register_item(item: dict) -> Optional[ChannelInfo]:
    ch = item.get("Channel")
    if ch is None:
        return None
    name = item.get("Title") or item.get("Name") or item.get("Model")
    poe = (
        _parse_bool_value(item["PoeStatus"])
        if "PoeStatus" in item
        else None
    )
    return ChannelInfo(
        channel_no=int(ch),
        camera_ip=item.get("IPAddress"),
        camera_model=item.get("Model"),
        camera_user_id=item.get("UserID"),
        camera_http_port=_parse_http_port(item.get("HTTPPort")),
        camera_protocol=item.get("Protocol"),
        register_status=item.get("Status"),
        data_rate=_parse_data_rate(item.get("DataRate")),
        cpu_usage=_parse_optional_float(item.get("CPUUsage")),
        video_state=item.get("VideoState"),
        name=name,
        poe_status=poe,
    )


def parse_cameraregister(body: str) -> list[ChannelInfo]:
    data = try_parse_json(body)
    if isinstance(data, dict) and "RegisteredCameras" in data:
        channels = []
        for item in data["RegisteredCameras"]:
            ch = item.get("Channel")
            if ch is None:
                continue
            parsed = _channel_from_register_item(item)
            if parsed is not None:
                channels.append(parsed)
        return channels

    fields = parse_key_value_body(body)
    indexed = parse_channel_indexed(fields, "Channel")
    channels = []
    for ch, attrs in sorted(indexed.items()):
        name = attrs.get("Title") or attrs.get("Name") or attrs.get("Model")
        poe = (
            _parse_bool_value(attrs["PoeStatus"])
            if "PoeStatus" in attrs
            else None
        )
        channels.append(
            ChannelInfo(
                channel_no=ch,
                camera_ip=attrs.get("IPAddress"),
                camera_model=attrs.get("Model"),
                camera_user_id=attrs.get("UserID"),
                camera_http_port=_parse_http_port(attrs.get("HTTPPort")),
                camera_protocol=attrs.get("Protocol"),
                register_status=attrs.get("Status"),
                data_rate=_parse_data_rate(attrs.get("DataRate")),
                cpu_usage=_parse_optional_float(attrs.get("CPUUsage")),
                video_state=attrs.get("VideoState"),
                name=name,
                poe_status=poe,
            )
        )
    return channels


def merge_channels(*sources: list[ChannelInfo]) -> list[ChannelInfo]:
    merged: dict[int, ChannelInfo] = {}
    for source in sources:
        for ch in source:
            if ch.channel_no not in merged:
                merged[ch.channel_no] = ch
                continue
            existing = merged[ch.channel_no]
            for attr in (
                "name",
                "source_state",
                "video_state",
                "camera_ip",
                "camera_model",
                "register_status",
                "data_rate",
                "cpu_usage",
                "poe_status",
            ):
                if getattr(existing, attr) is None and getattr(ch, attr) is not None:
                    setattr(existing, attr, getattr(ch, attr))
    return [merged[k] for k in sorted(merged)]


def format_celsius_only_temperature(raw: str) -> Optional[str]:
    """Из строки вида 35°C/95°F оставляет только значение в °C."""
    if not raw:
        return None
    text = html.unescape(str(raw).strip())
    m = _COMBINED_TEMP_RE.match(text)
    if m:
        return f"{m.group(1)} °C"
    if "/" in text:
        left = text.split("/", 1)[0].strip()
        digits = re.search(r"(\d+)", left)
        if digits:
            return f"{digits.group(1)} °C"
    return None


def _model_uses_celsius_only_temperature(
    model: Optional[str], *, profile: Optional[NvrApiProfile] = None
) -> bool:
    if profile is not None:
        return profile.celsius_only_temperature
    if not model:
        return False
    model_upper = model.strip().upper()
    if model_upper in MODELS_CELSIUS_ONLY_TEMPERATURE:
        return True
    return any(
        model_upper.startswith(prefix) for prefix in ("HRX-1620", "XRN-2010")
    )


def _finalize_disk_temperature(
    temp: Optional[str],
    *,
    model: Optional[str] = None,
    profile: Optional[NvrApiProfile] = None,
) -> Optional[str]:
    if not temp:
        return None
    if _model_uses_celsius_only_temperature(model, profile=profile):
        normalized = format_celsius_only_temperature(temp)
        if normalized:
            return normalized
    return temp


def extract_disk_temperature(
    disk: dict,
    *,
    model: Optional[str] = None,
    profile: Optional[NvrApiProfile] = None,
) -> Optional[str]:
    """Температура из storageinfo: плоские поля, Health или SMART.Attributes."""
    for key in ("TemperatureCelsius", "temperature_celsius"):
        val = disk.get(key)
        if val is not None and str(val).strip() != "":
            return _finalize_disk_temperature(
                f"{val} °C", model=model, profile=profile
            )

    for key in ("Temperature", "temperature"):
        val = disk.get(key)
        if val is not None and str(val).strip() != "":
            return _finalize_disk_temperature(
                str(val).strip(), model=model, profile=profile
            )

    for key in ("TemperatureInCelsius", "temperature_in_celsius"):
        val = disk.get(key)
        if val is not None and str(val).strip() != "":
            return _finalize_disk_temperature(
                f"{val} °C", model=model, profile=profile
            )

    health = disk.get("Health")
    if isinstance(health, dict):
        t = health.get("TemperatureInCelsius")
        if t is not None:
            return _finalize_disk_temperature(
                f"{t} °C", model=model, profile=profile
            )

    smart = disk.get("SMART")
    if isinstance(smart, dict):
        attrs = smart.get("Attributes") or []
        if isinstance(attrs, list):
            for attr in attrs:
                if not isinstance(attr, dict):
                    continue
                name = str(attr.get("Name", "")).lower()
                if name in ("temperature", "hda temperature"):
                    val = attr.get("Value")
                    if val is not None:
                        return _finalize_disk_temperature(
                            f"{val} °C", model=model, profile=profile
                        )
    return None


def normalize_disk_record(
    disk: dict,
    *,
    model: Optional[str] = None,
    profile: Optional[NvrApiProfile] = None,
) -> dict:
    out = dict(disk)
    temp = extract_disk_temperature(disk, model=model, profile=profile)
    if temp:
        out["Temperature"] = temp
    hours = _disk_power_on_hours_value(out)
    if hours is not None:
        out["PowerOnDuration"] = str(hours)
    return out


def normalize_storage_disks(
    disks: list[dict],
    *,
    model: Optional[str] = None,
    profile: Optional[NvrApiProfile] = None,
) -> list[dict]:
    return [normalize_disk_record(d, model=model, profile=profile) for d in disks]


_TEMPERATURE_SMART_RE = re.compile(
    r"Temperature\s*:\s*(\d+)\s*(?:&#?\d+;|\u00b0|\°)?\s*C?",
    re.IGNORECASE,
)
_POWER_ON_HOURS_SMART_RE = re.compile(
    r"009\s+Power[_-]On[_-]Hours\s+\d+\s+\d+\s+\d+\s+(\d+)",
    re.IGNORECASE,
)
_LEGACY_STORAGE_MODEL_PREFIXES = ("HRX-1620", "XRN-2010")


def parse_temperature_from_smart(
    text: str, *, model: Optional[str] = None
) -> Optional[str]:
    if not text:
        return None
    plain = html.unescape(text)
    plain = re.sub(r"<[^>]+>", " ", plain)
    if _model_uses_celsius_only_temperature(model):
        combined = format_celsius_only_temperature(plain)
        if combined:
            return combined
    m = _TEMPERATURE_SMART_RE.search(plain)
    if m:
        return f"{m.group(1)} °C"
    return None


def parse_power_on_hours_from_smart(text: str) -> Optional[int]:
    """SMART attribute 009 Power_On_Hours → часы наработки."""
    if not text:
        return None
    plain = html.unescape(text)
    plain = re.sub(r"<[^>]+>", " ", plain)
    m = _POWER_ON_HOURS_SMART_RE.search(plain)
    if not m:
        return None
    try:
        return int(m.group(1))
    except (TypeError, ValueError):
        return None


def _smart_fields_from_text(
    text: str, *, model: Optional[str] = None
) -> dict[str, str]:
    out: dict[str, str] = {}
    temp = parse_temperature_from_smart(text, model=model)
    if temp:
        out["Temperature"] = temp
    hours = parse_power_on_hours_from_smart(text)
    if hours is not None:
        out["PowerOnDuration"] = str(hours)
    return out


def _disk_slot_index(disk: dict) -> Optional[int]:
    for key in ("SlotNumber", "slot_number", "Storage", "storage", "Slot", "slot"):
        raw = disk.get(key)
        if raw is None:
            continue
        try:
            return int(str(raw).strip())
        except (TypeError, ValueError):
            continue
    return None


def _disk_power_on_hours_value(disk: dict) -> Optional[int]:
    health = disk.get("Health")
    if isinstance(health, dict):
        for key in (
            "PowerOnHours",
            "power_on_hours",
            "PowerOnDuration",
            "UseTime",
            "use_time",
        ):
            raw = health.get(key)
            if raw is not None and str(raw).strip():
                try:
                    return int(float(str(raw).replace(",", ".")))
                except (TypeError, ValueError):
                    pass
    for key in (
        "PowerOnDuration",
        "power_on_duration",
        "PowerOnHours",
        "power_on_hours",
        "UseTime",
        "use_time",
        "UseDuration",
        "use_duration",
        "OperationTime",
        "operation_time",
    ):
        raw = disk.get(key)
        if raw is None or not str(raw).strip():
            continue
        try:
            return int(float(str(raw).replace(",", ".")))
        except (TypeError, ValueError):
            continue
    return None


def _disk_index_candidates(disk: dict, position: int) -> list[int]:
    """Индексы diskutility для legacy NVR (SlotNumber может ≠ Storage)."""
    candidates: list[int] = []
    for key in ("SlotNumber", "slot_number", "Storage", "storage", "Slot", "slot"):
        raw = disk.get(key)
        if raw is None:
            continue
        try:
            val = int(str(raw).strip())
        except (TypeError, ValueError):
            continue
        if val not in candidates:
            candidates.append(val)
    for val in (position + 1, position):
        if val >= 0 and val not in candidates:
            candidates.append(val)
    return candidates


def _disk_needs_power_on_hours(disk: dict) -> bool:
    return _disk_power_on_hours_value(disk) is None


def _is_legacy_storage_model(model: Optional[str]) -> bool:
    if not model:
        return False
    model_upper = model.strip().upper()
    return any(
        model_upper.startswith(prefix) for prefix in _LEGACY_STORAGE_MODEL_PREFIXES
    )


def parse_diskutility_list(body: str, *, model: Optional[str] = None) -> list[dict]:
    data = try_parse_json(body)
    if isinstance(data, dict) and isinstance(data.get("Disks"), list):
        return [
            {"Index": d.get("Index"), "Name": (d.get("Name") or "").strip()}
            for d in data["Disks"]
            if isinstance(d, dict) and d.get("Index") is not None
        ]

    fields = parse_key_value_body(body)
    pattern = re.compile(r"^Disk\.(\d+)\.(.+)$")
    disks: dict[int, dict] = {}
    for key, value in fields.items():
        m = pattern.match(key)
        if not m:
            continue
        idx = int(m.group(1))
        attr = m.group(2)
        disks.setdefault(idx, {})
        if attr == "Index":
            disks[idx]["Index"] = int(value) if value.isdigit() else value
        elif attr == "Name":
            disks[idx]["Name"] = value.strip()
        elif attr == "SMART":
            smart_fields = _smart_fields_from_text(value, model=model)
            disks[idx].update(smart_fields)
    return [
        disks[k]
        for k in sorted(disks)
        if disks[k].get("Index") is not None
    ]


def parse_diskutility_detail(body: str, *, model: Optional[str] = None) -> dict:
    data = try_parse_json(body)
    if isinstance(data, dict) and isinstance(data.get("Disks"), list) and data["Disks"]:
        item = data["Disks"][0]
        if isinstance(item, dict):
            smart = item.get("SMART") or ""
            result = {
                "Index": item.get("Index"),
                "Name": (item.get("Name") or "").strip(),
            }
            result.update(_smart_fields_from_text(str(smart), model=model))
            return result

    fields = parse_key_value_body(body)
    pattern = re.compile(r"^Disk\.(\d+)\.(.+)$")
    result: dict = {}
    for key, value in fields.items():
        m = pattern.match(key)
        if not m:
            continue
        attr = m.group(2)
        if attr == "Index":
            result["Index"] = int(value) if value.isdigit() else value
        elif attr == "Name":
            result["Name"] = value.strip()
        elif attr == "SMART":
            result.update(_smart_fields_from_text(value, model=model))
    return result


def merge_disk_temperatures(
    storage_disks: list[dict],
    utility_disks: list[dict],
    *,
    model: Optional[str] = None,
) -> list[dict]:
    enriched = normalize_storage_disks(storage_disks, model=model)
    if not utility_disks:
        return enriched

    by_name = {
        (u.get("Name") or "").strip().lower(): u
        for u in utility_disks
        if u.get("Name")
    }

    for i, disk in enumerate(enriched):
        if disk.get("Temperature"):
            continue
        model = str(disk.get("Model") or disk.get("model") or "").strip().lower()
        if model and model in by_name and by_name[model].get("Temperature"):
            disk["Temperature"] = by_name[model]["Temperature"]
            continue
        if i < len(utility_disks) and utility_disks[i].get("Temperature"):
            disk["Temperature"] = utility_disks[i]["Temperature"]
    return enriched


def merge_disk_power_on_hours(
    storage_disks: list[dict],
    utility_disks: list[dict],
    *,
    details_by_index: Optional[dict[int, dict]] = None,
) -> list[dict]:
    enriched = [dict(d) for d in storage_disks]
    by_index: dict[int, dict] = {}
    for u in utility_disks:
        idx = u.get("Index")
        if idx is None:
            continue
        try:
            by_index[int(idx)] = dict(u)
        except (TypeError, ValueError):
            continue
    if details_by_index:
        for idx, detail in details_by_index.items():
            merged = dict(by_index.get(idx, {}))
            for key, value in detail.items():
                if value is not None:
                    merged[key] = value
            by_index[idx] = merged

    if not by_index:
        return enriched

    for i, disk in enumerate(enriched):
        if not _disk_needs_power_on_hours(disk):
            continue
        idx = _disk_slot_index(disk)
        source = by_index.get(idx) if idx is not None else None
        if source is None and idx is not None:
            for alt_idx, detail in by_index.items():
                if detail.get("RequestIndex") == idx:
                    source = detail
                    break
        if source is None and i < len(utility_disks):
            source = utility_disks[i]
        if not source:
            continue
        hours = _disk_power_on_hours_value(source)
        if hours is not None:
            disk["PowerOnDuration"] = str(hours)
    return enriched


async def _fetch_diskutility_detail(
    recorder: Recorder,
    credentials: Credentials,
    index: int,
    *,
    device_model: Optional[str] = None,
    cgi: str = "recording.cgi",
    timeout: float = 20.0,
) -> dict:
    detail_url = build_url(recorder, cgi, "diskutility", Index=str(index))
    st, detail_body, _ = await _fetch(recorder, credentials, detail_url, timeout)
    if st != 200 or not detail_body.strip() or _is_diskutility_error(detail_body):
        return {}
    detail = parse_diskutility_detail(detail_body, model=device_model)
    if detail.get("Index") is None:
        detail["Index"] = index
    return detail


async def enrich_storage_disk_metrics(
    recorder: Recorder,
    credentials: Credentials,
    disks: list[dict],
    *,
    device_model: Optional[str] = None,
    profile: Optional[NvrApiProfile] = None,
    timeout: float = 20.0,
    max_detail_fetches: int = 16,
) -> list[dict]:
    normalized = normalize_storage_disks(
        disks, model=device_model, profile=profile
    )
    needs_temp = any(not d.get("Temperature") for d in normalized)
    needs_hours = any(_disk_needs_power_on_hours(d) for d in normalized)
    if not needs_temp and not needs_hours:
        return normalized

    legacy = _is_legacy_storage_model(device_model)
    can_list = profile is None or profile.supports_diskutility
    utility_disks: list[dict] = []

    if can_list and not legacy:
        list_url = build_url(recorder, "recording.cgi", "diskutility")
        status, body, _ = await _fetch(recorder, credentials, list_url, timeout)
        if status == 200 and body.strip() and not _is_diskutility_error(body):
            utility_disks = parse_diskutility_list(body, model=device_model)

    details_by_index: dict[int, dict] = {}
    detail_fetches = 0

    async def _fetch_hours_detail(index: int) -> dict:
        nonlocal detail_fetches
        if detail_fetches >= max_detail_fetches:
            return {}
        detail_fetches += 1
        detail = await _fetch_diskutility_detail(
            recorder,
            credentials,
            index,
            device_model=device_model,
            cgi="recording.cgi",
            timeout=timeout,
        )
        if not _disk_power_on_hours_value(detail) and detail_fetches < max_detail_fetches:
            detail_fetches += 1
            alt = await _fetch_diskutility_detail(
                recorder,
                credentials,
                index,
                device_model=device_model,
                cgi="system.cgi",
                timeout=timeout,
            )
            if _disk_power_on_hours_value(alt) or not detail:
                detail = alt
        if detail:
            detail["RequestIndex"] = index
        return detail

    if legacy and needs_hours:
        for i, disk in enumerate(normalized):
            if not _disk_needs_power_on_hours(disk):
                continue
            for index in _disk_index_candidates(disk, i):
                if detail_fetches >= max_detail_fetches:
                    break
                detail = await _fetch_hours_detail(index)
                if not detail or not _disk_power_on_hours_value(detail):
                    continue
                hours = _disk_power_on_hours_value(detail)
                assert hours is not None
                disk["PowerOnDuration"] = str(hours)
                try:
                    details_by_index[int(detail.get("Index", index))] = detail
                except (TypeError, ValueError):
                    details_by_index[index] = detail
                break
    else:
        indices_to_fetch: list[int] = []
        if utility_disks:
            for u in utility_disks:
                idx = u.get("Index")
                if idx is None:
                    continue
                try:
                    idx_int = int(idx)
                except (TypeError, ValueError):
                    continue
                need_detail = False
                if needs_temp and not u.get("Temperature"):
                    need_detail = True
                if needs_hours and _disk_needs_power_on_hours(u):
                    need_detail = True
                if need_detail and idx_int not in indices_to_fetch:
                    indices_to_fetch.append(idx_int)

        if needs_hours and not indices_to_fetch:
            for i, disk in enumerate(normalized):
                if not _disk_needs_power_on_hours(disk):
                    continue
                for index in _disk_index_candidates(disk, i):
                    if index not in indices_to_fetch:
                        indices_to_fetch.append(index)

        for index in indices_to_fetch:
            if detail_fetches >= max_detail_fetches:
                break
            detail = await _fetch_hours_detail(index)
            if not detail:
                continue
            try:
                details_by_index[int(detail.get("Index", index))] = detail
            except (TypeError, ValueError):
                details_by_index[index] = detail
            for u in utility_disks:
                if u.get("Index") == detail.get("Index"):
                    if detail.get("Temperature"):
                        u["Temperature"] = detail["Temperature"]
                    if detail.get("PowerOnDuration"):
                        u["PowerOnDuration"] = detail["PowerOnDuration"]
                    break
            for i, disk in enumerate(normalized):
                if not _disk_needs_power_on_hours(disk):
                    continue
                if index not in _disk_index_candidates(disk, i):
                    continue
                hours = _disk_power_on_hours_value(detail)
                if hours is not None:
                    disk["PowerOnDuration"] = str(hours)
                    break

    with_temp = merge_disk_temperatures(
        normalized, utility_disks, model=device_model
    )
    return merge_disk_power_on_hours(
        with_temp,
        utility_disks,
        details_by_index=details_by_index or None,
    )


async def enrich_storage_temperatures(
    recorder: Recorder,
    credentials: Credentials,
    disks: list[dict],
    *,
    device_model: Optional[str] = None,
    profile: Optional[NvrApiProfile] = None,
    timeout: float = 20.0,
    max_detail_fetches: int = 16,
) -> list[dict]:
    return await enrich_storage_disk_metrics(
        recorder,
        credentials,
        disks,
        device_model=device_model,
        profile=profile,
        timeout=timeout,
        max_detail_fetches=max_detail_fetches,
    )


def _fill_storage_aggregate_from_disks(info: StorageInfo) -> None:
    if info.used_percent is not None or not info.disks:
        return
    used_mb, total_mb, pct = aggregate_storage_from_disks(info.disks)
    if pct is None:
        return
    if info.used_space_mb is None:
        info.used_space_mb = used_mb
    if info.total_space_mb is None:
        info.total_space_mb = total_mb
    info.used_percent = pct


def parse_storage(
    body: str,
    *,
    model: Optional[str] = None,
    profile: Optional[NvrApiProfile] = None,
) -> StorageInfo:
    data = try_parse_json(body)
    info = StorageInfo()
    if isinstance(data, dict):
        used = _to_float(data.get("UsedSpace"))
        total = _to_float(data.get("TotalSpace"))
        info.used_space_mb = used
        info.total_space_mb = total
        if used is not None and total and total > 0:
            info.used_percent = round(used / total * 100, 1)
        storages = data.get("Storages") or []
        if isinstance(storages, list):
            info.disks = normalize_storage_disks(
                storages, model=model, profile=profile
            )
            info.worst_status = _worst_disk_status(storages)
        root_status = data.get("Status")
        if root_status and not info.worst_status and info.disks:
            info.worst_status = str(root_status)
        _fill_storage_aggregate_from_disks(info)
        return info

    fields = parse_key_value_body(body)
    info.used_space_mb = _to_float(fields.get("UsedSpace"))
    info.total_space_mb = _to_float(fields.get("TotalSpace"))
    if info.used_space_mb is not None and info.total_space_mb and info.total_space_mb > 0:
        info.used_percent = round(info.used_space_mb / info.total_space_mb * 100, 1)
    disks = parse_storage_indexed(fields)
    info.disks = normalize_storage_disks(disks, model=model, profile=profile)
    info.worst_status = _worst_disk_status(disks)
    root_status = fields.get("Status")
    if root_status and not info.worst_status and info.disks:
        info.worst_status = root_status
    _fill_storage_aggregate_from_disks(info)
    return info


def _worst_disk_status(disks: list[dict]) -> Optional[str]:
    error_states = {"Error", "Fail", "Formatting", "Lock", "PWError"}
    statuses = []
    for d in disks:
        st = d.get("Status")
        if st:
            statuses.append(str(st))
    if any(s in error_states for s in statuses):
        return "error"
    if statuses:
        return statuses[0]
    return None


def _normalize_ntp_url_list(value) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, list):
        return ",".join(str(v) for v in value if v)
    return str(value).strip() or None


def is_sunapi_set_success(body: str) -> bool:
    text = (body or "").strip()
    if not text:
        return False
    if text.upper() == "OK":
        return True
    data = try_parse_json(text)
    if isinstance(data, dict):
        response = str(data.get("Response", "")).lower()
        if response in ("success", "ok"):
            return True
    lowered = text.lower()
    if "error" in lowered or "fail" in lowered or "denied" in lowered:
        return False
    return False


def parse_date(body: str) -> DateTimeInfo:
    data = try_parse_json(body)
    info = DateTimeInfo()
    if isinstance(data, dict):
        info.local_time = data.get("LocalTime")
        info.utc_time = data.get("UTCTime")
        info.sync_type = data.get("SyncType")
        info.ntp_status = data.get("NTPStatus")
        info.ntp_url_list = _normalize_ntp_url_list(data.get("NTPURLList"))
    else:
        fields = parse_key_value_body(body)
        info.local_time = fields.get("LocalTime")
        info.utc_time = fields.get("UTCTime")
        info.sync_type = fields.get("SyncType")
        info.ntp_status = fields.get("NTPStatus")
        info.ntp_url_list = fields.get("NTPURLList")

    ref = info.utc_time or info.local_time
    if ref:
        dt = parse_datetime_local(ref.replace("T", " "))
        if dt:
            now = datetime.now(timezone.utc)
            local_utc = dt.replace(tzinfo=timezone.utc)
            info.skew_seconds = abs((now - local_utc).total_seconds())
    return info


async def fetch_date_info(
    recorder: Recorder,
    credentials: Credentials,
    *,
    timeout: float = 20.0,
) -> tuple[Optional[DateTimeInfo], Optional[str]]:
    url = build_url(recorder, "system.cgi", "date")
    status, body, err = await _fetch(recorder, credentials, url, timeout)
    if err:
        return None, err
    if status >= 400 or not body.strip():
        return None, f"HTTP {status}"
    return parse_date(body), None


def _ntp_set_params(server: str, posix_timezone: str) -> dict[str, str]:
    return {
        "SyncType": "NTP",
        "NTPURLList": server,
        "POSIXTimeZone": posix_timezone,
        "NTPServerEnable": "False",
        "DSTEnable": "False",
        "DateFormat": "YYYY-MM-DD",
        "TimeFormat": "HMS24",
    }


def _first_ntp_host(ntp_server: str) -> str:
    host = (ntp_server or "").split(",")[0].strip()
    if not host:
        raise ValueError("Не указан NTP-сервер")
    return host


def query_ntp_utc_time(
    ntp_server: str,
    *,
    timeout: float = NTP_QUERY_TIMEOUT_SECONDS,
) -> datetime:
    """Запрашивает текущее UTC-время у NTP-сервера (UDP/123)."""
    host = _first_ntp_host(ntp_server)
    packet = b"\x1b" + 47 * b"\0"
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        sock.sendto(packet, (host, 123))
        data, _ = sock.recvfrom(48)
    if len(data) < 48:
        raise OSError("Некорректный ответ NTP-сервера")
    transmit_ts = struct.unpack("!12I", data)[10]
    seconds = transmit_ts - NTP_EPOCH_DELTA
    return datetime.fromtimestamp(seconds, tz=timezone.utc)


def ntp_utc_to_local_naive(utc_time: datetime) -> datetime:
    if utc_time.tzinfo is None:
        utc_time = utc_time.replace(tzinfo=timezone.utc)
    local = utc_time + NTP_LOCAL_UTC_OFFSET
    return local.replace(tzinfo=None)


async def fetch_ntp_local_datetime(
    ntp_server: str,
    *,
    timeout: float = NTP_QUERY_TIMEOUT_SECONDS,
) -> tuple[Optional[datetime], Optional[str]]:
    try:
        utc_time = await asyncio.to_thread(
            query_ntp_utc_time, ntp_server, timeout=timeout
        )
        return ntp_utc_to_local_naive(utc_time), None
    except OSError as exc:
        return None, f"Ошибка NTP: {exc}"
    except Exception as exc:
        return None, str(exc)


def _manual_time_set_params(posix_timezone: str, when: Optional[datetime] = None) -> dict[str, str]:
    now = when or datetime.now()
    return {
        "SyncType": "Manual",
        "Year": str(now.year),
        "Month": str(now.month),
        "Day": str(now.day),
        "Hour": str(now.hour),
        "Minute": str(now.minute),
        "Second": str(now.second),
        "POSIXTimeZone": posix_timezone,
        "DSTEnable": "False",
    }


def _skew_exceeds_threshold(
    date_info: Optional[DateTimeInfo],
    threshold: float = NTP_TIME_SKEW_APPLY_THRESHOLD_SECONDS,
) -> bool:
    if not date_info or date_info.skew_seconds is None:
        return False
    return date_info.skew_seconds > threshold


async def _apply_ntp_settings(
    recorder: Recorder,
    credentials: Credentials,
    server: str,
    posix_timezone: str,
    *,
    timeout: float = 20.0,
) -> tuple[bool, Optional[str]]:
    return await _sunapi_date_set(
        recorder,
        credentials,
        timeout=timeout,
        **_ntp_set_params(server, posix_timezone),
    )


async def _sunapi_date_set(
    recorder: Recorder,
    credentials: Credentials,
    *,
    timeout: float = 20.0,
    **params: str,
) -> tuple[bool, Optional[str]]:
    set_url = build_url(
        recorder,
        "system.cgi",
        "date",
        action="set",
        **params,
    )
    status, body, err = await _fetch(recorder, credentials, set_url, timeout)
    if err:
        return False, err
    if status >= 400:
        return False, f"HTTP {status}"
    if not is_sunapi_set_success(body):
        snippet = (body or "").strip()[:300]
        return False, snippet or "Устройство не подтвердило изменение настроек времени"
    return True, None


async def enable_recorder_ntp(
    recorder: Recorder,
    credentials: Credentials,
    ntp_server: str,
    *,
    posix_timezone: str = DEFAULT_NTP_POSIX_TIMEZONE,
    skew_apply_threshold: float = NTP_TIME_SKEW_APPLY_THRESHOLD_SECONDS,
    timeout: float = 20.0,
) -> EnableNtpResult:
    if not credentials.username or not credentials.password:
        return EnableNtpResult(success=False, error="Не заданы учётные данные API")

    server = (ntp_server or "").strip()
    if not server:
        return EnableNtpResult(
            success=False,
            error="Не задан NTP-сервер (monitoring.ntp_server в config.json)",
        )

    tz = (posix_timezone or DEFAULT_NTP_POSIX_TIMEZONE).strip()
    if not tz:
        return EnableNtpResult(
            success=False,
            error="Не задан POSIXTimeZone (monitoring.ntp_posix_timezone в config.json)",
        )

    ok, err = await _apply_ntp_settings(
        recorder, credentials, server, tz, timeout=timeout
    )
    if not ok:
        return EnableNtpResult(success=False, error=err)

    date_info, view_err = await fetch_date_info(recorder, credentials, timeout=timeout)
    if view_err:
        return EnableNtpResult(
            success=False,
            error=f"NTP настроен, но не удалось проверить: {view_err}",
        )

    if _skew_exceeds_threshold(date_info, skew_apply_threshold):
        ntp_local, ntp_time_err = await fetch_ntp_local_datetime(
            server, timeout=min(timeout, NTP_QUERY_TIMEOUT_SECONDS)
        )
        if not ntp_local:
            return EnableNtpResult(
                success=False,
                error=ntp_time_err or "Не удалось получить время с NTP-сервера",
                date_time=date_info,
            )

        manual_ok, manual_err = await _sunapi_date_set(
            recorder,
            credentials,
            timeout=timeout,
            **_manual_time_set_params(tz, when=ntp_local),
        )
        if not manual_ok:
            return EnableNtpResult(
                success=False,
                error=manual_err or "Не удалось установить время с NTP-сервера",
                date_time=date_info,
            )

        ok, err = await _apply_ntp_settings(
            recorder, credentials, server, tz, timeout=timeout
        )
        if not ok:
            return EnableNtpResult(
                success=False,
                error=err or "Время обновлено, но не удалось повторно включить NTP",
                date_time=date_info,
            )

        date_info, view_err = await fetch_date_info(
            recorder, credentials, timeout=timeout
        )
        if view_err:
            return EnableNtpResult(
                success=False,
                error=f"NTP применён, но не удалось проверить время: {view_err}",
            )

    if not date_info or (date_info.sync_type or "").upper() != "NTP":
        actual = date_info.sync_type if date_info else "неизвестно"
        return EnableNtpResult(
            success=False,
            error=f"Команда отправлена, но устройство вернуло SyncType={actual}",
            date_time=date_info,
        )
    return EnableNtpResult(success=True, date_time=date_info)


def _apply_period_times(info: RecordingPeriodInfo) -> RecordingPeriodInfo:
    start = info.start_time
    end = info.end_time
    if start and end:
        ds = parse_datetime_local(start.replace("T", " "))
        de = parse_datetime_local(end.replace("T", " "))
        if ds and de and de > ds:
            info.archive_days = (de - ds).total_seconds() / 86400
    return info


def parse_recording_period(body: str, *, channel_no: Optional[int] = None) -> RecordingPeriodInfo:
    fields = parse_key_value_body(body)
    data = try_parse_json(body)
    info = RecordingPeriodInfo(channel_no=channel_no)
    if isinstance(data, dict):
        info.start_time = data.get("StartTime")
        info.end_time = data.get("EndTime")
        ch = data.get("Channel")
        if ch is not None:
            info.channel_no = int(ch)
    else:
        info.start_time = fields.get("StartTime")
        info.end_time = fields.get("EndTime")
        if channel_no is not None:
            prefix = f"Channel.{channel_no}."
            ch_start = fields.get(f"{prefix}StartTime")
            ch_end = fields.get(f"{prefix}EndTime")
            if ch_start and ch_end:
                info.start_time = ch_start
                info.end_time = ch_end
                info.channel_no = channel_no

    return _apply_period_times(info)


def _period_has_archive_data(period: RecordingPeriodInfo) -> bool:
    return period.archive_days is not None or bool(
        period.start_time and period.end_time
    )


def _clone_global_period_for_channels(
    channel_nos: list[int],
    global_period: RecordingPeriodInfo,
) -> dict[int, RecordingPeriodInfo]:
    return {
        ch_no: RecordingPeriodInfo(
            start_time=global_period.start_time,
            end_time=global_period.end_time,
            archive_days=global_period.archive_days,
            channel_no=ch_no,
        )
        for ch_no in channel_nos
    }


async def fetch_channel_recording_periods(
    recorder: Recorder,
    credentials: Credentials,
    channel_nos: list[int],
    global_period: Optional[RecordingPeriodInfo],
    *,
    timeout: float = 20.0,
    max_channels: int = 64,
    max_concurrent: int = 8,
    detailed_archive: bool = False,
    sample_verify_count: int = 3,
) -> dict[int, RecordingPeriodInfo]:
    if not channel_nos:
        return {}

    nos = channel_nos[:max_channels]
    global_sig = _period_signature(global_period)
    has_global = global_period is not None and _period_has_archive_data(global_period)

    if has_global and not detailed_archive:
        sample_nos = nos[:sample_verify_count]
        if not sample_nos:
            return _clone_global_period_for_channels(nos, global_period)

        sem = asyncio.Semaphore(max_concurrent)

        async def fetch_sample(ch_no: int) -> tuple[int, Optional[RecordingPeriodInfo]]:
            async with sem:
                url = build_url(
                    recorder,
                    "recording.cgi",
                    "searchrecordingperiod",
                    Channel=str(ch_no),
                )
                status, body, _ = await _fetch(
                    recorder, credentials, url, timeout
                )
                if status != 200 or not body.strip():
                    return ch_no, None
                period = parse_recording_period(body, channel_no=ch_no)
                if _period_has_archive_data(period):
                    return ch_no, period
                return ch_no, None

        sample_results = await asyncio.gather(
            *(fetch_sample(n) for n in sample_nos)
        )
        sample_periods = [p for _, p in sample_results if p is not None]
        if sample_periods and all(
            _period_signature(p) == global_sig for p in sample_periods
        ):
            return _clone_global_period_for_channels(nos, global_period)

    sem = asyncio.Semaphore(max_concurrent)

    async def fetch_one(ch_no: int) -> tuple[int, Optional[RecordingPeriodInfo]]:
        async with sem:
            url = build_url(
                recorder,
                "recording.cgi",
                "searchrecordingperiod",
                Channel=str(ch_no),
            )
            status, body, _ = await _fetch(recorder, credentials, url, timeout)
            if status != 200 or not body.strip():
                return ch_no, None
            period = parse_recording_period(body, channel_no=ch_no)
            if _period_has_archive_data(period):
                return ch_no, period
            return ch_no, None

    results = await asyncio.gather(*(fetch_one(n) for n in nos))
    periods: dict[int, RecordingPeriodInfo] = {}
    for ch_no, period in results:
        if period is not None:
            periods[ch_no] = period
        elif has_global:
            periods[ch_no] = RecordingPeriodInfo(
                start_time=global_period.start_time,
                end_time=global_period.end_time,
                archive_days=global_period.archive_days,
                channel_no=ch_no,
            )
    return periods


def _parse_bool_value(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def _apply_channel_event_attr(
    ch_status: EventChannelStatus, attr: str, value
) -> None:
    attr_lower = attr.lower()
    if attr_lower == "videoloss":
        ch_status.video_loss = _parse_bool_value(value)
    elif attr in ("Connected", "NetworkCameraConnect"):
        ch_status.connected = _parse_bool_value(value)
    elif attr_lower == "lowfps":
        ch_status.low_fps = _parse_bool_value(value)
    elif attr_lower == "tampering":
        ch_status.tampering = _parse_bool_value(value)
    elif attr_lower == "defocusdetection":
        ch_status.defocus = _parse_bool_value(value)
    elif attr_lower == "fogdetection":
        ch_status.fog = _parse_bool_value(value)
    elif attr_lower == "sdfail":
        ch_status.sd_fail = _parse_bool_value(value)
    elif attr_lower == "sdfull":
        ch_status.sd_full = _parse_bool_value(value)


def _collect_system_events_from_fields(fields: dict[str, str]) -> dict[str, bool]:
    system_events: dict[str, bool] = {}
    prefix = "SystemEvent."
    for key, value in fields.items():
        if not key.startswith(prefix):
            continue
        event_key = key[len(prefix) :]
        if event_key:
            system_events[event_key] = _parse_bool_value(value)
    return system_events


def _collect_system_events_from_json(data: dict) -> dict[str, bool]:
    system_events: dict[str, bool] = {}
    raw = data.get("SystemEvent")
    if not isinstance(raw, dict):
        return system_events

    def walk(prefix: str, obj: dict) -> None:
        for key, val in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(val, dict):
                walk(full_key, val)
            elif isinstance(val, bool):
                system_events[full_key] = val
            elif val is not None and str(val).strip().lower() in ("true", "false"):
                system_events[full_key] = str(val).strip().lower() == "true"

    walk("", raw)
    return system_events


def parse_eventstatus(body: str) -> EventStatusResult:
    fields = parse_key_value_body(body)
    channels: dict[int, EventChannelStatus] = {}
    channel_pattern = re.compile(r"^Channel\.(\d+)\.(.+)$")
    for key, value in fields.items():
        m = channel_pattern.match(key)
        if not m:
            continue
        ch = int(m.group(1))
        attr = m.group(2)
        channels.setdefault(ch, EventChannelStatus(channel_no=ch))
        _apply_channel_event_attr(channels[ch], attr, value)

    system_events = _collect_system_events_from_fields(fields)

    data = try_parse_json(body)
    if isinstance(data, dict):
        if "ChannelEvent" in data:
            for item in data["ChannelEvent"]:
                ch = item.get("Channel")
                if ch is None:
                    continue
                ch = int(ch)
                channels.setdefault(ch, EventChannelStatus(channel_no=ch))
                for key, val in item.items():
                    if key == "Channel":
                        continue
                    if isinstance(val, bool) or (
                        isinstance(val, str)
                        and val.strip().lower() in ("true", "false")
                    ):
                        _apply_channel_event_attr(channels[ch], key, val)
                    elif key == "NetworkCameraConnect" and val is not None:
                        _apply_channel_event_attr(
                            channels[ch], "NetworkCameraConnect", val
                        )
        json_system = _collect_system_events_from_json(data)
        if json_system:
            system_events = json_system

    return EventStatusResult(
        channels=[channels[k] for k in sorted(channels)],
        system_events=system_events,
    )


def compute_stream_metrics(
    channels: list[ChannelInfo],
    *,
    profile: Optional[NvrApiProfile] = None,
) -> tuple[Optional[float], Optional[float], Optional[float], int, int]:
    """max CPU %, avg CPU %, sum DataRate Mbps, zero-bitrate IP channels (без analog)."""
    active = [ch for ch in channels if channel_is_active(ch)]
    cpus = [ch.cpu_usage for ch in active if ch.cpu_usage is not None]
    rates = [ch.data_rate for ch in active if ch.data_rate is not None]
    zero_bitrate = sum(
        1
        for ch in active
        if not is_analog_channel(ch)
        and ch.data_rate is not None
        and ch.data_rate <= 0
    )
    cpu_max = max(cpus) if cpus else None
    cpu_avg = round(sum(cpus) / len(cpus), 2) if cpus else None
    rate_sum = round(sum(rates), 3) if rates else None
    return cpu_max, cpu_avg, rate_sum, zero_bitrate, 0


def _to_float(value) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip().replace(",", ".")
    if not text:
        return None
    m = _SIZE_UNIT_RE.match(text)
    if m:
        try:
            number = float(m.group(1))
        except ValueError:
            return None
        unit = (m.group(2) or "").upper()
        if unit in ("TB", "ТБ"):
            return number * 1024 * 1024
        if unit in ("GB", "ГБ"):
            return number * 1024
        if unit in ("MB", "МБ", "КБ", "KB"):
            return number
        return number
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


async def poll_recorder(
    recorder: Recorder,
    credentials: Credentials,
    *,
    include_inventory: bool = True,
    timeout: float = 20.0,
) -> RecorderPollData:
    """Опрос NVR по SUNAPI.

    include_inventory: детальный архив по каждому каналу (searchrecordingperiod).
    Состояние канала (videosource) запрашивается при каждом опросе.
    """
    result = RecorderPollData()
    if not credentials.username or not credentials.password:
        result.error = "Не заданы учётные данные API"
        return result

    url = build_deviceinfo_url(recorder)
    status, body, err = await _fetch(recorder, credentials, url, timeout)
    if err or status >= 400 or not body.strip():
        result.error = err or f"HTTP {status}"
        return result

    result.device = parse_deviceinfo_response(body)
    if not result.device.model and not result.device.device_type:
        result.error = "Не распознан ответ deviceinfo"
        return result

    result.online = True
    profile = NvrApiProfile.from_device(result.device)

    cam_url = build_url(recorder, "media.cgi", "cameraregister")
    st, b, _ = await _fetch(recorder, credentials, cam_url, timeout)
    cam_channels: list[ChannelInfo] = []
    if st == 200:
        cam_channels = parse_cameraregister(b)

    vs_channels: list[ChannelInfo] = []
    vs_url = build_url(recorder, "media.cgi", "videosource")
    st, b, _ = await _fetch(recorder, credentials, vs_url, timeout)
    if st == 200:
        vs_channels = parse_videosource_channels(b)

    if cam_channels or vs_channels:
        result.channels = merge_channels(cam_channels, vs_channels)
        result.channels_polled = True
        (
            result.cpu_usage_max,
            result.cpu_usage_avg,
            result.data_rate_total_mbps,
            result.channels_zero_bitrate,
            result.channels_poe_off,
        ) = compute_stream_metrics(result.channels, profile=profile)

    storage_url = build_url(recorder, "system.cgi", "storageinfo")
    st, b, _ = await _fetch(recorder, credentials, storage_url, timeout)
    device_model = result.device.model if result.device else None
    if st == 200:
        if parse_sunapi_error_body(b):
            result.storage = StorageInfo(storageinfo_ok=False)
        else:
            result.storage = parse_storage(
                b, model=device_model, profile=profile
            )
            result.storage.storageinfo_ok = True
            if result.storage.disks:
                result.storage.disks = await enrich_storage_disk_metrics(
                    recorder,
                    credentials,
                    result.storage.disks,
                    device_model=device_model,
                    profile=profile,
                    timeout=timeout,
                )

    date_url = build_url(recorder, "system.cgi", "date")
    st, b, _ = await _fetch(recorder, credentials, date_url, timeout)
    if st == 200:
        result.date_time = parse_date(b)

    period_url = build_url(recorder, "recording.cgi", "searchrecordingperiod")
    st, b, _ = await _fetch(recorder, credentials, period_url, timeout)
    if st == 200:
        period_err = parse_sunapi_error_body(b)
        if period_err:
            result.recording_period_error = period_err
        else:
            result.recording_period = parse_recording_period(b)

    rec_storage_url = build_url(recorder, "recording.cgi", "storage")
    st, b, _ = await _fetch(recorder, credentials, rec_storage_url, timeout)
    if st == 200 and not parse_sunapi_error_body(b):
        enable, overwrite = parse_recording_storage(b)
        result.recording_storage_enable = enable
        result.recording_storage_overwrite = overwrite

    if result.channels:
        result.channel_recording_periods = await fetch_channel_recording_periods(
            recorder,
            credentials,
            [ch.channel_no for ch in result.channels],
            result.recording_period,
            timeout=timeout,
            detailed_archive=include_inventory,
        )

    event_url = build_url(recorder, "eventstatus.cgi", "eventstatus", action="check")
    st, b, _ = await _fetch(recorder, credentials, event_url, timeout)
    if st == 200:
        event_result = parse_eventstatus(b)
        result.events = event_result.channels
        result.system_events = event_result.system_events

    return result


async def fetch_systemlog_for_day(
    recorder: Recorder,
    credentials: Credentials,
    day_iso: str,
    *,
    timeout: float = 20.0,
) -> str:
    """systemlog за один день (FromDate=ToDate=day_iso)."""
    url = build_url(
        recorder,
        "system.cgi",
        "systemlog",
        action="view",
        FromDate=day_iso,
        ToDate=day_iso,
    )
    status, body, err = await _fetch(recorder, credentials, url, timeout)
    if status != 200 or err:
        return ""
    if parse_sunapi_error_body(body):
        return ""
    return body


def nvr_local_date_iso(poll: RecorderPollData) -> str:
    """Локальная дата NVR YYYY-MM-DD для systemlog FromDate/ToDate."""
    if poll.date_time and poll.date_time.local_time:
        return poll.date_time.local_time.strip()[:10]
    from .display_time import get_display_tz

    return datetime.now(get_display_tz()).date().isoformat()


async def scan_last_record_frame_drop_timestamp(
    recorder: Recorder,
    credentials: Credentials,
    *,
    end_date: str,
    scan_days: int = RECORD_FRAME_DROP_SCAN_DAYS,
    timeout: float = 20.0,
) -> Optional[str]:
    """Посуточный поиск последнего RecordFrameDrop, от end_date назад."""
    if scan_days <= 0:
        return None
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    for offset in range(scan_days + 1):
        day_iso = (end - timedelta(days=offset)).isoformat()
        body = await fetch_systemlog_for_day(
            recorder, credentials, day_iso, timeout=timeout
        )
        if not body:
            continue
        if find_frame_drop_lines(body):
            return parse_systemlog_latest_timestamp(body, RECORD_FRAME_DROP_LOG_TYPE)
    return None
