from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Literal, Optional

from ..sunapi_parsing import RECORD_FRAME_DROP_LOG_TYPE


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


_SIZE_UNIT_RE = re.compile(
    r"^([\d.,]+)\s*(TB|GB|MB|КБ|МБ|ТБ|ГБ)?$",
    re.IGNORECASE,
)


def _disk_mb_value(raw: Any) -> Optional[float]:
    if raw is None:
        return None
    text = str(raw).strip().replace(",", ".")
    if not text:
        return None
    m = _SIZE_UNIT_RE.match(text)
    if m:
        try:
            number = float(m.group(1))
        except ValueError:
            return None
        unit = (m.group(2) or "").upper()
        if unit in ("TB", "ТБ"):
            return number * 1024 * 1024
        if unit in ("GB", "ГБ"):
            return number * 1024
        if unit in ("MB", "МБ", "КБ", "KB"):
            return number
        return number
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def disk_space_mb(disk: dict[str, Any]) -> tuple[Optional[float], Optional[float]]:
    """Used/total in MB from storageinfo slot fields (incl. *InBytes)."""
    used = _disk_mb_value(disk_field(disk, "UsedSpace", "used_space"))
    total = _disk_mb_value(disk_field(disk, "TotalSpace", "total_space"))
    if used is None:
        used_bytes = _disk_mb_value(
            disk_field(disk, "UsedSpaceInBytes", "used_space_in_bytes")
        )
        if used_bytes is not None:
            used = used_bytes / (1024 * 1024)
    if total is None:
        total_bytes = _disk_mb_value(
            disk_field(disk, "TotalSpaceInBytes", "total_space_in_bytes")
        )
        if total_bytes is not None:
            total = total_bytes / (1024 * 1024)
    return used, total


