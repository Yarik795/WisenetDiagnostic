from __future__ import annotations

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
    skew_seconds: Optional[float] = None


@dataclass
class RecordingPeriodInfo:
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    archive_days: Optional[float] = None


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
            info.disks = storages
            info.worst_status = _worst_disk_status(storages)
        return info

    fields = parse_key_value_body(body)
    info.used_space_mb = _to_float(fields.get("UsedSpace"))
    info.total_space_mb = _to_float(fields.get("TotalSpace"))
    if info.used_space_mb is not None and info.total_space_mb and info.total_space_mb > 0:
        info.used_percent = round(info.used_space_mb / info.total_space_mb * 100, 1)
    disks = parse_storage_indexed(fields)
    info.disks = disks
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


def parse_date(body: str) -> DateTimeInfo:
    data = try_parse_json(body)
    info = DateTimeInfo()
    if isinstance(data, dict):
        info.local_time = data.get("LocalTime")
        info.utc_time = data.get("UTCTime")
        info.sync_type = data.get("SyncType")
        info.ntp_status = data.get("NTPStatus")
    else:
        fields = parse_key_value_body(body)
        info.local_time = fields.get("LocalTime")
        info.utc_time = fields.get("UTCTime")
        info.sync_type = fields.get("SyncType")
        info.ntp_status = fields.get("NTPStatus")

    ref = info.utc_time or info.local_time
    if ref:
        dt = parse_datetime_local(ref.replace("T", " "))
        if dt:
            now = datetime.now(timezone.utc)
            local_utc = dt.replace(tzinfo=timezone.utc)
            info.skew_seconds = abs((now - local_utc).total_seconds())
    return info


def parse_recording_period(body: str) -> RecordingPeriodInfo:
    fields = parse_key_value_body(body)
    data = try_parse_json(body)
    info = RecordingPeriodInfo()
    if isinstance(data, dict):
        info.start_time = data.get("StartTime")
        info.end_time = data.get("EndTime")
    else:
        info.start_time = fields.get("StartTime")
        info.end_time = fields.get("EndTime")

    start = info.start_time
    end = info.end_time
    if start and end:
        ds = parse_datetime_local(start.replace("T", " "))
        de = parse_datetime_local(end.replace("T", " "))
        if ds and de and de > ds:
            info.archive_days = (de - ds).total_seconds() / 86400
    return info


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

    date_url = build_url(recorder, "system.cgi", "date")
    st, b, _ = await _fetch(recorder, credentials, date_url, timeout)
    if st == 200:
        result.date_time = parse_date(b)

    period_url = build_url(recorder, "recording.cgi", "searchrecordingperiod")
    st, b, _ = await _fetch(recorder, credentials, period_url, timeout)
    if st == 200:
        result.recording_period = parse_recording_period(b)

    event_url = build_url(recorder, "eventstatus.cgi", "eventstatus", action="check")
    st, b, _ = await _fetch(recorder, credentials, event_url, timeout)
    if st == 200:
        result.events = parse_eventstatus(b)

    return result
