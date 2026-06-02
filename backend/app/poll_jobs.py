from __future__ import annotations

import asyncio
import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from .config_store import ConfigStore
from .models import Recorder
from .monitoring import PollCycleStats, run_poll_cycle
from .state_store import StateStore
from .ui.helpers import display_recorder_name

logger = logging.getLogger("poll_jobs")


def _build_poll_completion_message(job: PollJob, stats: PollCycleStats) -> str:
    if stats.total == 0:
        return "Нет включённых регистраторов"
    if job.kind == PollJobKind.INVENTORY:
        prefix = "Инвентаризация завершена"
    else:
        prefix = "Опрос завершён"
    parts = [f"{prefix}: {stats.responded} из {stats.total}"]
    if stats.responded_after_retry:
        parts.append(f"с повтора: {stats.responded_after_retry}")
    if stats.still_unreachable:
        parts.append(f"без ответа: {stats.still_unreachable}")
    return "; ".join(parts)


class PollJobKind(str, Enum):
    SHORT = "short"
    INVENTORY = "inventory"
    SCHEDULED_SHORT = "scheduled_short"
    SCHEDULED_INVENTORY = "scheduled_inventory"


class PollJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class RecorderPollResult:
    recorder_id: str
    display_name: str
    success: bool
    error: Optional[str] = None


@dataclass
class PollJob:
    job_id: str
    kind: PollJobKind
    status: PollJobStatus
    include_inventory: bool
    started_at: datetime
    finished_at: Optional[datetime] = None
    total: int = 0
    done: int = 0
    success: int = 0
    failed: int = 0
    running_names: list[str] = field(default_factory=list)
    recent_results: list[RecorderPollResult] = field(default_factory=list)
    message: Optional[str] = None
    refresh_url: Optional[str] = None
    phase: str = "polling"
    retry_round: int = 0
    max_attempts: int = 1
    pending_retry_count: int = 0
    retry_delay_seconds: int = 5
    responded_after_retry: int = 0
    still_unreachable: int = 0

    @property
    def percent(self) -> int:
        if self.total <= 0:
            return 0 if self.status != PollJobStatus.COMPLETED else 100
        return min(100, int(100 * self.done / self.total))

    @property
    def is_active(self) -> bool:
        return self.status in (PollJobStatus.PENDING, PollJobStatus.RUNNING)


class PollJobTracker:
    """Обновляет прогресс job при опросе регистраторов."""

    def __init__(self, job: PollJob, *, max_recent: int = 12) -> None:
        self.job = job
        self._max_recent = max_recent
        self._mu = asyncio.Lock()
        self._running: dict[str, str] = {}

    async def set_total(self, total: int) -> None:
        async with self._mu:
            self.job.total = total

    async def set_retry_config(self, max_attempts: int, delay_seconds: int) -> None:
        async with self._mu:
            self.job.max_attempts = max_attempts
            self.job.retry_delay_seconds = delay_seconds

    async def recorder_started(self, recorder: Recorder) -> None:
        name = display_recorder_name(recorder)
        async with self._mu:
            self._running[recorder.id] = name
            self.job.running_names = list(self._running.values())

    async def recorder_attempt_finished(self, recorder: Recorder) -> None:
        async with self._mu:
            self._running.pop(recorder.id, None)
            self.job.running_names = list(self._running.values())

    async def set_polling_round(self, attempt: int, pending_count: int) -> None:
        async with self._mu:
            self.job.phase = "polling"
            self.job.retry_round = attempt
            self.job.pending_retry_count = pending_count

    async def set_waiting_retry(
        self,
        attempt: int,
        pending_count: int,
        delay_seconds: int,
        max_attempts: int,
    ) -> None:
        async with self._mu:
            self.job.phase = "waiting_retry"
            self.job.retry_round = attempt
            self.job.pending_retry_count = pending_count
            self.job.retry_delay_seconds = delay_seconds
            self.job.max_attempts = max_attempts

    async def recorder_final_finished(
        self,
        recorder: Recorder,
        *,
        success: bool,
        after_retry: bool = False,
        error: Optional[str] = None,
    ) -> None:
        name = display_recorder_name(recorder)
        async with self._mu:
            self._running.pop(recorder.id, None)
            self.job.running_names = list(self._running.values())
            self.job.done += 1
            if success:
                self.job.success += 1
                if after_retry:
                    self.job.responded_after_retry += 1
            else:
                self.job.failed += 1
                self.job.still_unreachable += 1
            result = RecorderPollResult(
                recorder_id=recorder.id,
                display_name=name,
                success=success,
                error=error,
            )
            self.job.recent_results.insert(0, result)
            self.job.recent_results = self.job.recent_results[: self._max_recent]

    async def finish(self, message: str, *, failed: bool = False) -> None:
        async with self._mu:
            self.job.running_names = []
            self.job.finished_at = datetime.now(timezone.utc)
            self.job.message = message
            self.job.status = (
                PollJobStatus.FAILED if failed else PollJobStatus.COMPLETED
            )


