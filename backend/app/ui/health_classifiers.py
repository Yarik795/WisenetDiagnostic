from __future__ import annotations

from typing import Literal, Optional

from ..models import MonitoringSettings, Recorder
from ..state_store import RecorderMetricsRow
from .metrics_helpers import (
    SYSTEM_EVENT_ERROR_LABELS,
    active_fan_event_labels,
    disk_field,
    is_manual_sync,
    max_disk_temperature_celsius,
    parse_disks_json,
    parse_system_events_json,
    sync_type_label,
)
from .time_dashboard import TimeCategory, classify_time_health

HealthCategory = Literal[
    "time", "temperature", "storage", "fans", "channels", "archive"
]
HealthCategoryStatus = Literal["ok", "warn", "error", "unknown"]

CATEGORY_LABELS: dict[HealthCategory, str] = {
    "time": "Время / NTP",
    "temperature": "Температура HDD",
    "storage": "Накопители",
    "fans": "Вентиляторы",
    "channels": "Каналы",
    "archive": "Глубина архива",
}

BADGE_CODES: dict[HealthCategory, str] = {
    "time": "NTP",
    "temperature": "TEMP",
    "storage": "HDD",
    "fans": "FAN",
    "channels": "CH",
    "archive": "ARCH",
}

_DISK_ERROR_STATUSES = frozenset({"error", "fail", "full", "failed"})


def _recorder_has_poll_data(
    recorder: Recorder,
    metrics: Optional[RecorderMetricsRow],
) -> bool:
    if not recorder.enabled:
        return False
    if metrics is None or metrics.last_polled_at is None:
        return False
    return metrics.device_online


def classify_temperature_health(
    recorder: Recorder,
    metrics: Optional[RecorderMetricsRow],
    settings: MonitoringSettings,
) -> tuple[HealthCategoryStatus, str]:
    if not _recorder_has_poll_data(recorder, metrics):
        return "unknown", "Нет данных опроса"
    assert metrics is not None
    max_temp = max_disk_temperature_celsius(metrics.disks_json)
    if max_temp is None:
        return "unknown", "Температура HDD не возвращается устройством"
    if max_temp >= settings.hdd_temperature_error_celsius:
        return "error", f"Температура HDD {max_temp:.0f} °C (критично ≥ {settings.hdd_temperature_error_celsius} °C)"
    if max_temp >= settings.hdd_temperature_warn_celsius:
        return "warn", f"Температура HDD {max_temp:.0f} °C (предупреждение ≥ {settings.hdd_temperature_warn_celsius} °C)"
    return "ok", f"Температура HDD {max_temp:.0f} °C"


def classify_storage_health(
    recorder: Recorder,
    metrics: Optional[RecorderMetricsRow],
    settings: MonitoringSettings,
) -> tuple[HealthCategoryStatus, str]:
    if not _recorder_has_poll_data(recorder, metrics):
        return "unknown", "Нет данных опроса"
    assert metrics is not None
    reasons: list[str] = []
    status: HealthCategoryStatus = "ok"

    storage_st = (metrics.storage_status or "").strip().lower()
    if storage_st in _DISK_ERROR_STATUSES:
        status = "error"
        reasons.append(f"Статус массива: {metrics.storage_status}")

    pct = metrics.storage_used_percent
    if pct is not None:
        if pct >= settings.disk_usage_error_percent:
            status = "error"
            reasons.append(f"Заполнение {pct:.1f}%")
        elif pct >= settings.disk_usage_warn_percent:
            if status != "error":
                status = "warn"
            reasons.append(f"Заполнение {pct:.1f}%")

    for disk in parse_disks_json(metrics.disks_json):
        disk_status = (disk_field(disk, "Status", "status") or "").strip().lower()
        if disk_status in _DISK_ERROR_STATUSES:
            status = "error"
            slot = disk.get("Storage") or disk.get("storage") or disk.get("Slot") or "?"
            reasons.append(f"Слот {slot}: {disk_field(disk, 'Status', 'status')}")

    events = parse_system_events_json(metrics.system_events_json)
    for key in ("HDDFail", "HDDError", "HDDFull"):
        if events.get(key):
            status = "error"
            reasons.append(SYSTEM_EVENT_ERROR_LABELS.get(key, key))

    if not reasons:
        if pct is not None:
            return "ok", f"Заполнение {pct:.1f}%"
        return "unknown", "Нет данных по накопителям"
    return status, "; ".join(dict.fromkeys(reasons))


def classify_fans_health(
    recorder: Recorder,
    metrics: Optional[RecorderMetricsRow],
    settings: MonitoringSettings,
) -> tuple[HealthCategoryStatus, str]:
    del settings
    if not _recorder_has_poll_data(recorder, metrics):
        return "unknown", "Нет данных опроса"
    assert metrics is not None
    events = parse_system_events_json(metrics.system_events_json)
    if not events:
        return "unknown", "События вентиляторов не возвращаются устройством"
    labels = active_fan_event_labels(events)
    if labels:
        return "error", "; ".join(labels)
    return "ok", "Вентиляторы в норме"


