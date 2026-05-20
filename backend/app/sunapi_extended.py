from __future__ import annotations

import asyncio
import html
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
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
class RecorderPollData:
    device: Optional[DeviceInfo] = None
    online: bool = False
    error: Optional[str] = None
    storage: Optional[StorageInfo] = None
    date_time: Optional[DateTimeInfo] = None
    recording_period: Optional[RecordingPeriodInfo] = None
    channel_recording_periods: dict[int, RecordingPeriodInfo] = field(
        default_factory=dict
    )
    channels: list[ChannelInfo] = field(default_factory=list)
    events: list[EventChannelStatus] = field(default_factory=list)


def build_base_url(recorder: Recorder, cgi: str) -> str:
    scheme = "https" if recorder.use_https else "http"
    return f"{scheme}://{recorder.host}:{recorder.port}/stw-cgi/{cgi}"


def build_url(recorder: Recorder, cgi: str, submenu: str, action: str = "view", **params: str) -> str:
    base = build_base_url(recorder, cgi)
    query: dict[str, str] = {"msubmenu": submenu, "action": action, **params}
    return f"{base}?{urlencode(query)}"


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
            channels.append(
                ChannelInfo(
                    channel_no=int(ch),
                    camera_ip=item.get("IPAddress"),
                    camera_model=item.get("Model"),
                    register_status=item.get("Status"),
                    name=item.get("Model"),
                )
            )
        return channels
    return []


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


def extract_disk_temperature(disk: dict) -> Optional[str]:
    """Температура из storageinfo: плоские поля, Health или SMART.Attributes."""
    for key in ("TemperatureCelsius", "temperature_celsius"):
        val = disk.get(key)
        if val is not None and str(val).strip() != "":
            return f"{val} °C"

    for key in ("Temperature", "temperature"):
        val = disk.get(key)
        if val is not None and str(val).strip() != "":
            return str(val).strip()

    for key in ("TemperatureInCelsius", "temperature_in_celsius"):
        val = disk.get(key)
        if val is not None and str(val).strip() != "":
            return f"{val} °C"

    health = disk.get("Health")
    if isinstance(health, dict):
        t = health.get("TemperatureInCelsius")
        if t is not None:
            return f"{t} °C"

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
                        return f"{val} °C"
    return None


def normalize_disk_record(disk: dict) -> dict:
    out = dict(disk)
    temp = extract_disk_temperature(disk)
    if temp:
        out["Temperature"] = temp
    return out


def normalize_storage_disks(disks: list[dict]) -> list[dict]:
    return [normalize_disk_record(d) for d in disks]


_TEMPERATURE_SMART_RE = re.compile(
    r"Temperature\s*:\s*(\d+)\s*(?:&#?\d+;|\u00b0|\°)?\s*C?",
    re.IGNORECASE,
)


def parse_temperature_from_smart(text: str) -> Optional[str]:
    if not text:
        return None
    plain = html.unescape(text)
    plain = re.sub(r"<[^>]+>", " ", plain)
    m = _TEMPERATURE_SMART_RE.search(plain)
    if m:
        return f"{m.group(1)} °C"
    return None


def parse_diskutility_list(body: str) -> list[dict]:
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
            temp = parse_temperature_from_smart(value)
            if temp:
                disks[idx]["Temperature"] = temp
    return [
        disks[k]
        for k in sorted(disks)
        if disks[k].get("Index") is not None
    ]


def parse_diskutility_detail(body: str) -> dict:
    data = try_parse_json(body)
    if isinstance(data, dict) and isinstance(data.get("Disks"), list) and data["Disks"]:
        item = data["Disks"][0]
        if isinstance(item, dict):
            smart = item.get("SMART") or ""
            temp = parse_temperature_from_smart(str(smart))
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
            temp = parse_temperature_from_smart(value)
            if temp:
                result["Temperature"] = temp
    return result


def merge_disk_temperatures(
    storage_disks: list[dict],
    utility_disks: list[dict],
) -> list[dict]:
    enriched = normalize_storage_disks(storage_disks)
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
    timeout: float = 20.0,
    max_detail_fetches: int = 16,
) -> list[dict]:
    normalized = normalize_storage_disks(disks)
    if normalized and all(d.get("Temperature") for d in normalized):
        return normalized

    list_url = build_url(recorder, "recording.cgi", "diskutility")
    status, body, _ = await _fetch(recorder, credentials, list_url, timeout)
    if status != 200 or not body.strip():
        return normalized

    utility_disks = parse_diskutility_list(body)
    missing_temp = [u for u in utility_disks if not u.get("Temperature")]

    if missing_temp and len(missing_temp) <= max_detail_fetches:

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
            return parse_diskutility_detail(detail_body)

        indices = [u["Index"] for u in missing_temp[:max_detail_fetches]]
        details = await asyncio.gather(*(fetch_one(i) for i in indices))
        by_index = {d.get("Index"): d for d in details if d.get("Index") is not None}
        for u in utility_disks:
            if u.get("Temperature"):
                continue
            detail = by_index.get(u.get("Index"))
            if detail and detail.get("Temperature"):
                u["Temperature"] = detail["Temperature"]

    return merge_disk_temperatures(normalized, utility_disks)


