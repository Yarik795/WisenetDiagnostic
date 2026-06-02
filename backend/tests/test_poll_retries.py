from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from app.config_store import ConfigStore
from app.models import AppConfig, MonitoringSettings, Recorder
from app.monitoring import run_poll_cycle
from app.state_store import StateStore
from app.sunapi_extended import RecorderPollData


@pytest.fixture
def stores(tmp_path: Path) -> tuple[ConfigStore, StateStore]:
    config_store = ConfigStore(path=tmp_path / "config.json")
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    config_store.save(
        AppConfig(
            monitoring=MonitoringSettings(
                poll_retry_enabled=True,
                poll_retry_max=2,
                poll_retry_delay_seconds=1,
            ),
            recorders=[
                Recorder(
                    id="nvr-ok",
                    object_name="Obj",
                    host="10.0.0.1",
                    port=80,
                ),
                Recorder(
                    id="nvr-retry",
                    object_name="Obj",
                    host="10.0.0.2",
                    port=80,
                ),
                Recorder(
                    id="nvr-fail",
                    object_name="Obj",
                    host="10.0.0.3",
                    port=80,
                ),
            ],
        )
    )
    return config_store, state


@pytest.mark.asyncio
async def test_retry_succeeds_on_second_attempt(
    stores: tuple[ConfigStore, StateStore],
) -> None:
    config_store, state = stores
    calls: dict[str, int] = {"nvr-retry": 0}

    async def fake_poll(recorder, credentials, *, include_inventory=True, timeout=20.0):
        if recorder.id == "nvr-ok":
            return RecorderPollData(online=True)
        if recorder.id == "nvr-retry":
            calls["nvr-retry"] += 1
            if calls["nvr-retry"] >= 2:
                return RecorderPollData(online=True)
            return RecorderPollData(online=False, error="timeout")
        return RecorderPollData(online=False, error="offline")

    with (
        patch("app.monitoring.poll_recorder", side_effect=fake_poll),
        patch("app.monitoring.asyncio.sleep", new_callable=AsyncMock),
    ):
        stats = await run_poll_cycle(
            config_store,
            state,
            include_inventory=False,
            job_id="job-retry1",
        )

    assert stats.total == 3
    assert stats.responded == 2
    assert stats.responded_after_retry == 1
    assert stats.still_unreachable == 1

    attempts = state.list_poll_attempts(job_id="job-retry1")
    by_recorder: dict[str, list] = {}
    for row in attempts:
        by_recorder.setdefault(row.recorder_id, []).append(row)

    retry_rows = sorted(by_recorder["nvr-retry"], key=lambda r: r.attempt)
    assert len(retry_rows) == 2
    assert retry_rows[0].online is False
    assert retry_rows[1].online is True
    assert len(by_recorder["nvr-fail"]) == 3
    assert all(not row.online for row in by_recorder["nvr-fail"])

    retry_metrics = state.get_recorder_metrics("nvr-retry")
    assert retry_metrics is not None
    assert retry_metrics.last_poll_job_id == "job-retry1"
    assert retry_metrics.last_poll_attempts == 2
    assert retry_metrics.last_poll_success_attempt == 2
    assert retry_metrics.last_poll_first_try_ok is False

    ok_metrics = state.get_recorder_metrics("nvr-ok")
    assert ok_metrics is not None
    assert ok_metrics.last_poll_first_try_ok is True

    fail_metrics = state.get_recorder_metrics("nvr-fail")
    assert fail_metrics is not None
    assert fail_metrics.device_online is False
    assert fail_metrics.last_poll_success_attempt is None


@pytest.mark.asyncio
async def test_retries_disabled_single_pass(
    stores: tuple[ConfigStore, StateStore],
) -> None:
    config_store, state = stores
    config = config_store.load()
    config.monitoring.poll_retry_enabled = False
    config_store.save(config)

    calls = 0

    async def fake_poll(recorder, credentials, *, include_inventory=True, timeout=20.0):
        nonlocal calls
        calls += 1
        return RecorderPollData(online=False, error="offline")

    with patch("app.monitoring.poll_recorder", side_effect=fake_poll):
        stats = await run_poll_cycle(
            config_store,
            state,
            job_id="job-single",
        )

    assert stats.total == 3
    assert stats.still_unreachable == 3
    assert calls == 3
