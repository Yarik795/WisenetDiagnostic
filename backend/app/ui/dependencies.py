from functools import lru_cache

from ..config_store import ConfigStore
from ..state_store import StateStore


@lru_cache
def get_state_store() -> StateStore:
    store = StateStore()
    store.init_db()
    return store


def get_store() -> ConfigStore:
    return ConfigStore()
