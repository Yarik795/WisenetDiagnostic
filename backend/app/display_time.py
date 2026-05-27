from __future__ import annotations

import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .config_store import ConfigStore

logger = logging.getLogger(__name__)

DEFAULT_DISPLAY_TZ = "Europe/Moscow"
_FALLBACK_TZ = ZoneInfo(DEFAULT_DISPLAY_TZ)
_warned_invalid_tz = False


def get_display_tz() -> ZoneInfo:
    global _warned_invalid_tz
    name = (ConfigStore().load().monitoring.display_timezone or "").strip()
    if not name:
        name = DEFAULT_DISPLAY_TZ
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        if not _warned_invalid_tz:
            logger.warning(
                "Неизвестный display_timezone %r, используется %s",
                name,
                DEFAULT_DISPLAY_TZ,
            )
            _warned_invalid_tz = True
        return _FALLBACK_TZ


def to_display(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(get_display_tz())


def format_for_display(value: datetime | None, fmt: str) -> str:
    local = to_display(value)
    if local is None:
        return "—"
    return local.strftime(fmt)
