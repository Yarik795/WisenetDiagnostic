"""Фоновый ICMP-ping устройств «зомби» (CMDB без опроса) для отчёта «Устройства на объекте»."""

from __future__ import annotations

import asyncio
import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from .config_store import ConfigStore
from .ping_check import ping_host
from .state_store import StateStore
from .ui.site_inventory import build_site_object_groups, normalize_ip

logger = logging.getLogger("ping_jobs")

PING_CONCURRENCY = 16
PING_TIMEOUT_MS = 3000


class PingJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PingTarget:
    ip: str
    object_name: str
    name: str


@dataclass
class PingJob:
    job_id: str
    status: PingJobStatus
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
            return 0 if self.status != PingJobStatus.COMPLETED else 100
        return min(100, int(100 * self.done / self.total))

    @property
    def is_active(self) -> bool:
        return self.status in (PingJobStatus.PENDING, PingJobStatus.RUNNING)


class PingJobManager:
    """Массовый ping missing-устройств с прогрессом и кэшем результатов по IP."""

    def __init__(self) -> None:
        self._start_lock = threading.Lock()
        self._jobs: dict[str, PingJob] = {}
        self._active_job_id: Optional[str] = None
        self._tasks: dict[str, asyncio.Task] = {}
        self._cancel_events: dict[str, asyncio.Event] = {}
        self._results: dict[str, dict[str, Any]] = {}
        self._progress_lock = asyncio.Lock()

    def get_job(self, job_id: str) -> Optional[PingJob]:
        return self._jobs.get(job_id)

    def get_active_job(self) -> Optional[PingJob]:
        if not self._active_job_id:
            return None
        job = self._jobs.get(self._active_job_id)
        if job and job.is_active:
            return job
        return None

    def latest_results(self) -> dict[str, dict[str, Any]]:
        return dict(self._results)

    def _remember_job(self, job: PingJob) -> None:
        self._jobs[job.job_id] = job
        if job.is_active:
            self._active_job_id = job.job_id

    def _clear_active_if(self, job_id: str) -> None:
        if self._active_job_id == job_id:
            self._active_job_id = None

    def _collect_zombie_targets(
        self,
        config_store: ConfigStore,
        state_store: StateStore,
    ) -> list[PingTarget]:
        groups = build_site_object_groups(config_store, state_store)
        seen: set[str] = set()
        targets: list[PingTarget] = []
        for group in groups:
            for row in group.missing:
                ip = normalize_ip(row.get("host"))
                if not ip or ip in seen:
                    continue
                seen.add(ip)
                targets.append(
                    PingTarget(
                        ip=ip,
                        object_name=group.object_name,
                        name=str(row.get("name") or row.get("host") or ip),
                    )
                )
        return targets

    def start_ping_zombies(
        self,
        config_store: ConfigStore,
        state_store: StateStore,
        *,
        refresh_url: Optional[str] = None,
    ) -> PingJob:
        with self._start_lock:
            active = self.get_active_job()
            if active:
                return active

            job = PingJob(
                job_id=uuid.uuid4().hex[:12],
                status=PingJobStatus.PENDING,
                started_at=datetime.now(timezone.utc),
                refresh_url=refresh_url,
            )
            self._remember_job(job)
            task = asyncio.create_task(
                self._execute_job(job, config_store, state_store),
                name=f"ping-job-{job.job_id}",
            )
            self._tasks[job.job_id] = task
            task.add_done_callback(self._task_done_callback(job.job_id))
            return job

    def _task_done_callback(self, job_id: str):
        def _cb(_task: asyncio.Task) -> None:
            self._tasks.pop(job_id, None)
            self._cancel_events.pop(job_id, None)

        return _cb

    async def cancel_active(self) -> bool:
        job = self.get_active_job()
        if not job:
            return False
        job_id = job.job_id
        cancel_event = self._cancel_events.get(job_id)
        if cancel_event:
            cancel_event.set()
        task = self._tasks.get(job_id)
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        return True

    async def _execute_job(
        self,
        job: PingJob,
        config_store: ConfigStore,
        state_store: StateStore,
    ) -> None:
        cancel_event = asyncio.Event()
        self._cancel_events[job.job_id] = cancel_event
        current = asyncio.current_task()
        if current is not None:
            self._tasks[job.job_id] = current

        try:
            targets = self._collect_zombie_targets(config_store, state_store)
            job.total = len(targets)
            job.status = PingJobStatus.RUNNING

            if job.total == 0:
                job.finished_at = datetime.now(timezone.utc)
                job.status = PingJobStatus.COMPLETED
                job.message = "Нет устройств для ping"
                return

            self._results.clear()
            semaphore = asyncio.Semaphore(PING_CONCURRENCY)

            async def ping_one(target: PingTarget) -> None:
                if cancel_event.is_set():
                    return
                async with semaphore:
                    if cancel_event.is_set():
                        return
                    async with self._progress_lock:
                        job.running_hosts.append(target.ip)
                    try:
                        result = await ping_host(target.ip, timeout_ms=PING_TIMEOUT_MS)
                    except Exception as exc:
                        logger.exception(
                            "ping failed",
                            extra={"host": target.ip, "job_id": job.job_id},
                        )
                        result_reachable = False
                        result_rtt = None
                        result_error = str(exc)
                    else:
                        result_reachable = result.reachable
                        result_rtt = result.rtt_ms
                        result_error = result.error

                    entry = {
                        "reachable": result_reachable,
                        "rtt_ms": result_rtt,
                        "error": result_error,
                        "object_name": target.object_name,
                        "name": target.name,
                    }
                    async with self._progress_lock:
                        self._results[target.ip] = entry
                        job.done += 1
                        if result_reachable:
                            job.success += 1
                        else:
                            job.failed += 1
                        if target.ip in job.running_hosts:
                            job.running_hosts.remove(target.ip)

            await asyncio.gather(*(ping_one(t) for t in targets))

            if cancel_event.is_set():
                job.finished_at = datetime.now(timezone.utc)
                job.status = PingJobStatus.CANCELLED
                job.message = f"Ping прерван: {job.done} из {job.total}"
                return

            job.finished_at = datetime.now(timezone.utc)
            job.status = PingJobStatus.COMPLETED
            job.message = (
                f"Ping завершён: доступно {job.success} из {job.total}"
                + (f"; недоступно {job.failed}" if job.failed else "")
            )
        except asyncio.CancelledError:
            if cancel_event.is_set():
                job.finished_at = datetime.now(timezone.utc)
                job.status = PingJobStatus.CANCELLED
                job.message = f"Ping прерван: {job.done} из {job.total}"
            else:
                raise
        except Exception as exc:
            logger.exception("ping job failed", extra={"job_id": job.job_id})
            job.finished_at = datetime.now(timezone.utc)
            job.status = PingJobStatus.FAILED
            job.message = str(exc) or "Ошибка ping"
        finally:
            job.running_hosts = []
            self._tasks.pop(job.job_id, None)
            self._cancel_events.pop(job.job_id, None)
            self._clear_active_if(job.job_id)
