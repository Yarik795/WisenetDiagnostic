"""Отчёт «Конфигурации NVR/SPD»: выгрузка configbackup по объектам."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional

from ..config_backup import ConfigBackupTarget
from ..config_store import ConfigStore
from ..device_kinds import filter_recorders_by_kind
from ..models import Credentials, Recorder
from ..state_store import CmdbRecordRow, StateStore
from ..ui.helpers import display_recorder_name
from .site_inventory import normalize_object_name

DeviceKind = Literal["nvr", "spd"]

KIND_LABELS: dict[DeviceKind, str] = {
    "nvr": "Регистратор",
    "spd": "SPD",
}


@dataclass
class ConfigDeviceRow:
    kind: DeviceKind
    kind_label: str
    host: str
    port: int
    use_https: bool
    name: str
    model: str
    object_name: str

    def to_backup_target(self) -> ConfigBackupTarget:
        return ConfigBackupTarget(
            object_name=self.object_name,
            kind=self.kind,
            host=self.host,
            port=self.port,
            use_https=self.use_https,
        )


@dataclass
class DeviceConfigObjectGroup:
    object_name: str
    nvrs: list[ConfigDeviceRow] = field(default_factory=list)
    spd_devices: list[ConfigDeviceRow] = field(default_factory=list)

    @property
    def has_content(self) -> bool:
        return bool(self.nvrs or self.spd_devices)

    @property
    def device_count(self) -> int:
        return len(self.nvrs) + len(self.spd_devices)

    @property
    def all_devices(self) -> list[ConfigDeviceRow]:
        return [*self.nvrs, *self.spd_devices]


def is_spd_model(model_name: Optional[str]) -> bool:
    return (model_name or "").strip().upper().startswith("SPD")


def _nvr_row(recorder: Recorder) -> ConfigDeviceRow:
    object_name = normalize_object_name(recorder.object_name)
    return ConfigDeviceRow(
        kind="nvr",
        kind_label=KIND_LABELS["nvr"],
        host=recorder.host,
        port=recorder.port,
        use_https=recorder.use_https,
        name=display_recorder_name(recorder),
        model="",
        object_name=object_name,
    )


def _spd_row(row: CmdbRecordRow) -> ConfigDeviceRow:
    object_name = normalize_object_name(row.object_name)
    model = (row.model_name or "").strip()
    return ConfigDeviceRow(
        kind="spd",
        kind_label=KIND_LABELS["spd"],
        host=row.host,
        port=80,
        use_https=False,
        name=model or row.host,
        model=model,
        object_name=object_name,
    )


def build_device_config_groups(
    store: ConfigStore,
    state: StateStore,
) -> list[DeviceConfigObjectGroup]:
    groups_map: dict[str, DeviceConfigObjectGroup] = {}

    def get_group(object_name: str) -> DeviceConfigObjectGroup:
        key = normalize_object_name(object_name)
        if key not in groups_map:
            groups_map[key] = DeviceConfigObjectGroup(object_name=key)
        return groups_map[key]

    for recorder in filter_recorders_by_kind(store.list_recorders(), "tsv"):
        get_group(recorder.object_name).nvrs.append(_nvr_row(recorder))

    for row in state.cmdb_records_rows():
        if not is_spd_model(row.model_name):
            continue
        get_group(row.object_name).spd_devices.append(_spd_row(row))

    groups = [group for group in groups_map.values() if group.has_content]
    groups.sort(key=lambda group: group.object_name.lower())
    return groups


def _row_matches_search(row: ConfigDeviceRow, query: str) -> bool:
    haystack = " ".join(
        (
            row.kind_label,
            row.name,
            row.host,
            row.model,
            row.object_name,
        )
    ).lower()
    return query in haystack


def filter_device_config_groups(
    groups: list[DeviceConfigObjectGroup],
    search: str,
) -> list[DeviceConfigObjectGroup]:
    query = search.strip().lower()
    if not query:
        return groups

    filtered: list[DeviceConfigObjectGroup] = []
    for group in groups:
        if query in group.object_name.lower():
            filtered.append(group)
            continue

        subset = DeviceConfigObjectGroup(object_name=group.object_name)
        subset.nvrs = [row for row in group.nvrs if _row_matches_search(row, query)]
        subset.spd_devices = [
            row for row in group.spd_devices if _row_matches_search(row, query)
        ]
        if subset.has_content:
            filtered.append(subset)
    return filtered


def find_device_in_groups(
    groups: list[DeviceConfigObjectGroup],
    *,
    object_name: str,
    kind: DeviceKind,
    host: str,
) -> Optional[ConfigDeviceRow]:
    normalized_object = normalize_object_name(object_name)
    host_key = host.strip().lower()
    for group in groups:
        if group.object_name != normalized_object:
            continue
        devices = group.nvrs if kind == "nvr" else group.spd_devices
        for device in devices:
            if device.kind == kind and device.host.strip().lower() == host_key:
                return device
    return None


def resolve_object_devices(
    groups: list[DeviceConfigObjectGroup],
    object_name: str,
) -> list[ConfigDeviceRow]:
    normalized_object = normalize_object_name(object_name)
    for group in groups:
        if group.object_name == normalized_object:
            return group.all_devices
    return []


def device_configs_page_context(
    store: ConfigStore,
    state: StateStore,
    *,
    search: str = "",
) -> dict[str, Any]:
    all_groups = build_device_config_groups(store, state)
    groups = filter_device_config_groups(all_groups, search)
    device_total = sum(group.device_count for group in all_groups)
    return {
        "device_configs_search": search,
        "device_configs_has_data": device_total > 0,
        "device_configs_groups": groups,
        "device_configs_object_count": len(all_groups),
        "device_configs_device_count": device_total,
    }


def build_all_device_config_groups(
    store: ConfigStore,
    state: StateStore,
) -> list[DeviceConfigObjectGroup]:
    return build_device_config_groups(store, state)


def get_credentials(store: ConfigStore) -> Credentials:
    return store.load().credentials