def classify_channels_health(
    recorder: Recorder,
    metrics: Optional[RecorderMetricsRow],
    settings: MonitoringSettings,
) -> tuple[HealthCategoryStatus, str]:
    if not _recorder_has_poll_data(recorder, metrics):
        return "unknown", "Нет данных опроса"
    assert metrics is not None
    total = metrics.channel_count
    if total == 0:
        return "unknown", "Каналы не инвентаризированы"

    err = metrics.channels_error
    warn = metrics.channels_warn
    unknown = metrics.channels_unknown
    error_pct = (err / total * 100) if total else 0.0

    if err > 0 and error_pct >= settings.channels_error_threshold_percent:
        return (
            "error",
            f"Неисправно {err} из {total} каналов ({error_pct:.0f}%)",
        )
    if err > 0:
        return "warn", f"Неисправно {err} из {total} каналов"
    if warn > 0:
        return "warn", f"Деградация на {warn} из {total} каналов"
    if unknown == total:
        return "unknown", "Нет данных по каналам"
    return "ok", f"Исправно {metrics.channels_ok} из {total} каналов"


def classify_archive_health(
    recorder: Recorder,
    metrics: Optional[RecorderMetricsRow],
    settings: MonitoringSettings,
) -> tuple[HealthCategoryStatus, str]:
    if not _recorder_has_poll_data(recorder, metrics):
        return "unknown", "Нет данных опроса"
    assert metrics is not None
    min_days = metrics.archive_min_days
    if min_days is None:
        min_days = metrics.archive_days
    if min_days is None:
        return "unknown", "Глубина архива не определена"

    required = settings.archive_days_required
    critical = settings.archive_days_error_threshold
    if min_days < critical:
        return (
            "error",
            f"Глубина архива {min_days:.1f} сут. (критично < {critical} сут.)",
        )
    if min_days < required:
        max_days = metrics.archive_max_days or min_days
        if max_days != min_days:
            return (
                "warn",
                f"Глубина архива {min_days:.1f}-{max_days:.1f} сут. (норма {required} сут.)",
            )
        return "warn", f"Глубина архива {min_days:.1f} сут. (норма {required} сут.)"
    return "ok", f"Глубина архива {min_days:.1f} сут."


def classify_time_category(
    recorder: Recorder,
    metrics: Optional[RecorderMetricsRow],
    settings: MonitoringSettings,
) -> tuple[HealthCategoryStatus, str]:
    cat: TimeCategory = classify_time_health(recorder, metrics, settings)
    if cat == "error":
        if metrics and (metrics.ntp_status or "").strip().lower() == "fail":
            return "error", "NTP: Fail"
        if metrics and is_manual_sync(metrics.sync_type):
            return "error", f"Режим: {sync_type_label(metrics.sync_type)}"
        if metrics and metrics.sync_type:
            sync = metrics.sync_type.strip().lower()
            if sync and sync != "ntp":
                return "error", f"Режим: {sync_type_label(metrics.sync_type)}"
        skew = metrics.time_skew_seconds if metrics else None
        if skew is not None:
            return "error", f"Расхождение времени {int(skew)} с"
        return "error", "Критичное расхождение времени"
    if cat == "warn":
        skew = metrics.time_skew_seconds if metrics else None
        if skew is not None:
            return "warn", f"Расхождение времени {int(skew)} с"
        return "warn", "Деградация времени"
    if cat == "unknown":
        return "unknown", "Нет данных по времени"
    return "ok", "Время и NTP в норме"


def classify_category(
    category: HealthCategory,
    recorder: Recorder,
    metrics: Optional[RecorderMetricsRow],
    settings: MonitoringSettings,
) -> tuple[HealthCategoryStatus, str]:
    classifiers = {
        "time": classify_time_category,
        "temperature": classify_temperature_health,
        "storage": classify_storage_health,
        "fans": classify_fans_health,
        "channels": classify_channels_health,
        "archive": classify_archive_health,
    }
    return classifiers[category](recorder, metrics, settings)


def is_problem_status(status: HealthCategoryStatus) -> bool:
    return status in ("warn", "error")


def worst_category_status(*statuses: HealthCategoryStatus) -> HealthCategoryStatus:
    order = {"error": 3, "warn": 2, "unknown": 1, "ok": 0}
    if not statuses:
        return "unknown"
    return max(statuses, key=lambda s: order.get(s, 0))


def recorder_category_statuses(
    recorder: Recorder,
    metrics: Optional[RecorderMetricsRow],
    settings: MonitoringSettings,
) -> dict[HealthCategory, HealthCategoryStatus]:
    return {
        cat: classify_category(cat, recorder, metrics, settings)[0]
        for cat in CATEGORY_LABELS
    }


def recorder_problem_badges(
    recorder: Recorder,
    metrics: Optional[RecorderMetricsRow],
    settings: MonitoringSettings,
) -> list[tuple[str, str, str]]:
    """(code, css_class, title) for compact badges."""
    badges: list[tuple[str, str, str]] = []
    for cat, label in CATEGORY_LABELS.items():
        status, reason = classify_category(cat, recorder, metrics, settings)
        if not is_problem_status(status):
            continue
        code = BADGE_CODES[cat]
        css = f"health-badge health-badge--{status}"
        badges.append((code, css, f"{label}: {reason}"))
    return badges
