from functools import lru_cache

from fastapi import Request

from ..config_store import ConfigStore
from ..poll_jobs import PollJobManager
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
