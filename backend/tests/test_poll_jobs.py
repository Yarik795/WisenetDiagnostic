from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from app.config_store import ConfigStore
from app.models import AppConfig, Recorder
from app.monitoring import run_poll_cycle
from app.poll_jobs import PollJobManager, PollJobStatus, PollJobTracker, PollJob, PollJobKind
from app.state_store import StateStore


@pytest.fixture
def stores(tmp_path: Path) -> tuple[ConfigStore, StateStore]:
    config_store = ConfigStore(path=tmp_path / "config.json")
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    config_store.save(
        AppConfig(
            recorders=[
                Recorder(
                    id="nvr-a",
                    object_name="Obj",
                    host="10.0.0.1",
                    port=80,
                    enabled=True,
                ),
                Recorder(
                    id="nvr-b",
                    object_name="Obj",
                    host="10.0.0.2",
                    port=80,
                    enabled=True,
                ),
            ]
        )
    )
    return config_store, state


@pytest.mark.asyncio
async def test_run_poll_cycle_updates_tracker(stores: tuple[ConfigStore, StateStore]) -> None:
    config_store, state = stores
    job = PollJob(
        job_id="test",
        kind=PollJobKind.SHORT,
        status=PollJobStatus.RUNNING,
        include_inventory=False,
        started_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    )
    tracker = PollJobTracker(job)

    with patch(
        "app.monitoring.poll_single_recorder",
        new_callable=AsyncMock,
        return_value=None,
    ) as mock_poll:
        await run_poll_cycle(
            config_store, state, include_inventory=False, tracker=tracker
        )

    assert job.total == 2
    assert job.done == 2
    assert mock_poll.await_count == 2


@pytest.mark.asyncio
async def test_poll_job_manager_serializes_cycles(
    stores: tuple[ConfigStore, StateStore],
) -> None:
    config_store, state = stores
    manager = PollJobManager()
    started = asyncio.Event()
    release = asyncio.Event()

    async def slow_poll(*args, **kwargs):
        started.set()
        await release.wait()

    with patch("app.poll_jobs.run_poll_cycle", side_effect=slow_poll):
        job1 = manager.start_manual_poll(config_store, state, include_inventory=False)
        await asyncio.sleep(0.05)
        assert started.is_set()

        job2 = manager.start_manual_poll(config_store, state, include_inventory=False)
        assert job2.job_id == job1.job_id

        ran = await manager.try_run_scheduled(
            config_store, state, include_inventory=False
        )
        assert ran is False

        release.set()
        await manager._tasks[job1.job_id]

    assert job1.status == PollJobStatus.COMPLETED


def test_poll_all_endpoint_returns_progress_panel(tmp_path: Path) -> None:
    from fastapi.testclient import TestClient

    from app.main import app
    from app.ui.dependencies import get_state_store, get_store

    config_path = tmp_path / "config.json"
    store = ConfigStore(path=config_path)
    db_path = tmp_path / "monitoring.db"
    state = StateStore(path=db_path)
    state.init_db()

    app.dependency_overrides[get_store] = lambda: store
    app.dependency_overrides[get_state_store] = lambda: state
    try:
        client = TestClient(app)
        r = client.post(
            "/monitoring/poll-all",
            data={
                "refresh_url": "/objects/partials/health-dashboard",
                "refresh_target": "#health-dashboard-stack",
            },
        )
        assert r.status_code == 200
        assert "poll-job-panel" in r.text
        assert "Опрос регистраторов" in r.text
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_manual_poll_empty_recorders(tmp_path: Path) -> None:
    config_store = ConfigStore(path=tmp_path / "config.json")
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    manager = PollJobManager()

    with patch("app.poll_jobs.run_poll_cycle", new_callable=AsyncMock) as mock_cycle:
        job = manager.start_manual_poll(config_store, state, include_inventory=False)
        await manager._tasks[job.job_id]
        mock_cycle.assert_awaited_once()

    assert job.status == PollJobStatus.COMPLETED
    assert "Нет включённых" in (job.message or "")
