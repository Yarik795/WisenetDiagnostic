"""Тесты отчёта «Устройства на объекте»."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.config_store import ConfigStore
from app.models import RecorderCreate
from app.state_store import StateStore
from app.ui.site_inventory import (
    CATALOG_TYPE_CAMERA,
    CATALOG_TYPE_RECORDER,
    CATALOG_TYPE_SERVER,
    build_site_object_groups,
    is_analog_channel,
    is_channel_deactive,
    site_devices_page_context,
)
from app.ui.site_inventory_export import (
    build_site_devices_export_context,
    render_site_devices_export_html,
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
    assert is_channel_deactive(_channel(source_state="Deactive"))
    assert is_channel_deactive(_channel(source_state="deactive"))
    assert not is_channel_deactive(_channel(source_state="On"))


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


def _add_device(
    state: StateStore,
    *,
    host: str,
    address: str,
    device_type: str,
    model: str = "",
) -> None:
    state.insert_device_base(
        address=address,
        device_type=device_type,
        model=model,
        host=host,
    )


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
    _add_device(
        state_store,
        host="10.1.1.10",
        address="Объект 1",
        device_type=CATALOG_TYPE_RECORDER,
        model="PRN-4011",
    )
    _add_device(
        state_store,
        host="10.1.1.20",
        address="Объект 1",
        device_type=CATALOG_TYPE_CAMERA,
        model="XNO-6080R",
    )
    _add_device(
        state_store,
        host="10.1.1.30",
        address="Объект 1",
        device_type=CATALOG_TYPE_CAMERA,
        model="XNO-6080R",
    )
    _add_device(
        state_store,
        host="10.1.1.40",
        address="Объект 1",
        device_type=CATALOG_TYPE_SERVER,
        model="SPD-151",
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


def test_site_devices_page_context_ping_results(
    config_store: ConfigStore,
    state_store: StateStore,
) -> None:
    _add_device(
        state_store,
        host="10.1.1.30",
        address="Объект 1",
        device_type=CATALOG_TYPE_CAMERA,
        model="XNO-6080R",
    )
    ctx = site_devices_page_context(
        config_store,
        state_store,
        ping_results={
            "10.1.1.30": {
                "reachable": True,
                "rtt_ms": 5.0,
                "error": None,
            }
        },
    )
    assert ctx["site_devices_zombie_count"] == 1
    missing = ctx["site_devices_groups"][0].missing[0]
    assert missing["ping_status"] == "ok"
    assert "5" in missing["ping_label"]


def test_site_devices_export_includes_ping_results(
    config_store: ConfigStore,
    state_store: StateStore,
) -> None:
    _add_device(
        state_store,
        host="10.1.1.30",
        address="Объект 1",
        device_type=CATALOG_TYPE_CAMERA,
        model="XNO-6080R",
    )
    export_ctx = build_site_devices_export_context(
        config_store,
        state_store,
        ping_results={
            "10.1.1.30": {
                "reachable": False,
                "rtt_ms": None,
                "error": "timeout",
            }
        },
    )
    html = render_site_devices_export_html(export_ctx)
    assert "Недоступен" in html
    assert "<th>Ping</th>" in html


def test_build_site_object_groups_skips_deactive_channels(
    config_store: ConfigStore,
    state_store: StateStore,
) -> None:
    recorder = config_store.list_recorders()[0]
    state_store.upsert_channel(
        recorder.id,
        0,
        name="Активная",
        camera_ip="10.1.1.20",
        source_state="On",
        health_status="ok",
    )
    state_store.upsert_channel(
        recorder.id,
        1,
        name="Пустой слот",
        camera_ip="10.1.1.99",
        source_state="Deactive",
        health_status="unknown",
    )

    groups = build_site_object_groups(config_store, state_store)
    assert len(groups) == 1
    assert len(groups[0].ip_cameras) == 1
    assert groups[0].ip_cameras[0]["host"] == "10.1.1.20"
