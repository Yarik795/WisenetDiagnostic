"""Тесты паузы и возобновления автоматического опроса NVR."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.config_store import ConfigStore
from app.main import app
from app.models import AppConfig, Recorder
from app.scheduler import MonitoringScheduler
from app.state_store import StateStore
from app.ui.dependencies import get_state_store, get_store


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
            ]
        )
    )
    return config_store, state


@pytest.mark.asyncio
async def test_scheduler_skips_scheduled_poll_when_paused(
    stores: tuple[ConfigStore, StateStore],
) -> None:
    config_store, state = stores
    scheduler = MonitoringScheduler(config_store, state)

    with patch.object(
        scheduler.poll_jobs,
        "try_run_scheduled",
        new_callable=AsyncMock,
        return_value=True,
    ) as mock_scheduled:
        await scheduler._tick()
        assert mock_scheduled.await_count == 1

        scheduler.pause_auto()
        await scheduler._tick()
        assert mock_scheduled.await_count == 1

        scheduler.resume_auto()
        await scheduler._tick()
        assert mock_scheduled.await_count == 2


@pytest.mark.asyncio
async def test_scheduler_tick_still_runs_report_delivery_when_paused(
    stores: tuple[ConfigStore, StateStore],
) -> None:
    config_store, state = stores
    scheduler = MonitoringScheduler(config_store, state)
    scheduler.pause_auto()

    with patch.object(
        scheduler.poll_jobs,
        "try_run_scheduled",
        new_callable=AsyncMock,
    ) as mock_scheduled:
        with patch.object(
            scheduler.report_delivery,
            "tick_sync",
        ) as mock_report:
            await scheduler._tick()
            mock_scheduled.assert_not_awaited()
            mock_report.assert_called_once()


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    config_path = tmp_path / "config.json"
    store = ConfigStore(path=config_path)
    db_path = tmp_path / "monitoring.db"
    state = StateStore(path=db_path)
    state.init_db()

    def override_store() -> ConfigStore:
        return store

    def override_state() -> StateStore:
        return state

    app.dependency_overrides[get_store] = override_store
    app.dependency_overrides[get_state_store] = override_state
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_objects_page_has_auto_poll_controls(client: TestClient) -> None:
    r = client.get("/monitoring")
    assert r.status_code == 200
    assert "Остановить обновление" in r.text
    assert 'hx-post="/monitoring/auto-poll/stop"' in r.text
    assert 'id="poll-page-actions"' in r.text


def _scheduler_from_client(client: TestClient) -> MonitoringScheduler:
    client.get("/health")
    return client.app.state.scheduler


def test_auto_poll_stop_and_resume(client: TestClient) -> None:
    scheduler = _scheduler_from_client(client)

    r_stop = client.post(
        "/monitoring/auto-poll/stop",
        data={
            "refresh_url": "/monitoring/partials/groups",
            "refresh_target": "#object-groups",
        },
    )
    assert r_stop.status_code == 200
    assert "Возобновить обновление" in r_stop.text
    assert "приостановлен" in r_stop.text.lower()
    assert scheduler.is_auto_paused()

    r_resume = client.post(
        "/monitoring/auto-poll/resume",
        data={
            "refresh_url": "/monitoring/partials/groups",
            "refresh_target": "#object-groups",
        },
    )
    assert r_resume.status_code == 200
    assert "Остановить обновление" in r_resume.text
    assert not scheduler.is_auto_paused()


def test_manual_poll_works_when_auto_paused(client: TestClient) -> None:
    scheduler = _scheduler_from_client(client)
    scheduler.pause_auto()

    with patch("app.poll_jobs.run_poll_cycle", new_callable=AsyncMock):
        r = client.post(
            "/monitoring/poll-all",
            data={
                "refresh_url": "/monitoring/partials/health-dashboard",
                "refresh_target": "#health-dashboard-stack",
            },
        )
    assert r.status_code == 200
    assert "poll-job-panel" in r.text
