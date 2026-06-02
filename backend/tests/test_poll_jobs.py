from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from app.config_store import ConfigStore
from app.models import AppConfig, Recorder
from app.monitoring import PollCycleStats, run_poll_cycle
from app.poll_jobs import (
    PollJob,
    PollJobKind,
    PollJobManager,
    PollJobStatus,
    PollJobTracker,
)
from app.monitoring import PollCycleCancelled
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
async def test_run_poll_cycle_updates_tracker_incrementally(
    stores: tuple[ConfigStore, StateStore],
) -> None:
    config_store, state = stores
    job = PollJob(
        job_id="incr",
        kind=PollJobKind.SHORT,
        status=PollJobStatus.RUNNING,
        include_inventory=False,
        started_at=__import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ),
    )
    tracker = PollJobTracker(job)
    online_poll = __import__(
        "app.sunapi_extended", fromlist=["RecorderPollData"]
    ).RecorderPollData(online=True)
    slow_id = "nvr-a"

    async def staggered_poll(recorder, *args, **kwargs):
        if recorder.id == slow_id:
            await asyncio.sleep(0.15)
        return online_poll

    with patch("app.monitoring.poll_recorder", side_effect=staggered_poll):
        cycle_task = asyncio.create_task(
            run_poll_cycle(
                config_store,
                state,
                include_inventory=False,
                tracker=tracker,
            )
        )
        await asyncio.sleep(0.05)
        assert job.done == 1
        await cycle_task

    assert job.done == 2


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


@pytest.mark.asyncio
async def test_cancel_active_poll(stores: tuple[ConfigStore, StateStore]) -> None:
    config_store, state = stores
    manager = PollJobManager()
    release = asyncio.Event()

    async def slow_poll(*args, **kwargs):
        await release.wait()
        return PollCycleStats(total=2)

    with patch("app.poll_jobs.run_poll_cycle", side_effect=slow_poll):
        job = manager.start_manual_poll(config_store, state, include_inventory=False)
        await asyncio.sleep(0.05)
        assert manager.get_active_job() is not None
        assert await manager.cancel_active_poll()
        assert job.status == PollJobStatus.CANCELLED
        assert "прерван" in (job.message or "").lower()
        assert manager.get_active_job() is None
        release.set()


@pytest.mark.asyncio
async def test_run_poll_cycle_respects_cancel_event(
    stores: tuple[ConfigStore, StateStore],
) -> None:
    config_store, state = stores
    cancel_event = asyncio.Event()
    online_poll = __import__(
        "app.sunapi_extended", fromlist=["RecorderPollData"]
    ).RecorderPollData(online=True)

    call_count = 0

    async def slow_poll(recorder, *args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            cancel_event.set()
        await asyncio.sleep(0.05)
        return online_poll

    with patch("app.monitoring.poll_recorder", side_effect=slow_poll):
        with pytest.raises(PollCycleCancelled):
            await run_poll_cycle(
                config_store,
                state,
                cancel_event=cancel_event,
            )


def test_poll_cancel_endpoint(poll_web_client: tuple) -> None:
    client, store, state = poll_web_client
    mgr = client.app.state.poll_job_manager
    from datetime import datetime, timezone

    job = PollJob(
        job_id="cancel-ui",
        kind=PollJobKind.SHORT,
        status=PollJobStatus.RUNNING,
        include_inventory=False,
        started_at=datetime.now(timezone.utc),
        total=10,
        done=3,
    )
    mgr._remember_job(job)
    ev = asyncio.Event()
    mgr._cancel_events[job.job_id] = ev

    async def fake_cancel():
        ev.set()
        job.status = PollJobStatus.CANCELLED
        job.message = "Опрос прерван: 3 из 10"
        job.finished_at = datetime.now(timezone.utc)
        mgr._clear_active_if(job.job_id)

    with patch.object(mgr, "cancel_active_poll", new_callable=AsyncMock, side_effect=fake_cancel):
        r = client.post(
            "/monitoring/poll/cancel",
            data=_POLL_REFRESH,
        )
    assert r.status_code == 200
    assert "poll-job-panel--idle" in r.text or "Опросить все NVR" in r.text
    assert "Остановить опрос" not in r.text


def test_poll_panel_shows_cancel_button_when_active(poll_web_client: tuple) -> None:
    client, _, _ = poll_web_client
    from datetime import datetime, timezone

    mgr = client.app.state.poll_job_manager
    job = PollJob(
        job_id="ui-cancel",
        kind=PollJobKind.SHORT,
        status=PollJobStatus.RUNNING,
        include_inventory=False,
        started_at=datetime.now(timezone.utc),
        total=5,
        done=1,
    )
    mgr._remember_job(job)
    try:
        r = client.get("/monitoring/poll-ui", params=_POLL_REFRESH)
        assert r.status_code == 200
        assert 'hx-post="/monitoring/poll/cancel"' in r.text
        assert "Остановить опрос" in r.text
    finally:
        mgr._clear_active_if(job.job_id)
        mgr._jobs.pop(job.job_id, None)


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
