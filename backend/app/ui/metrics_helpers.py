from __future__ import annotations

import json
import re
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


def format_archive_days_value(days: Optional[float]) -> str:
    if days is None:
        return "—"
    return f"{days:.1f} сут."


def format_archive_days(days: Optional[float], required: int = 30) -> str:
    if days is None:
        return "—"
    text = format_archive_days_value(days)
    if days < required:
        return f"{text} (норма {required})"
    return text


def format_archive_range(
    min_days: Optional[float],
    max_days: Optional[float],
    required: int = 30,
) -> str:
    if min_days is None and max_days is None:
        return "—"
    if min_days is not None and max_days is not None and min_days != max_days:
        text = f"{min_days:.1f}-{max_days:.1f} сут."
        if min_days < required:
            return f"{text} (норма {required})"
        return text
    value = max_days if max_days is not None else min_days
    return format_archive_days(value, required)


def is_manual_sync(sync_type: Optional[str]) -> bool:
    return (sync_type or "").strip().lower() == "manual"


NTP_UPDATE_SKEW_THRESHOLD_SECONDS = 1.0


def needs_ntp_time_update(
    metrics,
    threshold: float = NTP_UPDATE_SKEW_THRESHOLD_SECONDS,
) -> bool:
    if metrics is None:
        return False
    skew = metrics.time_skew_seconds
    if skew is None:
        return False
    return skew > threshold


def sync_type_label(sync_type: Optional[str]) -> str:
    if not sync_type:
        return "—"
    mapping = {
        "manual": "Ручная",
        "ntp": "NTP",
        "gps": "GPS",
    }
    return mapping.get(sync_type.strip().lower(), sync_type)


def sync_type_badge_class(sync_type: Optional[str]) -> str:
    key = (sync_type or "").strip().lower()
    if key == "manual":
        return "sync-badge sync-badge--manual"
    if key == "ntp":
        return "sync-badge sync-badge--ntp"
    if key == "gps":
        return "sync-badge sync-badge--gps"
    return "sync-badge"


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


def disk_temperature_display(disk: dict[str, Any]) -> str:
    for key in ("TemperatureCelsius", "temperature_celsius"):
        val = disk.get(key)
        if val is not None and str(val).strip() != "":
            return f"{val} °C"
    temp = disk_field(
        disk,
        "Temperature",
        "temperature",
        "TemperatureInCelsius",
    )
    if temp:
        if temp.isdigit():
            return f"{temp} °C"
        return temp
    health = disk.get("Health")
    if isinstance(health, dict) and health.get("TemperatureInCelsius") is not None:
        return f"{health['TemperatureInCelsius']} °C"
    return "—"


def max_disk_temperature(disks_json: Optional[str]) -> Optional[str]:
    disks = parse_disks_json(disks_json)
    temps: list[str] = []
    for disk in disks:
        t = disk_temperature_display(disk)
        if t != "—":
            temps.append(t)
    if not temps:
        return None
    def _temp_value(label: str) -> int:
        m = re.search(r"\d+", label)
        return int(m.group()) if m else 0

    return max(temps, key=_temp_value)
