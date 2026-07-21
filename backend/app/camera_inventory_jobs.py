"""Фоновый inventory-опрос IP-камер с регистраторов."""

from __future__ import annotations

import asyncio
import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from .camera_inventory import (
    apply_inventory_outcome,
    build_inventory_targets,
    probe_camera_inventory,
)
from .config_store import ConfigStore
from .state_store import StateStore

logger = logging.getLogger("camera_inventory_jobs")

INVENTORY_CONCURRENCY = 12


class CameraInventoryJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CameraInventoryJob:
    job_id: str
    status: CameraInventoryJobStatus
    started_at: datetime
    finished_at: Optional[datetime] = None
    total: int = 0
    done: int = 0
    success: int = 0
    failed: int = 0
    running_hosts: list[str] = field(default_factory=list)
    message: Optional[str] = None
    refresh_url: Optional[str] = None

    @property
    def percent(self) -> int:
        if self.total <= 0:
            return 0 if self.status != CameraInventoryJobStatus.COMPLETED else 100
        return min(100, int(100 * self.done / self.total))

    @property
    def is_active(self) -> bool:
        return self.status in (
            CameraInventoryJobStatus.PENDING,
            CameraInventoryJobStatus.RUNNING,
        )


class CameraInventoryJobManager:
    def __init__(self) -> None:
        self._start_lock = threading.Lock()
        self._jobs: dict[str, CameraInventoryJob] = {}
        self._active_job_id: Optional[str] = None
        self._tasks: dict[str, asyncio.Task] = {}
        self._cancel_events: dict[str, asyncio.Event] = {}
        self._progress_lock = asyncio.Lock()

    def get_job(self, job_id: str) -> Optional[CameraInventoryJob]:
        return self._jobs.get(job_id)

    def get_active_job(self) -> Optional[CameraInventoryJob]:
        if not self._active_job_id:
            return None
        job = self._jobs.get(self._active_job_id)
        if job and job.is_active:
            return job
        return None

    def _remember_job(self, job: CameraInventoryJob) -> None:
        self._jobs[job.job_id] = job
        if job.is_active:
            self._active_job_id = job.job_id

    def _clear_active_if(self, job_id: str) -> None:
        if self._active_job_id == job_id:
            self._active_job_id = None

    def start_inventory(
        self,
        config_store: ConfigStore,
        state_store: StateStore,
        *,
        refresh_url: Optional[str] = None,
    ) -> CameraInventoryJob:
        with self._start_lock:
            active = self.get_active_job()
            if active:
                return active

            job = CameraInventoryJob(
                job_id=uuid.uuid4().hex[:12],
                status=CameraInventoryJobStatus.PENDING,
                started_at=datetime.now(timezone.utc),
                refresh_url=refresh_url,
            )
            self._remember_job(job)
            task = asyncio.create_task(
                self._execute_job(job, config_store, state_store),
                name=f"camera-inventory-{job.job_id}",
            )
            self._tasks[job.job_id] = task
            task.add_done_callback(self._task_done_callback(job.job_id))
            return job

    def _task_done_callback(self, job_id: str):
        def _cb(_task: asyncio.Task) -> None:
            self._tasks.pop(job_id, None)
            self._cancel_events.pop(job_id, None)

        return _cb

    async def cancel_job(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if not job or not job.is_active:
            return False
        cancel = self._cancel_events.get(job_id)
        if cancel:
            cancel.set()
        job.status = CameraInventoryJobStatus.CANCELLED
        job.finished_at = datetime.now(timezone.utc)
        job.message = "Отменено пользователем"
        self._clear_active_if(job_id)
        task = self._tasks.get(job_id)
        if task and not task.done():
            task.cancel()
        return True

    async def _execute_job(
        self,
        job: CameraInventoryJob,
        config_store: ConfigStore,
        state_store: StateStore,
    ) -> None:
        cancel = asyncio.Event()
        self._cancel_events[job.job_id] = cancel
        targets = build_inventory_targets(config_store, state_store)
        job.total = len(targets)
        job.status = CameraInventoryJobStatus.RUNNING

        if not targets:
            job.status = CameraInventoryJobStatus.COMPLETED
            job.finished_at = datetime.now(timezone.utc)
            job.message = "Нет IP-камер для опроса"
            self._clear_active_if(job.job_id)
            return

        sem = asyncio.Semaphore(INVENTORY_CONCURRENCY)

        async def _probe_one(target) -> None:
            if cancel.is_set():
                return
            async with sem:
                if cancel.is_set():
                    return
                async with self._progress_lock:
                    job.running_hosts.append(target.host)
                try:
                    outcome = await probe_camera_inventory(target)
                    await apply_inventory_outcome(
                        state_store,
                        target.host,
                        outcome,
                    )
                    async with self._progress_lock:
                        job.done += 1
                        if outcome.error and outcome.manufacturer == "unknown":
                            job.failed += 1
                        else:
                            job.success += 1
                except Exception as exc:
                    logger.exception(
                        "camera inventory probe failed",
                        extra={"host": target.host},
                    )
                    from .camera_inventory import CameraInventoryOutcome

                    await apply_inventory_outcome(
                        state_store,
                        target.host,
                        CameraInventoryOutcome(
                            manufacturer="unknown",
                            error=str(exc)[:200],
                        ),
                    )
                    async with self._progress_lock:
                        job.done += 1
                        job.failed += 1
                finally:
                    async with self._progress_lock:
                        if target.host in job.running_hosts:
                            job.running_hosts.remove(target.host)

        try:
            await asyncio.gather(*[_probe_one(t) for t in targets])
            if cancel.is_set():
                job.status = CameraInventoryJobStatus.CANCELLED
            else:
                job.status = CameraInventoryJobStatus.COMPLETED
                job.message = (
                    f"Опрошено {job.success} из {job.total}"
                    + (f", ошибок: {job.failed}" if job.failed else "")
                )
        except asyncio.CancelledError:
            job.status = CameraInventoryJobStatus.CANCELLED
            job.message = "Отменено"
        except Exception as exc:
            job.status = CameraInventoryJobStatus.FAILED
            job.message = str(exc)[:200]
            logger.exception("camera inventory job failed")
        finally:
            job.finished_at = datetime.now(timezone.utc)
            self._clear_active_if(job.job_id)