def parse_storage(body: str) -> StorageInfo:
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
            info.disks = normalize_storage_disks(storages)
            info.worst_status = _worst_disk_status(storages)
        return info

    fields = parse_key_value_body(body)
    info.used_space_mb = _to_float(fields.get("UsedSpace"))
    info.total_space_mb = _to_float(fields.get("TotalSpace"))
    if info.used_space_mb is not None and info.total_space_mb and info.total_space_mb > 0:
        info.used_percent = round(info.used_space_mb / info.total_space_mb * 100, 1)
    disks = parse_storage_indexed(fields)
    info.disks = normalize_storage_disks(disks)
    info.worst_status = _worst_disk_status(disks)
    return info


def _worst_disk_status(disks: list[dict]) -> Optional[str]:
    error_states = {"Error", "Fail", "Formatting", "Lock", "Full", "PWError"}
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


async def enable_recorder_ntp(
    recorder: Recorder,
    credentials: Credentials,
    ntp_server: str,
    *,
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

    set_url = build_url(
        recorder,
        "system.cgi",
        "date",
        action="set",
        SyncType="NTP",
        NTPURLList=server,
    )
    status, body, err = await _fetch(recorder, credentials, set_url, timeout)
    if err:
        return EnableNtpResult(success=False, error=err)
    if status >= 400:
        return EnableNtpResult(success=False, error=f"HTTP {status}")
    if not is_sunapi_set_success(body):
        snippet = (body or "").strip()[:300]
        return EnableNtpResult(
            success=False,
            error=snippet or "Устройство не подтвердило смену режима синхронизации",
        )

    date_info, view_err = await fetch_date_info(recorder, credentials, timeout=timeout)
    if view_err:
        return EnableNtpResult(
            success=False,
            error=f"Режим применён, но не удалось проверить: {view_err}",
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


async def fetch_channel_recording_periods(
    recorder: Recorder,
    credentials: Credentials,
    channel_nos: list[int],
    global_period: Optional[RecordingPeriodInfo],
    *,
    timeout: float = 20.0,
    max_channels: int = 64,
    max_concurrent: int = 8,
) -> dict[int, RecordingPeriodInfo]:
    if not channel_nos:
        return {}

    sem = asyncio.Semaphore(max_concurrent)
    nos = channel_nos[:max_channels]

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
        elif global_period and _period_has_archive_data(global_period):
            periods[ch_no] = RecordingPeriodInfo(
                start_time=global_period.start_time,
                end_time=global_period.end_time,
                archive_days=global_period.archive_days,
                channel_no=ch_no,
            )
    return periods


def parse_eventstatus(body: str) -> list[EventChannelStatus]:
    fields = parse_key_value_body(body)
    channels: dict[int, EventChannelStatus] = {}
    pattern = re.compile(r"^Channel\.(\d+)\.(.+)$")
    for key, value in fields.items():
        m = pattern.match(key)
        if not m:
            continue
        ch = int(m.group(1))
        attr = m.group(2)
        channels.setdefault(ch, EventChannelStatus(channel_no=ch))
        if attr.lower() == "videoloss":
            channels[ch].video_loss = value.lower() == "true"
        elif attr == "Connected":
            channels[ch].connected = value.lower() == "true"

    data = try_parse_json(body)
    if isinstance(data, dict) and "ChannelEvent" in data:
        for item in data["ChannelEvent"]:
            ch = item.get("Channel")
            if ch is None:
                continue
            ch = int(ch)
            channels.setdefault(ch, EventChannelStatus(channel_no=ch))
            for key, val in item.items():
                if key == "Channel":
                    continue
                if isinstance(val, bool):
                    if key.lower() == "videoloss":
                        channels[ch].video_loss = val
                    elif key == "Connected":
                        channels[ch].connected = val
    return [channels[k] for k in sorted(channels)]


def _to_float(value) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
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

    storage_url = build_url(recorder, "system.cgi", "storageinfo")
    st, b, _ = await _fetch(recorder, credentials, storage_url, timeout)
    if st == 200:
        result.storage = parse_storage(b)
        if result.storage and result.storage.disks:
            result.storage.disks = await enrich_storage_temperatures(
                recorder,
                credentials,
                result.storage.disks,
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
        )

    event_url = build_url(recorder, "eventstatus.cgi", "eventstatus", action="check")
    st, b, _ = await _fetch(recorder, credentials, event_url, timeout)
    if st == 200:
        result.events = parse_eventstatus(b)

    return result
