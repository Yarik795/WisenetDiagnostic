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
from .sunapi_parsing import (
    parse_channel_indexed,
    parse_datetime_local,
    parse_key_value_body,
    parse_storage_indexed,
    try_parse_json,
)

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

_CGI_VERSION_RE = re.compile(r"(\d+)\.(\d+)")
_SIZE_UNIT_RE = re.compile(
    r"^([\d.,]+)\s*(TB|GB|MB|КБ|МБ|ТБ)?$",
    re.IGNORECASE,
)
_DISKUTILITY_ERROR_MARKERS = ("NG", "Error Code:", "Submenu Not Found")
_REGISTER_STATUS_ERROR = frozenset(
    {"connectfail", "disconnected", "fail", "failed", "error"}
)


def normalize_register_status(status: Optional[str]) -> str:
    if not status:
        return ""
    return status.strip().lower().replace(" ", "").replace("_", "")


def is_register_status_error(status: Optional[str]) -> bool:
    return normalize_register_status(status) in _REGISTER_STATUS_ERROR

_COMBINED_TEMP_RE = re.compile(
    r"^(\d+)\s*(?:&#?\d+;|\u00b0|\°|.)?\s*C",
    re.IGNORECASE,
)


@dataclass
class ChannelInfo:
    channel_no: int
    name: Optional[str] = None
    source_state: Optional[str] = None
    camera_ip: Optional[str] = None
    camera_model: Optional[str] = None
    register_status: Optional[str] = None


@dataclass
class StorageInfo:
    used_space_mb: Optional[float] = None
    total_space_mb: Optional[float] = None
    used_percent: Optional[float] = None
    disks: list[dict] = field(default_factory=list)
    worst_status: Optional[str] = None


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

        return cls(
            model=model or None,
            cgi_version=cgi_ver,
            supports_diskutility=supports_diskutility,
            celsius_only_temperature=celsius_only,
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


def parse_cameraregister(body: str) -> list[ChannelInfo]:
    data = try_parse_json(body)
    if isinstance(data, dict) and "RegisteredCameras" in data:
        channels = []
        for item in data["RegisteredCameras"]:
            ch = item.get("Channel")
            if ch is None:
                continue
            name = item.get("Title") or item.get("Name") or item.get("Model")
            channels.append(
                ChannelInfo(
                    channel_no=int(ch),
                    camera_ip=item.get("IPAddress"),
                    camera_model=item.get("Model"),
                    register_status=item.get("Status"),
                    name=name,
                )
            )
        return channels

    fields = parse_key_value_body(body)
    indexed = parse_channel_indexed(fields, "Channel")
    channels = []
    for ch, attrs in sorted(indexed.items()):
        name = attrs.get("Title") or attrs.get("Name") or attrs.get("Model")
        channels.append(
            ChannelInfo(
                channel_no=ch,
                camera_ip=attrs.get("IPAddress"),
                camera_model=attrs.get("Model"),
                register_status=attrs.get("Status"),
                name=name,
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
                "camera_ip",
                "camera_model",
                "register_status",
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
            temp = parse_temperature_from_smart(value, model=model)
            if temp:
                disks[idx]["Temperature"] = temp
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
            temp = parse_temperature_from_smart(str(smart), model=model)
            return {
                "Index": item.get("Index"),
                "Name": (item.get("Name") or "").strip(),
                "Temperature": temp,
            }

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
            temp = parse_temperature_from_smart(value, model=model)
            if temp:
                result["Temperature"] = temp
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
    normalized = normalize_storage_disks(
        disks, model=device_model, profile=profile
    )
    if normalized and all(d.get("Temperature") for d in normalized):
        return normalized

    if profile is not None and not profile.supports_diskutility:
        return normalized

    list_url = build_url(recorder, "recording.cgi", "diskutility")
    status, body, _ = await _fetch(recorder, credentials, list_url, timeout)
    if status != 200 or not body.strip() or _is_diskutility_error(body):
        return normalized

    utility_disks = parse_diskutility_list(body, model=device_model)
    still_missing_storage = any(not d.get("Temperature") for d in normalized)
    missing_temp = [
        u for u in utility_disks if not u.get("Temperature")
    ]

    if (
        still_missing_storage
        and missing_temp
        and len(missing_temp) <= max_detail_fetches
    ):

        async def fetch_one(index) -> dict:
            detail_url = build_url(
                recorder,
                "recording.cgi",
                "diskutility",
                Index=str(index),
            )
            st, detail_body, _ = await _fetch(
                recorder, credentials, detail_url, timeout
            )
            if st != 200:
                return {"Index": index}
            return parse_diskutility_detail(detail_body, model=device_model)

        indices = [u["Index"] for u in missing_temp[:max_detail_fetches]]
        details = await asyncio.gather(*(fetch_one(i) for i in indices))
        by_index = {d.get("Index"): d for d in details if d.get("Index") is not None}
        for u in utility_disks:
            if u.get("Temperature"):
                continue
            detail = by_index.get(u.get("Index"))
            if detail and detail.get("Temperature"):
                u["Temperature"] = detail["Temperature"]

    return merge_disk_temperatures(normalized, utility_disks, model=device_model)


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
        return info

    fields = parse_key_value_body(body)
    info.used_space_mb = _to_float(fields.get("UsedSpace"))
    info.total_space_mb = _to_float(fields.get("TotalSpace"))
    if info.used_space_mb is not None and info.total_space_mb and info.total_space_mb > 0:
        info.used_percent = round(info.used_space_mb / info.total_space_mb * 100, 1)
    disks = parse_storage_indexed(fields)
    info.disks = normalize_storage_disks(disks, model=model, profile=profile)
    info.worst_status = _worst_disk_status(disks)
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

    if include_inventory:
        cam_url = build_url(recorder, "media.cgi", "cameraregister")
        st, b, _ = await _fetch(recorder, credentials, cam_url, timeout)
        cam_channels: list[ChannelInfo] = []
        if st == 200:
            cam_channels = parse_cameraregister(b)

        vs_url = build_url(recorder, "media.cgi", "videosource")
        st, b, _ = await _fetch(recorder, credentials, vs_url, timeout)
        vs_channels: list[ChannelInfo] = []
        if st == 200:
            vs_channels = parse_videosource_channels(b)

        result.channels = merge_channels(cam_channels, vs_channels)
        result.channels_polled = True

    storage_url = build_url(recorder, "system.cgi", "storageinfo")
    st, b, _ = await _fetch(recorder, credentials, storage_url, timeout)
    device_model = result.device.model if result.device else None
    if st == 200:
        result.storage = parse_storage(
            b, model=device_model, profile=profile
        )
        if result.storage and result.storage.disks:
            result.storage.disks = await enrich_storage_temperatures(
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
        result.recording_period = parse_recording_period(b)

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
