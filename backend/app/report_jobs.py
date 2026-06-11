from __future__ import annotations

import asyncio
import logging
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

from .cashflow_report import build_cashflow_report

logger = logging.getLogger("report_jobs")

ProgressCallback = Callable[[str, int], None]
JobRunner = Callable[[ProgressCallback], str]


class ReportJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ReportJob:
    job_id: str
    status: ReportJobStatus
    started_at: datetime
    finished_at: Optional[datetime] = None
    phase: str = "Подготовка"
    percent: int = 0
    message: Optional[str] = None
    refresh_url: Optional[str] = None
    refresh_target: Optional[str] = None
    refresh_select: Optional[str] = None
    source_key: Optional[str] = None

    @property
    def is_active(self) -> bool:
        return self.status in (ReportJobStatus.PENDING, ReportJobStatus.RUNNING)


class ReportJobManager:
    """Фоновые задачи с прогрессом (отчёты, загрузка исходных данных)."""

    def __init__(self) -> None:
        self._start_lock = threading.Lock()
        self._jobs: dict[str, ReportJob] = {}
        self._active_by_key: dict[str, str] = {}
        self._tasks: dict[str, asyncio.Task] = {}

    def get_job(self, job_id: str) -> Optional[ReportJob]:
        return self._jobs.get(job_id)

    def get_active_job(self, source_key: Optional[str] = None) -> Optional[ReportJob]:
        if source_key is not None:
            job_id = self._active_by_key.get(source_key)
            if not job_id:
                return None
            job = self._jobs.get(job_id)
            if job and job.is_active:
                return job
            return None

        for job_id in self._active_by_key.values():
            job = self._jobs.get(job_id)
            if job and job.is_active:
                return job
        return None

    def start(
        self,
        runner: JobRunner,
        *,
        refresh_url: Optional[str] = None,
        refresh_target: Optional[str] = None,
        refresh_select: Optional[str] = None,
        source_key: Optional[str] = None,
    ) -> ReportJob:
        lock_key = source_key or "__default__"
        with self._start_lock:
            active = self.get_active_job(source_key)
            if active:
                return active

            job = ReportJob(
                job_id=uuid.uuid4().hex[:12],
                status=ReportJobStatus.PENDING,
                started_at=datetime.now(timezone.utc),
                refresh_url=refresh_url,
                refresh_target=refresh_target,
                refresh_select=refresh_select,
                source_key=source_key,
            )
            self._jobs[job.job_id] = job
            self._active_by_key[lock_key] = job.job_id
            task = asyncio.create_task(
                self._execute(job, runner),
                name=f"job-{job.job_id}",
            )
            self._tasks[job.job_id] = task
            task.add_done_callback(self._task_done_callback(job.job_id, lock_key))
            return job

    def start_report(
        self,
        xlsx_path: Path,
        *,
        refresh_url: Optional[str] = None,
        refresh_target: Optional[str] = None,
        refresh_select: Optional[str] = None,
    ) -> ReportJob:
        def runner(on_progress: ProgressCallback) -> str:
            build_cashflow_report(xlsx_path, on_progress=on_progress)
            return "Отчёт успешно сформирован"

        return self.start(
            runner,
            refresh_url=refresh_url,
            refresh_target=refresh_target,
            refresh_select=refresh_select,
            source_key="report",
        )

    def _task_done_callback(self, job_id: str, lock_key: str):
        def _cb(_task: asyncio.Task) -> None:
            self._tasks.pop(job_id, None)
            if self._active_by_key.get(lock_key) == job_id:
                self._active_by_key.pop(lock_key, None)

        return _cb

    async def _execute(self, job: ReportJob, runner: JobRunner) -> None:
        job.status = ReportJobStatus.RUNNING

        def on_progress(phase: str, percent: int) -> None:
            job.phase = phase
            job.percent = max(0, min(100, percent))

        try:
            message = await asyncio.to_thread(runner, on_progress)
            job.status = ReportJobStatus.COMPLETED
            job.percent = 100
            job.phase = "Готово"
            job.message = message
        except Exception as exc:
            logger.exception("background job failed", extra={"job_id": job.job_id})
            job.status = ReportJobStatus.FAILED
            job.message = str(exc) or "Ошибка выполнения"
            job.phase = "Ошибка"
        finally:
            job.finished_at = datetime.now(timezone.utc)
