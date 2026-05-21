from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

from ..models import MonitoringSettings, Recorder
from ..state_store import RecorderMetricsRow
from .grouping import effective_status
from .health_classifiers import (
    CATEGORY_LABELS,
    HealthCategory,
    HealthCategoryStatus,
    classify_category,
    is_problem_status,
    worst_category_status,
)
from .time_dashboard import aggregate_time_stats

SeverityCategory = Literal["ok", "warn", "error", "unknown"]


@dataclass
class CategoryKpi:
    category: HealthCategory
    label: str
    ok: int = 0
    warn: int = 0
    error: int = 0
    unknown: int = 0

    @property
    def worst_status(self) -> HealthCategoryStatus:
        if self.error > 0:
            return "error"
        if self.warn > 0:
            return "warn"
        if self.unknown > 0 and self.ok == 0:
            return "unknown"
        return "ok"

    @property
    def problem_count(self) -> int:
        return self.warn + self.error

    @property
    def total(self) -> int:
        return self.ok + self.warn + self.error + self.unknown


@dataclass
class HealthDashboardStats:
    total_enabled: int = 0
    ok: int = 0
    warn: int = 0
    error: int = 0
    unknown: int = 0
    has_problems: bool = False
    category_kpis: list[CategoryKpi] = field(default_factory=list)
    time_fixable: int = 0

    @property
    def stacked_segments(self) -> list[tuple[str, int, str]]:
        return [
            ("ok", self.ok, "time-stack-ok"),
            ("warn", self.warn, "time-stack-warn"),
            ("error", self.error, "time-stack-error"),
            ("unknown", self.unknown, "time-stack-unknown"),
        ]

    @property
    def stacked_total(self) -> int:
        return self.ok + self.warn + self.error + self.unknown


@dataclass
class HealthProblemRow:
    recorder: Recorder
    metrics: Optional[RecorderMetricsRow]
    category: HealthCategory
    category_label: str
    status: HealthCategoryStatus
    value_display: str
    reason: str
    effective: str
    polled_at_display: str = "—"


def _severity_from_effective(effective: str) -> SeverityCategory:
    if effective in ("error", "offline"):
        return "error"
    if effective == "warn":
        return "warn"
    if effective in ("ok", "online"):
        return "ok"
    return "unknown"


def aggregate_health_stats(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
) -> HealthDashboardStats:
    stats = HealthDashboardStats()
    kpis = {cat: CategoryKpi(category=cat, label=label) for cat, label in CATEGORY_LABELS.items()}
    time_stats = aggregate_time_stats(recorders, metrics_map, settings)
    stats.time_fixable = time_stats.fixable

    for rec in recorders:
        if not rec.enabled:
            continue
        stats.total_enabled += 1
        metrics = metrics_map.get(rec.id)
        effective = effective_status(rec, metrics)
        sev = _severity_from_effective(effective)
        if sev == "ok":
            stats.ok += 1
        elif sev == "warn":
            stats.warn += 1
            stats.has_problems = True
        elif sev == "error":
            stats.error += 1
            stats.has_problems = True
        else:
            stats.unknown += 1

        for cat, kpi in kpis.items():
            cat_status, _ = classify_category(cat, rec, metrics, settings)
            if cat_status == "ok":
                kpi.ok += 1
            elif cat_status == "warn":
                kpi.warn += 1
            elif cat_status == "error":
                kpi.error += 1
            else:
                kpi.unknown += 1

    stats.category_kpis = [kpis[cat] for cat in CATEGORY_LABELS]
    if any(k.problem_count > 0 for k in stats.category_kpis):
        stats.has_problems = True
    return stats


