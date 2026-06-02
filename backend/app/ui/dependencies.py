from functools import lru_cache

from fastapi import Request

from ..config_store import ConfigStore
from ..poll_jobs import PollJobManager
from ..scheduler import MonitoringScheduler
from ..state_store import StateStore


@lru_cache
def get_state_store() -> StateStore:
    store = StateStore()
    store.init_db()
    return store


def get_store() -> ConfigStore:
    return ConfigStore()


def get_poll_job_manager(request: Request) -> PollJobManager:
    mgr = getattr(request.app.state, "poll_job_manager", None)
    if mgr is None:
        mgr = PollJobManager()
        request.app.state.poll_job_manager = mgr
    return mgr


def get_monitoring_scheduler(request: Request) -> MonitoringScheduler:
    scheduler = getattr(request.app.state, "scheduler", None)
    if scheduler is None:
        poll_jobs = get_poll_job_manager(request)
        scheduler = MonitoringScheduler(ConfigStore(), get_state_store(), poll_jobs=poll_jobs)
        request.app.state.scheduler = scheduler
    return scheduler
