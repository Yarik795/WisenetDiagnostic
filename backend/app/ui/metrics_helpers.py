from __future__ import annotations

import json
from typing import Any, Optional


def parse_disks_json(raw: Optional[str]) -> list[dict[str, Any]]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [d for d in data if isinstance(d, dict)]


def format_mb(value: Optional[float]) -> str:
    if value is None:
        return "—"
    mb = float(value)
    if mb >= 1024 * 1024:
        return f"{mb / (1024 * 1024):.1f} ПБ"
    if mb >= 1024:
        return f"{mb / 1024:.1f} ТБ"
    return f"{mb:.0f} МБ"


def format_percent(value: Optional[float]) -> str:
    if value is None:
        return "—"
    return f"{float(value):.1f}%"


def format_archive_days(days: Optional[float], required: int = 30) -> str:
    if days is None:
        return "—"
    text = f"{days:.1f} сут."
    if days < required:
        return f"{text} (норма {required})"
    return text


def format_skew(seconds: Optional[float]) -> str:
    if seconds is None:
        return "—"
    s = int(seconds)
    if s < 60:
        return f"{s} с"
    return f"{s // 60} мин {s % 60} с"


def format_channel_counts(
    total: int,
    ok: int,
    warn: int,
    error: int,
    unknown: int,
) -> str:
    if total == 0:
        return "нет данных"
    parts = [f"{total} кан."]
    if ok:
        parts.append(f"{ok} ок")
    if warn:
        parts.append(f"{warn} дегр.")
    if error:
        parts.append(f"{error} отказ")
    if unknown:
        parts.append(f"{unknown} ?")
    return " · ".join(parts)


def format_bool_ru(value: Optional[bool], true_label: str = "Да", false_label: str = "Нет") -> str:
    if value is None:
        return "—"
    return true_label if value else false_label


def disk_slot(disk: dict[str, Any]) -> str:
    for key in ("Storage", "storage", "Slot", "slot"):
        if key in disk and disk[key] is not None:
            return str(disk[key])
    return "—"


def disk_field(disk: dict[str, Any], *keys: str) -> Optional[str]:
    for key in keys:
        if key in disk and disk[key] not in (None, ""):
            return str(disk[key])
    return None


def _disk_number(disk: dict[str, Any], *keys: str) -> Optional[float]:
    raw = disk_field(disk, *keys)
    if raw is None:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def disk_used_display(disk: dict[str, Any]) -> str:
    return format_mb(_disk_number(disk, "UsedSpace", "used_space"))


def disk_total_display(disk: dict[str, Any]) -> str:
    return format_mb(_disk_number(disk, "TotalSpace", "total_space"))


def disk_percent_display(disk: dict[str, Any]) -> str:
    used = _disk_number(disk, "UsedSpace", "used_space")
    total = _disk_number(disk, "TotalSpace", "total_space")
    if used is None or total is None or total <= 0:
        return "—"
    return format_percent(used / total * 100)
