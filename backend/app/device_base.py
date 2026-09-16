"""Справочник «База устройств» и синхронизация регистраторов/СКУД в config.json."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Optional

from .config_store import ConfigStore
from .device_kinds import recorder_device_kind
from .models import Recorder, RecorderCreate, RecorderUpdate
from .state_store import DeviceBaseRow, StateStore

DeviceType = Literal["recorder", "locker", "skud_controller", "camera", "server"]

DEVICE_TYPES: tuple[DeviceType, ...] = (
    "recorder",
    "locker",
    "skud_controller",
    "camera",
    "server",
)

DEVICE_TYPE_LABELS: dict[str, str] = {
    "recorder": "Регистратор",
    "locker": "Локер",
    "skud_controller": "Контроллер СКУД",
    "camera": "Камера",
    "server": "Сервер",
}

LOCKER_MODELS: tuple[str, ...] = ("LockerBox", "Pridex")

MONITORED_TYPES: dict[str, str] = {
    "recorder": "tsv",
    "skud_controller": "skud",
    "locker": "lockers",
}

LOCKER_DEFAULT_PORT = 5555

IPV4_RE = re.compile(
    r"^(?:25[0-5]|2[0-4]\d|[01]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[01]?\d?\d)){3}$"
)


class DeviceBaseError(Exception):
    def __init__(self, message: str, *, field: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.field = field


@dataclass
class DeviceBaseFormData:
    address: str
    device_type: str
    model: str
    host: str


def device_type_label(device_type: str) -> str:
    return DEVICE_TYPE_LABELS.get(device_type, device_type)


def is_monitored_type(device_type: str) -> bool:
    return device_type in MONITORED_TYPES


def parse_device_base_form(
    address: str,
    device_type: str,
    model: str,
    host: str,
) -> tuple[Optional[DeviceBaseFormData], dict[str, str]]:
    errors: dict[str, str] = {}
    addr = address.strip()
    kind = device_type.strip()
    model_value = model.strip()
    ip = host.strip()

    if not addr:
        errors["address"] = "Укажите адрес"
    if kind not in DEVICE_TYPES:
        errors["device_type"] = "Выберите тип устройства"
        kind = "recorder"
    if not ip:
        errors["host"] = "Укажите IP-адрес"
    elif not IPV4_RE.match(ip):
        errors["host"] = "Некорректный IPv4-адрес"

    if kind == "locker":
        if model_value not in LOCKER_MODELS:
            errors["model"] = "Для локера выберите LockerBox или Pridex"
    else:
        model_value = ""

    if errors:
        return None, errors

    return (
        DeviceBaseFormData(
            address=addr,
            device_type=kind,
            model=model_value,
            host=ip,
        ),
        {},
    )


def list_devices(
    state: StateStore,
    *,
    search: str = "",
    device_type: str = "",
) -> list[DeviceBaseRow]:
    rows = state.list_device_base(
        device_type=device_type.strip() or None,
    )
    query = search.strip().lower()
    if not query:
        return rows
    result: list[DeviceBaseRow] = []
    for row in rows:
        haystack = " ".join(
            (
                row.address,
                row.host,
                row.model,
                row.device_type,
                device_type_label(row.device_type),
            )
        ).lower()
        if query in haystack:
            result.append(row)
    return result


def list_device_addresses(state: StateStore) -> list[str]:
    return state.list_device_base_addresses()


def save_device(
    state: StateStore,
    store: ConfigStore,
    data: DeviceBaseFormData,
    *,
    device_id: Optional[int] = None,
) -> DeviceBaseRow:
    existing: Optional[DeviceBaseRow] = None
    if device_id is not None:
        existing = state.get_device_base(device_id)
        if existing is None:
            raise DeviceBaseError("Устройство не найдено")

    other = state.get_device_base_by_host(data.host)
    if other is not None and (existing is None or other.id != existing.id):
        raise DeviceBaseError("Такой IP уже есть в базе", field="host")

    recorder_id = _sync_monitoring(
        store,
        state,
        device_type=data.device_type,
        address=data.address,
        host=data.host,
        recorder_id=existing.recorder_id if existing else None,
        previous_host=existing.host if existing else None,
    )

    if existing is None:
        return state.insert_device_base(
            address=data.address,
            device_type=data.device_type,
            model=data.model,
            host=data.host,
            recorder_id=recorder_id,
        )
    updated = state.update_device_base(
        existing.id,
        address=data.address,
        device_type=data.device_type,
        model=data.model,
        host=data.host,
        recorder_id=recorder_id,
    )
    if updated is None:
        raise DeviceBaseError("Устройство не найдено")
    return updated


def delete_device(
    state: StateStore,
    store: ConfigStore,
    device_id: int,
) -> None:
    row = state.get_device_base(device_id)
    if row is None:
        raise DeviceBaseError("Устройство не найдено")
    _detach_recorder(store, state, row.recorder_id)
    if not state.delete_device_base(device_id):
        raise DeviceBaseError("Устройство не найдено")


def _sync_monitoring(
    store: ConfigStore,
    state: StateStore,
    *,
    device_type: str,
    address: str,
    host: str,
    recorder_id: Optional[str],
    previous_host: Optional[str],
) -> Optional[str]:
    target_kind = MONITORED_TYPES.get(device_type)
    if target_kind is None:
        _detach_recorder(store, state, recorder_id)
        return None

    recorder = store.get_recorder(recorder_id) if recorder_id else None
    if recorder is None:
        recorder = _find_recorder(store, host, target_kind)
    if recorder is None and previous_host and previous_host != host:
        recorder = _find_recorder(store, previous_host, target_kind)

    if recorder is not None:
        store.update_recorder(
            recorder.id,
            RecorderUpdate(
                object_name=address,
                name=recorder.name,
                host=host,
                port=recorder.port,
                use_https=recorder.use_https,
                mac=recorder.mac,
                device_kind=target_kind,  # type: ignore[arg-type]
                inex_panel_id=recorder.inex_panel_id,
            ),
        )
        return recorder.id

    created = store.create_recorder(
        RecorderCreate(
            object_name=address,
            name=None,
            host=host,
            port=LOCKER_DEFAULT_PORT if target_kind == "lockers" else 80,
            use_https=False,
            device_kind=target_kind,  # type: ignore[arg-type]
        )
    )
    return created.id


def _detach_recorder(
    store: ConfigStore,
    state: StateStore,
    recorder_id: Optional[str],
) -> None:
    if not recorder_id:
        return
    store.delete_recorder(recorder_id)
    state.delete_recorder_data(recorder_id)


def _find_recorder(
    store: ConfigStore,
    host: str,
    device_kind: str,
) -> Optional[Recorder]:
    needle = host.strip().lower()
    for recorder in store.list_recorders():
        if recorder.host.strip().lower() != needle:
            continue
        if recorder_device_kind(recorder) == device_kind:
            return recorder
    return None