def list_health_problem_rows(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
    *,
    problems_only: bool = True,
    search: str = "",
    category_filter: Optional[HealthCategory] = None,
) -> list[HealthProblemRow]:
    q = search.strip().lower()
    rows: list[HealthProblemRow] = []
    for rec in recorders:
        if not rec.enabled:
            continue
        metrics = metrics_map.get(rec.id)
        for cat, label in CATEGORY_LABELS.items():
            if category_filter and cat != category_filter:
                continue
            status, reason = classify_category(cat, rec, metrics, settings)
            if problems_only and not is_problem_status(status):
                continue
            if q:
                hay = f"{rec.object_name} {rec.host} {rec.name or ''} {label} {reason}".lower()
                if q not in hay:
                    continue
            polled = "—"
            if metrics and metrics.last_polled_at:
                polled = metrics.last_polled_at.strftime("%Y-%m-%d %H:%M")
            rows.append(
                HealthProblemRow(
                    recorder=rec,
                    metrics=metrics,
                    category=cat,
                    category_label=label,
                    status=status,
                    value_display=_value_display(cat, metrics, settings),
                    reason=reason,
                    effective=effective_status(rec, metrics),
                    polled_at_display=polled,
                )
            )

    def _sort_key(row: HealthProblemRow) -> tuple:
        status_order = {"error": 0, "warn": 1, "unknown": 2, "ok": 3}
        return (
            status_order.get(row.status, 9),
            row.recorder.object_name.lower(),
            row.recorder.host,
            CATEGORY_LABELS[row.category],
        )

    rows.sort(key=_sort_key)
    return rows


def _value_display(
    category: HealthCategory,
    metrics: Optional[RecorderMetricsRow],
    settings: MonitoringSettings,
) -> str:
    if metrics is None:
        return "—"
    if category == "temperature":
        from .metrics_helpers import max_disk_temperature

        return max_disk_temperature(metrics.disks_json) or "—"
    if category == "storage":
        parts = []
        if metrics.storage_used_percent is not None:
            parts.append(f"{metrics.storage_used_percent:.1f}%")
        if metrics.storage_status:
            parts.append(metrics.storage_status)
        return " · ".join(parts) if parts else "—"
    if category == "channels":
        from .metrics_helpers import format_channel_counts

        return format_channel_counts(
            metrics.channel_count,
            metrics.channels_ok,
            metrics.channels_warn,
            metrics.channels_error,
            metrics.channels_unknown,
        )
    if category == "archive":
        from .metrics_helpers import format_archive_range

        return format_archive_range(
            metrics.archive_min_days,
            metrics.archive_max_days,
            settings.archive_days_required,
        )
    if category == "time":
        from .metrics_helpers import format_skew

        skew = format_skew(metrics.time_skew_seconds)
        ntp = metrics.ntp_status or "—"
        return f"Δt {skew}, NTP {ntp}"
    if category == "fans":
        from .metrics_helpers import active_fan_event_labels, parse_system_events_json

        events = parse_system_events_json(metrics.system_events_json)
        labels = active_fan_event_labels(events)
        return "; ".join(labels) if labels else "норма"
    return "—"


def object_health_problem_count(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
) -> int:
    count = 0
    for rec in recorders:
        if not rec.enabled:
            continue
        metrics = metrics_map.get(rec.id)
        statuses = [
            classify_category(cat, rec, metrics, settings)[0]
            for cat in CATEGORY_LABELS
        ]
        if any(is_problem_status(s) for s in statuses):
            count += 1
    return count


def object_category_problem_counts(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
) -> dict[HealthCategory, int]:
    counts = {cat: 0 for cat in CATEGORY_LABELS}
    for rec in recorders:
        if not rec.enabled:
            continue
        metrics = metrics_map.get(rec.id)
        for cat in CATEGORY_LABELS:
            status, _ = classify_category(cat, rec, metrics, settings)
            if is_problem_status(status):
                counts[cat] += 1
    return counts


def health_dashboard_context(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
    *,
    ntp_server: str = "",
    compact: bool = False,
    problems_only: bool = True,
    search: str = "",
    category_filter: Optional[HealthCategory] = None,
) -> dict:
    stats = aggregate_health_stats(recorders, metrics_map, settings)
    problem_rows = list_health_problem_rows(
        recorders,
        metrics_map,
        settings,
        problems_only=problems_only,
        search=search,
        category_filter=category_filter,
    )
    return {
        "health_stats": stats,
        "health_problem_rows": problem_rows,
        "health_ntp_server": (ntp_server or "").strip() or "—",
        "health_dashboard_compact": compact,
        "health_default_expanded": stats.has_problems,
        "health_category_filter": category_filter,
        "health_temp_warn": settings.hdd_temperature_warn_celsius,
        "health_temp_error": settings.hdd_temperature_error_celsius,
        "health_archive_required": settings.archive_days_required,
        "health_archive_critical": settings.archive_days_error_threshold,
        "health_channels_threshold": settings.channels_error_threshold_percent,
    }
