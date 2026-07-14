"""Тесты отчёта «Устройства на объекте»."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.config_store import ConfigStore
from app.models import RecorderCreate
from app.state_store import CmdbRecordRow, StateStore
from app.ui.site_inventory import (
    CMDB_TYPE_AUX,
    CMDB_TYPE_CAMERA,
    CMDB_TYPE_NVR,
    build_site_object_groups,
    is_analog_channel,
    site_devices_page_context,
)
from app.state_store import ChannelRow


def _channel(
    *,
    channel_no: int = 0,
    camera_ip: str | None = None,
    source_state: str | None = None,
    name: str | None = None,
) -> ChannelRow:
    return ChannelRow(
        id=channel_no + 1,
        recorder_id="nvr-test",
        channel_no=channel_no,
        name=name,
        camera_ip=camera_ip,
        camera_model=None,
        source_state=source_state,
        health_status="ok",
        health_reason=None,
        video_loss=None,
        last_polled_at=None,
    )


def test_is_analog_channel() -> None:
    assert is_analog_channel(_channel(source_state="On", name="Вход"))
    assert is_analog_channel(_channel(source_state="Off", name="Двор"))
    assert not is_analog_channel(_channel(camera_ip="10.0.0.5"))
    assert not is_analog_channel(_channel(source_state="Deactive"))
    assert not is_analog_channel(_channel())


@pytest.fixture
def config_store(tmp_path: Path) -> ConfigStore:
    store = ConfigStore(path=tmp_path / "config.json")
    store.create_recorder(
        RecorderCreate(
            object_name="Объект 1",
            name="NVR-1",
            host="10.1.1.10",
            port=80,
            use_https=False,
            device_kind="tsv",
        )
    )
    return store


@pytest.fixture
def state_store(tmp_path: Path) -> StateStore:
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    return state


def _write_cmdb(state: StateStore, rows: list[CmdbRecordRow]) -> None:
    with state.replace_cmdb_records() as session:
        session.write_batch(rows)


def test_build_site_object_groups_match_extra_missing(
    config_store: ConfigStore,
    state_store: StateStore,
) -> None:
    recorder = config_store.list_recorders()[0]
    now = datetime.now(timezone.utc)
    state_store.upsert_recorder_metrics(
        recorder.id,
        model="PRN-4011",
        device_online=True,
        health_status="ok",
        last_polled_at=now,
    )
    state_store.upsert_channel(
        recorder.id,
        0,
        name="Камера 1",
        camera_ip="10.1.1.20",
        camera_model="XNO-6080R",
        source_state="On",
        health_status="ok",
        last_polled_at=now,
    )
    state_store.upsert_channel(
        recorder.id,
        1,
        name="Аналог 1",
        source_state="On",
        health_status="ok",
        last_polled_at=now,
    )
    _write_cmdb(
        state_store,
        [
            CmdbRecordRow(
                host="10.1.1.10",
                functional_type=CMDB_TYPE_NVR,
                manufacturer="Hanwha",
                object_name="Объект 1",
                model_name="PRN-4011",
                mac="AA:BB:CC:DD:EE:01",
                device_kind="tsv",
                source_row=1,
            ),
            CmdbRecordRow(
                host="10.1.1.20",
                functional_type=CMDB_TYPE_CAMERA,
                manufacturer="Hanwha",
                object_name="Объект 1",
                model_name="XNO-6080R",
                mac="AA:BB:CC:DD:EE:02",
                device_kind=None,
                source_row=2,
            ),
            CmdbRecordRow(
                host="10.1.1.30",
                functional_type=CMDB_TYPE_CAMERA,
                manufacturer="Hanwha",
                object_name="Объект 1",
                model_name="XNO-6080R",
                mac="AA:BB:CC:DD:EE:03",
                device_kind=None,
                source_row=3,
            ),
            CmdbRecordRow(
                host="10.1.1.40",
                functional_type=CMDB_TYPE_AUX,
                manufacturer="Hanwha",
                object_name="Объект 1",
                model_name="SPD-151",
                mac="AA:BB:CC:DD:EE:04",
                device_kind=None,
                source_row=4,
            ),
        ],
    )

    groups = build_site_object_groups(config_store, state_store)
    assert len(groups) == 1
    group = groups[0]
    assert group.object_name == "Объект 1"
    assert len(group.nvrs) == 1
    assert group.nvrs[0]["match_status"] == "ok"
    assert len(group.ip_cameras) == 1
    assert group.ip_cameras[0]["match_status"] == "ok"
    assert len(group.analog_cameras) == 1
    assert group.analog_cameras[0]["match_status"] == "info"
    assert len(group.auxiliary) == 1
    assert group.auxiliary[0]["model"] == "SPD-151"
    assert len(group.missing) == 1
    assert group.missing[0]["host"] == "10.1.1.30"


def test_site_devices_page_context_search(
    config_store: ConfigStore,
    state_store: StateStore,
) -> None:
    recorder = config_store.list_recorders()[0]
    state_store.upsert_channel(
        recorder.id,
        0,
        name="Уникальная камера",
        camera_ip="10.9.9.9",
        source_state="On",
        health_status="ok",
    )
    ctx = site_devices_page_context(config_store, state_store, search="Уникальная")
    assert ctx["site_devices_has_data"] is True
    assert len(ctx["site_devices_groups"]) == 1
    assert len(ctx["site_devices_groups"][0].ip_cameras) == 1