class PollJobManager:
    """Фоновые массовые опросы и единая блокировка цикла опроса."""

    def __init__(self) -> None:
        self._cycle_lock = asyncio.Lock()
        self._manual_start_lock = threading.Lock()
        self._jobs: dict[str, PollJob] = {}
        self._active_job_id: Optional[str] = None
        self._tasks: dict[str, asyncio.Task] = {}

    def get_job(self, job_id: str) -> Optional[PollJob]:
        return self._jobs.get(job_id)

    def get_active_job(self) -> Optional[PollJob]:
        if not self._active_job_id:
            return None
        job = self._jobs.get(self._active_job_id)
        if job and job.is_active:
            return job
        return None

    def _remember_job(self, job: PollJob) -> None:
        self._jobs[job.job_id] = job
        if job.is_active:
            self._active_job_id = job.job_id

    def _clear_active_if(self, job_id: str) -> None:
        if self._active_job_id == job_id:
            self._active_job_id = None

    def _new_job(
        self,
        kind: PollJobKind,
        *,
        include_inventory: bool,
        refresh_url: Optional[str] = None,
    ) -> PollJob:
        job = PollJob(
            job_id=uuid.uuid4().hex[:12],
            kind=kind,
            status=PollJobStatus.PENDING,
            include_inventory=include_inventory,
            started_at=datetime.now(timezone.utc),
            refresh_url=refresh_url,
        )
        self._remember_job(job)
        return job

    async def try_run_scheduled(
        self,
        config_store: ConfigStore,
        state_store: StateStore,
        *,
        include_inventory: bool,
    ) -> bool:
        """Запуск цикла планировщика. False — цикл уже выполняется."""
        if self._cycle_lock.locked():
            logger.info("scheduler tick skipped: poll cycle already running")
            return False

        kind = (
            PollJobKind.SCHEDULED_INVENTORY
            if include_inventory
            else PollJobKind.SCHEDULED_SHORT
        )
        job = self._new_job(kind, include_inventory=include_inventory)
        await self._execute_job(job, config_store, state_store)
        return True

    def start_manual_poll(
        self,
        config_store: ConfigStore,
        state_store: StateStore,
        *,
        include_inventory: bool,
        refresh_url: Optional[str] = None,
    ) -> PollJob:
        with self._manual_start_lock:
            active = self.get_active_job()
            if active:
                return active

            kind = PollJobKind.INVENTORY if include_inventory else PollJobKind.SHORT
            job = self._new_job(
                kind,
                include_inventory=include_inventory,
                refresh_url=refresh_url,
            )
            task = asyncio.create_task(
                self._execute_job(job, config_store, state_store),
                name=f"poll-job-{job.job_id}",
            )
            self._tasks[job.job_id] = task
            task.add_done_callback(lambda t: self._tasks.pop(job.job_id, None))
            return job

    async def _execute_job(
        self,
        job: PollJob,
        config_store: ConfigStore,
        state_store: StateStore,
    ) -> None:
        if self._cycle_lock.locked() and job.status == PollJobStatus.PENDING:
            job.status = PollJobStatus.SKIPPED
            job.finished_at = datetime.now(timezone.utc)
            job.message = "Опрос уже выполняется"
            self._clear_active_if(job.job_id)
            return

        async with self._cycle_lock:
            job.status = PollJobStatus.RUNNING
            tracker = PollJobTracker(job)
            try:
                stats = await run_poll_cycle(
                    config_store,
                    state_store,
                    include_inventory=job.include_inventory,
                    job_id=job.job_id,
                    tracker=tracker,
                )
                msg = _build_poll_completion_message(job, stats)
                await tracker.finish(msg)
            except Exception as exc:
                logger.exception("poll job failed", extra={"job_id": job.job_id})
                await tracker.finish(str(exc) or "Ошибка опроса", failed=True)
            finally:
                self._clear_active_if(job.job_id)
