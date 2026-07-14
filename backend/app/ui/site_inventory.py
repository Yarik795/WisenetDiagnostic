"""Отчёт «Устройства на объекте»: реальные устройства ТСВ vs CMDB."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Literal, Optional

from ..config_store import ConfigStore
from ..device_kinds import filter_recorders_by_kind
from ..models import Recorder
from ..state_store import ChannelRow, CmdbRecordRow, RecorderMetricsRow, StateStore
from .grouping import STATUS_LABELS, metrics_map_from_list

MatchStatus = Literal["ok", "extra", "missing", "info"]

CMDB_TYPE_NVR = "Видеорегистраторы"
CMDB_TYPE_CAMERA = "Видеокамеры"
CMDB_TYPE_AUX = "Вспомогательное оборудование"

MATCH_LABELS: dict[str, str] = {
    "ok": "Совпадает с CMDB",
    "extra": "Нет в CMDB",
    "missing": "Не найдено при опросе",
    "info": "Информационно",
}


@dataclass
class SiteObjectGroup:
    object_name: str
    nvrs: list[dict[str, Any]] = field(default_factory=list)
    ip_cameras: list[dict[str, Any]] = field(default_factory=list)
    analog_cameras: list[dict[str, Any]] = field(default_factory=list)
    auxiliary: list[dict[str, Any]] = field(default_factory=list)
    missing: list[dict[str, Any]] = field(default_factory=list)

    @property
    def has_content(self) -> bool:
        return bool(
            self.nvrs
            or self.ip_cameras
            or self.analog_cameras
            or self.auxiliary
            or self.missing
        )

    @property
    def device_count(self) -> int:
        return (
            len(self.nvrs)
            + len(self.ip_cameras)
            + len(self.analog_cameras)
            + len(self.auxiliary)
            + len(self.missing)
        )


def normalize_ip(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def normalize_object_name(value: Optional[str]) -> str:
    return (value or "").strip() or "— Без объекта —"


def is_channel_deactive(channel: ChannelRow) -> bool:
    return (channel.source_state or "").strip().lower() == "deactive"


def is_analog_channel(channel: ChannelRow) -> bool:
    if normalize_ip(channel.camera_ip):
        return False
    state = (channel.source_state or "").strip().lower()
    if state == "deactive":
        return False
    if state:
        return True
    return bool((channel.name or "").strip())


def _find_cmdb_by_ip(
    cmdb_rows: list[CmdbRecordRow],
    host: str,
    functional_type: str,
) -> Optional[CmdbRecordRow]:
    ip = normalize_ip(host)
    if not ip:
        return None
    for row in cmdb_rows:
        if normalize_ip(row.host) == ip and row.functional_type == functional_type:
            return row
    return None


def _device_row(
    *,
    device_type: str,
    device_type_label: str,
    match_status: MatchStatus,
    name: str = "",
    host: str = "",
    model: str = "",
    manufacturer: str = "",
    mac: str = "",
    channel_no: Optional[int] = None,
    recorder_name: str = "",
    recorder_host: str = "",
    health_status: str = "",
    health_label: str = "",
    source_state: str = "",
    cmdb_model: str = "",
    cmdb_mac: str = "",
    note: str = "",
) -> dict[str, Any]:
    return {
        "device_type": device_type,
        "device_type_label": device_type_label,
        "match_status": match_status,
        "match_label": MATCH_LABELS.get(match_status, match_status),
        "name": name,
        "host": host,
        "model": model,
        "manufacturer": manufacturer,
        "mac": mac,
        "channel_no": channel_no,
        "recorder_name": recorder_name,
        "recorder_host": recorder_host,
        "health_status": health_status,
        "health_label": health_label,
        "source_state": source_state,
        "cmdb_model": cmdb_model,
        "cmdb_mac": cmdb_mac,
        "note": note,
    }


def _nvr_row(
    recorder: Recorder,
    metrics: Optional[RecorderMetricsRow],
    cmdb: Optional[CmdbRecordRow],
) -> dict[str, Any]:
    match_status: MatchStatus = "ok" if cmdb else "extra"
    health = metrics.health_status if metrics and metrics.last_polled_at else "unknown"
    return _device_row(
        device_type="nvr",
        device_type_label="Видеорегистратор",
        match_status=match_status,
        name=recorder.name or recorder.host,
        host=recorder.host,
        model=(metrics.model if metrics else None) or "",
        manufacturer=cmdb.manufacturer if cmdb else "",
        mac=recorder.mac or (cmdb.mac if cmdb else "") or "",
        health_status=health,
        health_label=STATUS_LABELS.get(health, health),
        cmdb_model=cmdb.model_name if cmdb else "",
        cmdb_mac=cmdb.mac if cmdb else "",
    )


def _ip_camera_row(
    channel: ChannelRow,
    recorder: Recorder,
    cmdb: Optional[CmdbRecordRow],
) -> dict[str, Any]:
    match_status: MatchStatus = "ok" if cmdb else "extra"
    return _device_row(
        device_type="ip_camera",
        device_type_label="IP-камера",
        match_status=match_status,
        name=channel.name or f"Канал {channel.channel_no + 1}",
        host=channel.camera_ip or "",
        model=channel.camera_model or "",
        manufacturer=cmdb.manufacturer if cmdb else "",
        mac=cmdb.mac if cmdb else "",
        channel_no=channel.channel_no,
        recorder_name=recorder.name or recorder.host,
        recorder_host=recorder.host,
        health_status=channel.health_status,
        health_label=STATUS_LABELS.get(channel.health_status, channel.health_status),
        source_state=channel.source_state or "",
        cmdb_model=cmdb.model_name if cmdb else "",
        cmdb_mac=cmdb.mac if cmdb else "",
    )


def _analog_camera_row(channel: ChannelRow, recorder: Recorder) -> dict[str, Any]:
    return _device_row(
        device_type="analog_camera",
        device_type_label="Аналоговая камера",
        match_status="info",
        name=channel.name or f"Канал {channel.channel_no + 1}",
        channel_no=channel.channel_no,
        recorder_name=recorder.name or recorder.host,
        recorder_host=recorder.host,
        health_status=channel.health_status,
        health_label=STATUS_LABELS.get(channel.health_status, channel.health_status),
        source_state=channel.source_state or "",
        note="Без IP — сопоставление с CMDB недоступно",
    )


def _cmdb_row(
    row: CmdbRecordRow,
    *,
    match_status: MatchStatus,
    note: str = "",
) -> dict[str, Any]:
    type_labels = {
        CMDB_TYPE_NVR: "Видеорегистратор",
        CMDB_TYPE_CAMERA: "Видеокамера",
        CMDB_TYPE_AUX: "Вспомогательное",
    }
    return _device_row(
        device_type="cmdb",
        device_type_label=type_labels.get(row.functional_type, row.functional_type),
        match_status=match_status,
        name=row.model_name or row.host,
        host=row.host,
        model=row.model_name,
        manufacturer=row.manufacturer,
        mac=row.mac or "",
        cmdb_model=row.model_name,
        cmdb_mac=row.mac or "",
        note=note,
    )


def build_site_object_groups(
    store: ConfigStore,
    state: StateStore,
) -> list[SiteObjectGroup]:
    tsv_recorders = filter_recorders_by_kind(store.list_recorders(), "tsv")
    metrics_map = metrics_map_from_list(state.list_recorder_metrics())
    cmdb_rows = state.cmdb_records_rows()

    channels_by_recorder: dict[str, list[ChannelRow]] = defaultdict(list)
    for channel in state.list_channels():
        channels_by_recorder[channel.recorder_id].append(channel)

    groups_map: dict[str, SiteObjectGroup] = {}
    found_nvr_ips: set[str] = set()
    found_camera_ips: set[str] = set()

    def get_group(object_name: str) -> SiteObjectGroup:
        key = normalize_object_name(object_name)
        if key not in groups_map:
            groups_map[key] = SiteObjectGroup(object_name=key)
        return groups_map[key]

    for recorder in tsv_recorders:
        object_name = normalize_object_name(recorder.object_name)
        group = get_group(object_name)
        metrics = metrics_map.get(recorder.id)
        host_ip = normalize_ip(recorder.host)
        if host_ip:
            found_nvr_ips.add(host_ip)
        cmdb = _find_cmdb_by_ip(cmdb_rows, recorder.host, CMDB_TYPE_NVR)
        group.nvrs.append(_nvr_row(recorder, metrics, cmdb))

        for channel in channels_by_recorder.get(recorder.id, []):
            if is_channel_deactive(channel):
                continue
            if normalize_ip(channel.camera_ip):
                cam_ip = normalize_ip(channel.camera_ip)
                found_camera_ips.add(cam_ip)
                cam_cmdb = _find_cmdb_by_ip(cmdb_rows, channel.camera_ip or "", CMDB_TYPE_CAMERA)
                group.ip_cameras.append(_ip_camera_row(channel, recorder, cam_cmdb))
            elif is_analog_channel(channel):
                group.analog_cameras.append(_analog_camera_row(channel, recorder))

    for row in cmdb_rows:
        object_name = normalize_object_name(row.object_name)
        group = get_group(object_name)
        host_ip = normalize_ip(row.host)

        if row.functional_type == CMDB_TYPE_AUX:
            group.auxiliary.append(
                _cmdb_row(
                    row,
                    match_status="info",
                    note="Проверить наличие на объекте",
                )
            )
            continue

        if row.functional_type == CMDB_TYPE_NVR:
            if host_ip and host_ip not in found_nvr_ips:
                group.missing.append(
                    _cmdb_row(
                        row,
                        match_status="missing",
                        note="Вероятно, не добавлен в мониторинг или недоступен",
                    )
                )
            continue

        if row.functional_type == CMDB_TYPE_CAMERA:
            if host_ip and host_ip not in found_camera_ips:
                group.missing.append(
                    _cmdb_row(
                        row,
                        match_status="missing",
                        note="Вероятно, не добавлена ни на один регистратор",
                    )
                )

    groups = [g for g in groups_map.values() if g.has_content]
    groups.sort(key=lambda g: g.object_name.lower())
    return groups


def _filter_groups(groups: list[SiteObjectGroup], search: str) -> list[SiteObjectGroup]:
    q = search.strip().lower()
    if not q:
        return groups

    def row_matches(row: dict[str, Any]) -> bool:
        haystack = " ".join(
            str(row.get(key, "") or "")
            for key in (
                "name",
                "host",
                "model",
                "manufacturer",
                "recorder_name",
                "recorder_host",
                "note",
                "device_type_label",
            )
        ).lower()
        return q in haystack

    filtered: list[SiteObjectGroup] = []
    for group in groups:
        if q in group.object_name.lower():
            filtered.append(group)
            continue
        subset = SiteObjectGroup(object_name=group.object_name)
        for collection, attr in (
            (group.nvrs, "nvrs"),
            (group.ip_cameras, "ip_cameras"),
            (group.analog_cameras, "analog_cameras"),
            (group.auxiliary, "auxiliary"),
            (group.missing, "missing"),
        ):
            matched = [row for row in collection if row_matches(row)]
            setattr(subset, attr, matched)
        if subset.has_content:
            filtered.append(subset)
    return filtered


def _build_kpi(groups: list[SiteObjectGroup]) -> dict[str, int]:
    kpi = {
        "objects": len(groups),
        "real_total": 0,
        "matched_ok": 0,
        "extra": 0,
        "analog": 0,
        "auxiliary": 0,
        "missing": 0,
    }
    for group in groups:
        for row in group.nvrs + group.ip_cameras:
            kpi["real_total"] += 1
            if row["match_status"] == "ok":
                kpi["matched_ok"] += 1
            elif row["match_status"] == "extra":
                kpi["extra"] += 1
        kpi["analog"] += len(group.analog_cameras)
        kpi["auxiliary"] += len(group.auxiliary)
        kpi["missing"] += len(group.missing)
    return kpi


def _apply_ping_results_to_groups(
    groups: list[SiteObjectGroup],
    ping_results: dict[str, dict[str, Any]],
) -> None:
    for group in groups:
        for row in group.missing:
            ip = normalize_ip(row.get("host"))
            entry = ping_results.get(ip) if ip else None
            if not entry:
                row["ping_status"] = ""
                row["ping_label"] = ""
                row["ping_rtt"] = None
                row["ping_error"] = ""
                continue
            if entry.get("reachable"):
                row["ping_status"] = "ok"
                rtt = entry.get("rtt_ms")
                row["ping_label"] = f"Доступен{f' ({rtt:.0f} мс)' if rtt is not None else ''}"
                row["ping_rtt"] = rtt
                row["ping_error"] = ""
            else:
                row["ping_status"] = "error"
                row["ping_label"] = "Недоступен"
                row["ping_rtt"] = None
                row["ping_error"] = entry.get("error") or ""


def _count_zombies(groups: list[SiteObjectGroup]) -> int:
    return sum(len(group.missing) for group in groups)


def site_devices_page_context(
    store: ConfigStore,
    state: StateStore,
    *,
    search: str = "",
    ping_results: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    all_groups = build_site_object_groups(store, state)
    zombie_count = _count_zombies(all_groups)
    results = ping_results or {}
    _apply_ping_results_to_groups(all_groups, results)
    groups = _filter_groups(all_groups, search)
    if search:
        _apply_ping_results_to_groups(groups, results)
    kpi = _build_kpi(groups)
    has_data = bool(all_groups)
    return {
        "site_devices_search": search,
        "site_devices_has_data": has_data,
        "site_devices_groups": groups,
        "site_devices_kpi": kpi,
        "site_devices_zombie_count": zombie_count,
    }
