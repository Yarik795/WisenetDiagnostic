"""Тесты фонового ping зомби-устройств."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from app.config_store import ConfigStore
from app.models import RecorderCreate
from app.ping_check import PingResult
from app.ping_jobs import PingJobManager, PingJobStatus
from app.state_store import CmdbRecordRow, StateStore
from app.ui.site_inventory import CMDB_TYPE_CAMERA, CMDB_TYPE_NVR


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


@pytest.mark.asyncio
async def test_ping_zombies_completes_and_stores_results(
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
    _write_cmdb(
        state_store,
        [
            CmdbRecordRow(
                host="10.1.1.10",
                functional_type=CMDB_TYPE_NVR,
                manufacturer="Hanwha",
                object_name="Объект 1",
                model_name="PRN-4011",
                mac=None,
                device_kind="tsv",
                source_row=1,
            ),
            CmdbRecordRow(
                host="10.1.1.30",
                functional_type=CMDB_TYPE_CAMERA,
                manufacturer="Hanwha",
                object_name="Объект 1",
                model_name="XNO-6080R",
                mac=None,
                device_kind=None,
                source_row=2,
            ),
        ],
    )

    mgr = PingJobManager()

    async def fake_ping(host: str, *, timeout_ms: int = 3000) -> PingResult:
        if host == "10.1.1.30":
            return PingResult(reachable=True, rtt_ms=12.5)
        return PingResult(reachable=False, error="timeout")

    with patch("app.ping_jobs.ping_host", new=AsyncMock(side_effect=fake_ping)):
        job = mgr.start_ping_zombies(config_store, state_store)
        task = mgr._tasks[job.job_id]
        await task

    finished = mgr.get_job(job.job_id)
    assert finished is not None
    assert finished.status == PingJobStatus.COMPLETED
    assert finished.total == 1
    assert finished.success == 1
    assert finished.failed == 0
    results = mgr.latest_results()
    assert results["10.1.1.30"]["reachable"] is True
    assert results["10.1.1.30"]["rtt_ms"] == 12.5


@pytest.mark.asyncio
async def test_ping_zombies_no_targets(
    config_store: ConfigStore,
    state_store: StateStore,
) -> None:
    mgr = PingJobManager()
    job = mgr.start_ping_zombies(config_store, state_store)
    task = mgr._tasks[job.job_id]
    await task
    finished = mgr.get_job(job.job_id)
    assert finished is not None
    assert finished.status == PingJobStatus.COMPLETED
    assert finished.total == 0
    assert finished.message == "Нет устройств для ping"
