from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from app.config_store import ConfigStore
from app.models import AppConfig, Recorder
from app.monitoring import PollCycleStats, run_poll_cycle
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
                ),
                Recorder(
                    id="nvr-b",
                    object_name="Obj",
                    host="10.0.0.2",
                    port=80,
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

    online_poll = __import__("app.sunapi_extended", fromlist=["RecorderPollData"]).RecorderPollData(
        online=True
    )

    with patch(
        "app.monitoring.poll_recorder",
        new_callable=AsyncMock,
        return_value=online_poll,
    ) as mock_poll:
        await run_poll_cycle(
            config_store,
            state,
            include_inventory=False,
            tracker=tracker,
            job_id="testjob01",
        )

    assert job.total == 2
    assert job.done == 2
    assert job.success == 2
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
        return PollCycleStats()

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


@pytest.fixture
def poll_web_client(tmp_path: Path) -> tuple:
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
    client = TestClient(app)
    yield client, store, state
    app.dependency_overrides.clear()


_POLL_REFRESH = {
    "refresh_url": "/objects/partials/groups",
    "refresh_target": "#object-groups",
}


def _poll_page_actions_snippet(html: str) -> str:
    idx = html.find('id="poll-page-actions"')
    assert idx >= 0
    end = html.find("</div>", idx)
    return html[idx : end + 6] if end >= 0 else html[idx : idx + 800]


def test_poll_ui_idle_includes_watch_polling(poll_web_client: tuple) -> None:
    client, _, _ = poll_web_client
    r = client.get("/monitoring/poll-ui", params=_POLL_REFRESH)
    assert r.status_code == 200
    assert "poll-job-panel--idle" in r.text
    snippet = _poll_page_actions_snippet(r.text)
    assert 'hx-get="/monitoring/poll-ui' in snippet
    assert 'hx-trigger="every 2s"' in snippet


def test_objects_page_idle_includes_watch_polling(poll_web_client: tuple) -> None:
    client, _, _ = poll_web_client
    r = client.get("/objects")
    assert r.status_code == 200
    snippet = _poll_page_actions_snippet(r.text)
    assert 'hx-get="/monitoring/poll-ui' in snippet
    assert 'hx-trigger="every 2s"' in snippet


def test_poll_ui_active_job_no_wrapper_polling(poll_web_client: tuple) -> None:
    from datetime import datetime, timezone

    client, _, _ = poll_web_client
    mgr = client.app.state.poll_job_manager
    job = PollJob(
        job_id="ui-active",
        kind=PollJobKind.SHORT,
        status=PollJobStatus.RUNNING,
        include_inventory=False,
        started_at=datetime.now(timezone.utc),
        total=10,
        done=3,
    )
    mgr._remember_job(job)
    try:
        r = client.get("/monitoring/poll-ui", params=_POLL_REFRESH)
        assert r.status_code == 200
        assert "poll-job-panel--running" in r.text
        assert 'hx-trigger="every 1s"' in r.text
        snippet = _poll_page_actions_snippet(r.text)
        assert "every 2s" not in snippet
    finally:
        mgr._clear_active_if(job.job_id)
        mgr._jobs.pop(job.job_id, None)


def test_poll_all_pending_includes_progress_polling(poll_web_client: tuple) -> None:
    from datetime import datetime, timezone

    client, _, _ = poll_web_client
    mgr = client.app.state.poll_job_manager
    job = PollJob(
        job_id="post-pending",
        kind=PollJobKind.SHORT,
        status=PollJobStatus.PENDING,
        include_inventory=False,
        started_at=datetime.now(timezone.utc),
    )
    mgr._remember_job(job)
    with patch.object(mgr, "start_manual_poll", return_value=job):
        r = client.post("/monitoring/poll-all", data=_POLL_REFRESH)
    assert r.status_code == 200
    assert 'hx-trigger="every 1s"' in r.text
    assert "poll-job-panel--running" in r.text
    assert "Запуск" in r.text


def test_poll_all_endpoint_returns_progress_panel(poll_web_client: tuple) -> None:
    client, _, _ = poll_web_client
    r = client.post(
        "/monitoring/poll-all",
        data={
            "refresh_url": "/objects/partials/health-dashboard",
            "refresh_target": "#health-dashboard-stack",
        },
    )
    assert r.status_code == 200
    assert "poll-job-panel" in r.text
    assert "poll-job-panel--compact" in r.text
    assert "poll-job-line" in r.text
    assert "Опросить все NVR" in r.text
    assert "poll-job-results" not in r.text
    assert "Сейчас:" not in r.text
    assert "Автоматический опрос" not in r.text


@pytest.mark.asyncio
async def test_manual_poll_empty_recorders(tmp_path: Path) -> None:
    config_store = ConfigStore(path=tmp_path / "config.json")
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    manager = PollJobManager()

    with patch("app.poll_jobs.run_poll_cycle", new_callable=AsyncMock) as mock_cycle:
        mock_cycle.return_value = PollCycleStats(total=0)
        job = manager.start_manual_poll(config_store, state, include_inventory=False)
        await manager._tasks[job.job_id]
        mock_cycle.assert_awaited_once()

    assert job.status == PollJobStatus.COMPLETED
    assert "Нет включённых" in (job.message or "")
