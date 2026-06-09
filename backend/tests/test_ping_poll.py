"""Тесты ping-опроса для СКУД и биотерминалов."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from app.config_store import ConfigStore
from app.models import AppConfig, Recorder
from app.monitoring import apply_poll_result, poll_single_recorder
from app.ping_check import PingResult
from app.state_store import StateStore
from app.sunapi_extended import RecorderPollData


@pytest.fixture
def stores(tmp_path):
    config_path = tmp_path / "config.json"
    db_path = tmp_path / "state.db"
    store = ConfigStore(path=config_path)
    state = StateStore(path=db_path)
    state.init_db()
    skud = Recorder(
        id="skud-test",
        object_name="Obj",
        host="10.0.0.50",
        device_kind="skud",
        mac="AA:BB:CC:DD:EE:FF",
    )
    store.save(AppConfig(recorders=[skud]))
    return store, state, skud


@pytest.mark.asyncio
async def test_poll_single_recorder_skud_uses_ping(stores) -> None:
    store, state, skud = stores
    with patch(
        "app.ping_check.ping_host",
        new_callable=AsyncMock,
        return_value=PingResult(reachable=True, rtt_ms=3.0),
    ) as ping_mock:
        with patch("app.monitoring.poll_recorder", new_callable=AsyncMock) as sunapi_mock:
            await poll_single_recorder(
                store, state, skud, include_inventory=False
            )
    ping_mock.assert_awaited_once_with("10.0.0.50")
    sunapi_mock.assert_not_called()
    metrics = state.get_recorder_metrics("skud-test")
    assert metrics is not None
    assert metrics.device_online is True
    assert metrics.health_status == "ok"


def test_apply_poll_result_skud_skips_nvr_categories(stores) -> None:
    store, state, skud = stores
    polled_at = datetime(2026, 6, 9, tzinfo=timezone.utc)
    apply_poll_result(
        store,
        state,
        skud,
        RecorderPollData(online=False, error="timeout"),
        store.load().monitoring,
        polled_at,
    )
    metrics = state.get_recorder_metrics("skud-test")
    assert metrics is not None
    assert metrics.health_status == "error"
    assert metrics.health_reason == "timeout"
    assert state.list_channels("skud-test") == []
