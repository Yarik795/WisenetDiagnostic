from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from .config_store import ConfigStore
from .monitoring import run_inventory_cycle, run_poll_cycle
from .state_store import StateStore

logger = logging.getLogger("scheduler")


class MonitoringScheduler:
    def __init__(self, config_store: ConfigStore, state_store: StateStore) -> None:
        self.config_store = config_store
        self.state_store = state_store
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()
        self._last_full: datetime | None = None
        self._last_inventory: datetime | None = None

    def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._stop.clear()
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        self._stop.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _loop(self) -> None:
        logger.info("monitoring scheduler started")
        while not self._stop.is_set():
            try:
                await self._tick()
            except Exception:
                logger.exception("scheduler tick failed")
            config = self.config_store.load()
            interval = config.monitoring.poll_interval_minutes * 60
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=interval)
                break
            except asyncio.TimeoutError:
                continue
        logger.info("monitoring scheduler stopped")

    async def _tick(self) -> None:
        now = datetime.now(timezone.utc)
        config = self.config_store.load()
        full_min = config.monitoring.full_poll_interval_minutes
        inventory_hours = 24

        do_inventory = (
            self._last_inventory is None
            or (now - self._last_inventory).total_seconds() >= inventory_hours * 3600
        )
        if do_inventory:
            await run_inventory_cycle(self.config_store, self.state_store)
            self._last_inventory = now
            self._last_full = now
            return

        do_full = (
            self._last_full is None
            or (now - self._last_full).total_seconds() >= full_min * 60
        )
        await run_poll_cycle(
            self.config_store,
            self.state_store,
            include_inventory=do_full,
        )
        if do_full:
            self._last_full = now
