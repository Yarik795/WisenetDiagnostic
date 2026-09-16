"""Тесты справочника «База устройств» и синхронизации с мониторингом."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.config_store import ConfigStore
from app.device_base import (
    DeviceBaseError,
    DeviceBaseFormData,
    delete_device,
    list_devices,
    parse_device_base_form,
    save_device,
)
from app.device_kinds import recorder_device_kind
from app.models import RecorderCreate
from app.state_store import StateStore


@pytest.fixture
def store(tmp_path: Path) -> ConfigStore:
    return ConfigStore(path=tmp_path / "config.json")


@pytest.fixture
def state(tmp_path: Path) -> StateStore:
    db = StateStore(path=tmp_path / "monitoring.db")
    db.init_db()
    return db


def test_parse_device_base_form_requires_ipv4() -> None:
    data, errors = parse_device_base_form("Адрес", "recorder", "", "nvr.local")
    assert data is None
    assert "host" in errors


def test_parse_device_base_form_locker_needs_model() -> None:
    data, errors = parse_device_base_form("Адрес", "locker", "", "10.1.1.1")
    assert data is None
    assert "model" in errors


def test_parse_device_base_form_ok_locker() -> None:
    data, errors = parse_device_base_form("Адрес 1", "locker", "Pridex", "10.1.1.1")
    assert errors == {}
    assert data is not None
    assert data.model == "Pridex"


def test_parse_device_base_form_strips_model_for_non_locker() -> None:
    data, errors = parse_device_base_form("Адрес", "camera", "XNO", "10.1.1.2")
    assert errors == {}
    assert data is not None
    assert data.model == ""


def test_save_recorder_creates_monitoring_entry(
    store: ConfigStore, state: StateStore
) -> None:
    row = save_device(
        state,
        store,
        DeviceBaseFormData(
            address="Объект А",
            device_type="recorder",
            model="",
            host="10.10.10.10",
        ),
    )
    assert row.recorder_id
    recorders = store.list_recorders()
    assert len(recorders) == 1
    assert recorders[0].id == row.recorder_id
    assert recorders[0].host == "10.10.10.10"
    assert recorder_device_kind(recorders[0]) == "tsv"


def test_save_skud_creates_ping_device(store: ConfigStore, state: StateStore) -> None:
    row = save_device(
        state,
        store,
        DeviceBaseFormData(
            address="Объект А",
            device_type="skud_controller",
            model="",
            host="10.20.20.20",
        ),
    )
    recorder = store.get_recorder(row.recorder_id or "")
    assert recorder is not None
    assert recorder_device_kind(recorder) == "skud"


def test_save_lockerbox_creates_lockers_device(store: ConfigStore, state: StateStore) -> None:
    row = save_device(
        state,
        store,
        DeviceBaseFormData(
            address="Объект А",
            device_type="locker",
            model="LockerBox",
            host="10.30.30.30",
        ),
    )
    recorder = store.get_recorder(row.recorder_id or "")
    assert recorder is not None
    assert recorder_device_kind(recorder) == "lockers"
    assert recorder.port == 5555
    assert recorder.id.startswith("lkr-")


def test_save_pridex_creates_lockers_with_adb_port(store: ConfigStore, state: StateStore) -> None:
    row = save_device(
        state,
        store,
        DeviceBaseFormData(
            address="Объект А",
            device_type="locker",
            model="Pridex",
            host="10.40.40.40",
        ),
    )
    recorder = store.get_recorder(row.recorder_id or "")
    assert recorder is not None
    assert recorder_device_kind(recorder) == "lockers"
    assert recorder.port == 5555
    assert recorder.id.startswith("lkr-")


def test_duplicate_ip_rejected(store: ConfigStore, state: StateStore) -> None:
    data = DeviceBaseFormData(
        address="Объект А",
        device_type="camera",
        model="",
        host="10.1.1.1",
    )
    save_device(state, store, data)
    with pytest.raises(DeviceBaseError, match="уже есть"):
        save_device(state, store, data)


def test_save_links_existing_recorder(store: ConfigStore, state: StateStore) -> None:
    existing = store.create_recorder(
        RecorderCreate(
            object_name="Старый",
            host="10.8.8.8",
            port=443,
            use_https=True,
            device_kind="tsv",
        )
    )
    row = save_device(
        state,
        store,
        DeviceBaseFormData(
            address="Новый адрес",
            device_type="recorder",
            model="",
            host="10.8.8.8",
        ),
    )
    assert row.recorder_id == existing.id
    assert len(store.list_recorders()) == 1
    updated = store.get_recorder(existing.id)
    assert updated is not None
    assert updated.object_name == "Новый адрес"
    assert updated.port == 443
    assert updated.use_https is True


def test_type_change_detaches_recorder(store: ConfigStore, state: StateStore) -> None:
    row = save_device(
        state,
        store,
        DeviceBaseFormData(
            address="Объект А",
            device_type="recorder",
            model="",
            host="10.9.9.9",
        ),
    )
    assert store.list_recorders()
    save_device(
        state,
        store,
        DeviceBaseFormData(
            address="Объект А",
            device_type="camera",
            model="",
            host="10.9.9.9",
        ),
        device_id=row.id,
    )
    assert store.list_recorders() == []
    updated = state.get_device_base(row.id)
    assert updated is not None
    assert updated.recorder_id is None


def test_delete_removes_monitoring(store: ConfigStore, state: StateStore) -> None:
    row = save_device(
        state,
        store,
        DeviceBaseFormData(
            address="Объект А",
            device_type="skud_controller",
            model="",
            host="10.4.4.4",
        ),
    )
    delete_device(state, store, row.id)
    assert state.count_device_base() == 0
    assert store.list_recorders() == []


def test_list_devices_search_and_type(store: ConfigStore, state: StateStore) -> None:
    save_device(
        state,
        store,
        DeviceBaseFormData("Ленина 1", "recorder", "", "10.0.0.1"),
    )
    save_device(
        state,
        store,
        DeviceBaseFormData("Ленина 1", "camera", "", "10.0.0.2"),
    )
    save_device(
        state,
        store,
        DeviceBaseFormData("Мира 2", "server", "", "10.0.0.3"),
    )
    cameras = list_devices(state, device_type="camera")
    assert len(cameras) == 1
    assert cameras[0].host == "10.0.0.2"
    found = list_devices(state, search="мира")
    assert len(found) == 1
    by_label = list_devices(state, search="камера")
    assert len(by_label) == 1
