from __future__ import annotations

import asyncio
import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

from .cashflow_report import build_cashflow_report

logger = logging.getLogger("report_jobs")


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

    @property
    def is_active(self) -> bool:
        return self.status in (ReportJobStatus.PENDING, ReportJobStatus.RUNNING)


class ReportJobManager:
    """Фоновая генерация отчёта «Статус оплаты»."""

    def __init__(self) -> None:
        self._start_lock = threading.Lock()
        self._jobs: dict[str, ReportJob] = {}
        self._active_job_id: Optional[str] = None
        self._tasks: dict[str, asyncio.Task] = {}

    def get_job(self, job_id: str) -> Optional[ReportJob]:
        return self._jobs.get(job_id)

    def get_active_job(self) -> Optional[ReportJob]:
        if not self._active_job_id:
            return None
        job = self._jobs.get(self._active_job_id)
        if job and job.is_active:
            return job
        return None

    def start(
        self,
        xlsx_path: Path,
        *,
        refresh_url: Optional[str] = None,
    ) -> ReportJob:
        with self._start_lock:
            active = self.get_active_job()
            if active:
                return active

            job = ReportJob(
                job_id=uuid.uuid4().hex[:12],
                status=ReportJobStatus.PENDING,
                started_at=datetime.now(timezone.utc),
                refresh_url=refresh_url,
            )
            self._jobs[job.job_id] = job
            self._active_job_id = job.job_id
            task = asyncio.create_task(
                self._execute(job, xlsx_path),
                name=f"report-job-{job.job_id}",
            )
            self._tasks[job.job_id] = task
            task.add_done_callback(self._task_done_callback(job.job_id))
            return job

    def _task_done_callback(self, job_id: str):
        def _cb(_task: asyncio.Task) -> None:
            self._tasks.pop(job_id, None)

        return _cb

    async def _execute(self, job: ReportJob, xlsx_path: Path) -> None:
        job.status = ReportJobStatus.RUNNING

        def on_progress(phase: str, percent: int) -> None:
            job.phase = phase
            job.percent = max(0, min(100, percent))

        try:
            await asyncio.to_thread(
                build_cashflow_report,
                xlsx_path,
                on_progress=on_progress,
            )
            job.status = ReportJobStatus.COMPLETED
            job.percent = 100
            job.phase = "Готово"
            job.message = "Отчёт успешно сформирован"
        except Exception as exc:
            logger.exception("report job failed", extra={"job_id": job.job_id})
            job.status = ReportJobStatus.FAILED
            job.message = str(exc) or "Ошибка формирования отчёта"
            job.phase = "Ошибка"
        finally:
            job.finished_at = datetime.now(timezone.utc)
            if self._active_job_id == job.job_id:
                self._active_job_id = None