def aggregate_storage_from_disks(
    disks: list[dict[str, Any]],
) -> tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Sum per-slot UsedSpace/TotalSpace when API omits root UsedSpace (XRN-3210/6410).
    Returns (used_mb, total_mb, used_percent).
    """
    used_sum = 0.0
    total_sum = 0.0
    has_slot = False
    for disk in disks:
        used, total = disk_space_mb(disk)
        if total is None or total <= 0:
            continue
        has_slot = True
        used_sum += used or 0.0
        total_sum += total
    if not has_slot or total_sum <= 0:
        return None, None, None
    pct = round(used_sum / total_sum * 100, 1)
    return round(used_sum, 1), round(total_sum, 1), pct


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


def format_cpu_usage(value: Optional[float]) -> str:
    if value is None:
        return "—"
    return f"{float(value):.1f}%"


def format_mbps(value: Optional[float]) -> str:
    if value is None:
        return "—"
    return f"{float(value):.2f} Мбит/с"


def _disk_bool_field(disk: dict[str, Any], *keys: str) -> Optional[bool]:
    for key in keys:
        if key not in disk:
            continue
        raw = disk[key]
        if raw is None:
            continue
        text = str(raw).strip().lower()
        if text in ("true", "1", "yes"):
            return True
        if text in ("false", "0", "no"):
            return False
    return None


def disk_drop_datarate_percent(disk: dict[str, Any]) -> Optional[float]:
    raw = disk_field(
        disk,
        "DropDataratePercent",
        "drop_datarate_percent",
        "DropDatarate",
    )
    if raw is None:
        return None
    try:
        return float(str(raw).replace(",", "."))
    except (TypeError, ValueError):
        return None


def disk_worst_loss_percent(disk: dict[str, Any]) -> Optional[float]:
    raw = disk_field(disk, "WorstLossPercent", "worst_loss_percent", "WorstLoss")
    if raw is None:
        return None
    try:
        return float(str(raw).replace(",", "."))
    except (TypeError, ValueError):
        return None


def disk_format_required(disk: dict[str, Any]) -> bool:
    return _disk_bool_field(disk, "FormatRequired", "format_required") is True


def max_disk_drop_datarate_percent(disks: list[dict[str, Any]]) -> Optional[float]:
    values = [v for d in disks if (v := disk_drop_datarate_percent(d)) is not None]
    return max(values) if values else None


def any_disk_format_required(disks: list[dict[str, Any]]) -> bool:
    return any(disk_format_required(d) for d in disks)


def disk_drop_display(disk: dict[str, Any]) -> str:
    pct = disk_drop_datarate_percent(disk)
    if pct is None:
        return "—"
    return format_percent(pct)


def disk_power_on_hours(disk: dict[str, Any]) -> Optional[str]:
    hours = disk_power_on_hours_raw(disk)
    if hours is None:
        return None
    return f"{hours} ч"


def disk_power_on_hours_raw(disk: dict[str, Any]) -> Optional[int]:
    health = disk.get("Health")
    if isinstance(health, dict):
        for key in (
            "PowerOnHours",
            "power_on_hours",
            "PowerOnDuration",
            "UseTime",
            "use_time",
        ):
            raw = health.get(key)
            if raw is not None and str(raw).strip():
                try:
                    return int(float(str(raw).replace(",", ".")))
                except (TypeError, ValueError):
                    pass
    raw = disk_field(
        disk,
        "PowerOnDuration",
        "power_on_duration",
        "PowerOnHours",
        "power_on_hours",
        "UseTime",
        "use_time",
        "UseDuration",
        "use_duration",
        "OperationTime",
        "operation_time",
    )
    if raw is None:
        return None
    try:
        return int(float(str(raw).replace(",", ".")))
    except (TypeError, ValueError):
        return None


_MONTH_SHORT_RU = (
    "янв.",
    "фев.",
    "мар.",
    "апр.",
    "май",
    "июн.",
    "июл.",
    "авг.",
    "сен.",
    "окт.",
    "ноя.",
    "дек.",
)


def format_manufacture_date(value: Optional[str]) -> str:
    """YYYY-MM из S/N → «сен. 2020»."""
    if not value:
        return "—"
    m = re.match(r"^(\d{4})-(\d{2})$", value.strip())
    if not m:
        return value
    year = int(m.group(1))
    month = int(m.group(2))
    if 1 <= month <= 12:
        return f"{_MONTH_SHORT_RU[month - 1]} {year}"
    return value


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


ARCHIVE_RANGE_MERGE_THRESHOLD_DAYS = 0.05
ARCHIVE_RANGE_DISPLAY_DECIMALS = 1


def archive_range_differs(min_days: float, max_days: float) -> bool:
    """True, если min/max нужно показать как диапазон, а не одно число."""
    if abs(min_days - max_days) < ARCHIVE_RANGE_MERGE_THRESHOLD_DAYS:
        return False
    return round(min_days, ARCHIVE_RANGE_DISPLAY_DECIMALS) != round(
        max_days, ARCHIVE_RANGE_DISPLAY_DECIMALS
    )


def format_archive_range(
    min_days: Optional[float],
    max_days: Optional[float],
    required: int = 30,
) -> str:
    if min_days is None and max_days is None:
        return "—"
    if (
        min_days is not None
        and max_days is not None
        and archive_range_differs(min_days, max_days)
    ):
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


def show_ntp_action_button(metrics) -> bool:
    if metrics is None:
        return False
    if is_manual_sync(metrics.sync_type):
        return True
    return needs_ntp_time_update(metrics)


def ntp_action_button_label(metrics) -> str:
    if is_manual_sync(metrics.sync_type):
        return "Включить NTP"
    return "Обновить NTP"


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


def disk_used_display(disk: dict[str, Any]) -> str:
    used, _ = disk_space_mb(disk)
    return format_mb(used)


def disk_total_display(disk: dict[str, Any]) -> str:
    _, total = disk_space_mb(disk)
    return format_mb(total)


def disk_percent_display(disk: dict[str, Any]) -> str:
    used, total = disk_space_mb(disk)
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


def disk_temperature_celsius(disk: dict[str, Any]) -> Optional[float]:
    for key in ("TemperatureCelsius", "temperature_celsius"):
        val = disk.get(key)
        if val is not None and str(val).strip() != "":
            try:
                return float(val)
            except (TypeError, ValueError):
                pass
    temp = disk_field(disk, "Temperature", "temperature", "TemperatureInCelsius")
    if temp:
        m = re.search(r"\d+", temp)
        if m:
            return float(m.group())
    health = disk.get("Health")
    if isinstance(health, dict) and health.get("TemperatureInCelsius") is not None:
        try:
            return float(health["TemperatureInCelsius"])
        except (TypeError, ValueError):
            pass
    return None


def max_disk_temperature_celsius_from_disks(disks: list[dict[str, Any]]) -> Optional[float]:
    values = [t for d in disks if (t := disk_temperature_celsius(d)) is not None]
    return max(values) if values else None


def max_disk_temperature_celsius(disks_json: Optional[str]) -> Optional[float]:
    return max_disk_temperature_celsius_from_disks(parse_disks_json(disks_json))


def max_disk_temperature(disks_json: Optional[str]) -> Optional[str]:
    temp = max_disk_temperature_celsius(disks_json)
    if temp is None:
        return None
    return f"{int(temp) if temp == int(temp) else temp:.1f} °C"


def active_fan_event_labels(events: dict[str, bool]) -> list[str]:
    return active_system_event_labels(events, labels=FAN_EVENT_LABELS)


STORAGE_SYSTEM_EVENT_KEYS: tuple[str, ...] = (
    "HDDFail",
    "HDDError",
    "HDDNone",
    "HDDFull",
)

SYSTEM_EVENT_ERROR_LABELS: dict[str, str] = {
    "CPUFanError": "Вентилятор CPU",
    "FrameFanError": "Вентилятор корпуса",
    "FanError": "Ошибка вентилятора",
    "LeftFanError": "Левый вентилятор",
    "RightFanError": "Правый вентилятор",
    "HDDFail": "Сбой HDD",
    "HDDError": "Ошибка HDD",
    "HDDNone": "Накопитель отсутствует",
    "HDDFull": "Диск заполнен",
    "BatteryFail": "Сбой батареи",
    "MemoryError": "Ошибка памяти",
    "RecordingError": "Ошибка записи",
    "iSCSIDisconnect": "Отключение iSCSI",
}

FAN_EVENT_LABELS: dict[str, str] = {
    "CPUFanError": "Вентилятор CPU",
    "FrameFanError": "Вентилятор корпуса",
    "FanError": "Ошибка вентилятора",
    "LeftFanError": "Левый вентилятор",
    "RightFanError": "Правый вентилятор",
}

SYSTEM_EVENT_WARN_LABELS: dict[str, str] = {
    "CpuOverload": "Перегрузка CPU",
    "NetCamTrafficOverFlow": "Перегрузка трафика камер",
    "NetTxTrafficOverflow": "Перегрузка исходящего трафика",
    "NewFWAvailable": "Доступно обновление ПО",
    "BeingUpdate": "Идёт обновление",
    "OverwriteDecoding": "Конфликт декодирования и перезаписи",
    "AMDLoadFail": "Сбой загрузки AMD",
    "HDDCountChanged": "Изменено число накопителей",
    "USBHDDConnect": "Подключён USB-накопитель",
    "RecordFrameDrop": "Потеря кадров записи",
}


def parse_system_events_json(raw: Optional[str]) -> dict[str, bool]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: bool(v) for k, v in data.items()}


def parse_system_event_times_json(raw: Optional[str]) -> dict[str, str]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(k): str(v) for k, v in data.items() if v}


def effective_system_events(
    events: dict[str, bool],
    times: Optional[dict[str, str]] = None,
) -> dict[str, bool]:
    """RecordFrameDrop учитывается только при подтверждённой дате в systemlog (не залипший флаг)."""
    result = dict(events)
    if result.get(RECORD_FRAME_DROP_LOG_TYPE) and not (times or {}).get(
        RECORD_FRAME_DROP_LOG_TYPE
    ):
        result[RECORD_FRAME_DROP_LOG_TYPE] = False
    return result


def format_nvr_systemlog_timestamp(raw: str) -> str:
    raw = raw.strip()
    for fmt, size in (("%Y-%m-%d %H:%M:%S", 19), ("%Y-%m-%d %H:%M", 16)):
        try:
            dt = datetime.strptime(raw[:size], fmt)
            return dt.strftime("%d.%m.%Y %H:%M")
        except ValueError:
            continue
    return raw


def format_system_event_label(
    key: str,
    base_label: str,
    events: dict[str, bool],
    times: dict[str, str],
) -> str:
    if key == RECORD_FRAME_DROP_LOG_TYPE and events.get(key):
        timestamp = times.get(key)
        if timestamp:
            return f"{base_label} ({format_nvr_systemlog_timestamp(timestamp)})"
    return base_label


def active_storage_system_event_labels(events: dict[str, bool]) -> list[str]:
    return active_system_event_labels(
        events,
        labels={
            k: SYSTEM_EVENT_ERROR_LABELS[k]
            for k in STORAGE_SYSTEM_EVENT_KEYS
            if k in SYSTEM_EVENT_ERROR_LABELS
        },
    )


def active_system_event_labels(
    events: dict[str, bool],
    *,
    labels: dict[str, str],
    times: Optional[dict[str, str]] = None,
) -> list[str]:
    event_times = times or {}
    result: list[str] = []
    for key, label in labels.items():
        if events.get(key):
            result.append(
                format_system_event_label(key, label, events, event_times)
            )
    return result


_COVERED_SYSTEM_EVENT_KEYS: frozenset[str] = frozenset(STORAGE_SYSTEM_EVENT_KEYS) | frozenset(
    FAN_EVENT_LABELS
)


def uncategorized_system_event_problems(
    events: dict[str, bool],
    times: Optional[dict[str, str]] = None,
) -> tuple[Optional[Literal["error", "warn"]], list[str]]:
    """Активные системные события, не покрытые классификаторами накопителей и вентиляторов."""
    event_times = times or {}
    events = effective_system_events(events, event_times)
    error_labels: list[str] = []
    warn_labels: list[str] = []
    for key, label in SYSTEM_EVENT_ERROR_LABELS.items():
        if key not in _COVERED_SYSTEM_EVENT_KEYS and events.get(key):
            error_labels.append(
                format_system_event_label(key, label, events, event_times)
            )
    for key, label in SYSTEM_EVENT_WARN_LABELS.items():
        if events.get(key):
            warn_labels.append(
                format_system_event_label(key, label, events, event_times)
            )
    labels = error_labels + warn_labels
    if error_labels:
        return "error", labels
    if warn_labels:
        return "warn", labels
    return None, []


def system_events_display(
    system_events_json: Optional[str],
    system_event_times_json: Optional[str] = None,
) -> str:
    events = parse_system_events_json(system_events_json)
    times = parse_system_event_times_json(system_event_times_json)
    events = effective_system_events(events, times)
    if not events:
        return "Аппаратные события: нет данных"
    active = active_system_event_labels(
        events,
        labels={**SYSTEM_EVENT_ERROR_LABELS, **SYSTEM_EVENT_WARN_LABELS},
        times=times,
    )
    if not active:
        return "Аппаратные события: норма"
    return "; ".join(active)
