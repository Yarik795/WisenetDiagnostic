from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, Optional

from ..models import MonitoringSettings, Recorder
from ..state_store import RecorderMetricsRow
from .grouping import effective_status
from .health_classifiers import (
    CATEGORY_LABELS,
    HealthCategory,
    HealthCategoryStatus,
    classify_category,
    is_problem_status,
)
from .time_dashboard import time_dashboard_context


@dataclass
class CategoryDashboardStats:
    total_enabled: int = 0
    ok: int = 0
    warn: int = 0
    error: int = 0
    unknown: int = 0
    has_problems: bool = False

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


@dataclass
class CategoryDashboardSection:
    category: HealthCategory
    title: str
    element_id: str
    default_expanded: bool
    meta_text: str = ""
    is_time: bool = False
    stats: Optional[CategoryDashboardStats] = None
    problem_rows: list[HealthProblemRow] = field(default_factory=list)
    time_context: Optional[SimpleNamespace] = None


def aggregate_category_stats(
    category: HealthCategory,
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
) -> CategoryDashboardStats:
    stats = CategoryDashboardStats()
    for rec in recorders:
        if not rec.enabled:
            continue
        stats.total_enabled += 1
        metrics = metrics_map.get(rec.id)
        cat_status, _ = classify_category(category, rec, metrics, settings)
        if cat_status == "ok":
            stats.ok += 1
        elif cat_status == "warn":
            stats.warn += 1
            stats.has_problems = True
        elif cat_status == "error":
            stats.error += 1
            stats.has_problems = True
        else:
            stats.unknown += 1
    return stats


def list_health_problem_rows(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
    *,
    problems_only: bool = True,
    search: str = "",
    category_filter: HealthCategory,
) -> list[HealthProblemRow]:
    q = search.strip().lower()
    label = CATEGORY_LABELS[category_filter]
    rows: list[HealthProblemRow] = []
    for rec in recorders:
        if not rec.enabled:
            continue
        metrics = metrics_map.get(rec.id)
        status, reason = classify_category(category_filter, rec, metrics, settings)
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
                category=category_filter,
                category_label=label,
                status=status,
                value_display=_value_display(category_filter, metrics, settings),
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


def category_meta_text(category: HealthCategory, settings: MonitoringSettings) -> str:
    if category == "temperature":
        return (
            f"Предупреждение ≥ {settings.hdd_temperature_warn_celsius} °C"
            f" · критично ≥ {settings.hdd_temperature_error_celsius} °C"
        )
    if category == "storage":
        return "Сбои HDD (HDDFail, HDDError); заполнение диска не контролируется"
    if category == "fans":
        return "Источник: SystemEvent (CPUFanError, FrameFanError и др.)"
    if category == "channels":
        return (
            f"Массовый отказ каналов: ≥ {settings.channels_error_threshold_percent}%"
            " неисправных"
        )
    if category == "archive":
        return (
            f"Норматив: {settings.archive_days_required} сут."
            f" · критично < {settings.archive_days_error_threshold} сут."
        )
    return ""


def build_category_sections(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
    *,
    ntp_server: str = "",
    compact: bool = False,
    problems_only: bool = True,
    search: str = "",
) -> list[CategoryDashboardSection]:
    sections: list[CategoryDashboardSection] = []
    for cat, label in CATEGORY_LABELS.items():
        if cat == "time":
            time_ctx = time_dashboard_context(
                recorders,
                metrics_map,
                settings,
                ntp_server=ntp_server,
                compact=compact,
                problems_only=problems_only,
                search=search,
            )
            sections.append(
                CategoryDashboardSection(
                    category="time",
                    title=label,
                    element_id="time-dashboard",
                    default_expanded=time_ctx["time_default_expanded"],
                    is_time=True,
                    time_context=SimpleNamespace(**time_ctx),
                )
            )
            continue

        stats = aggregate_category_stats(cat, recorders, metrics_map, settings)
        rows = list_health_problem_rows(
            recorders,
            metrics_map,
            settings,
            problems_only=problems_only,
            search=search,
            category_filter=cat,
        )
        sections.append(
            CategoryDashboardSection(
                category=cat,
                title=label,
                element_id=f"category-dashboard-{cat}",
                default_expanded=stats.has_problems,
                stats=stats,
                problem_rows=rows,
                meta_text=category_meta_text(cat, settings),
            )
        )
    return sections


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
            classify_category(c, rec, metrics, settings)[0]
            for c in CATEGORY_LABELS
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
    highlight_category: Optional[HealthCategory] = None,
) -> dict:
    sections = build_category_sections(
        recorders,
        metrics_map,
        settings,
        ntp_server=ntp_server,
        compact=compact,
        problems_only=problems_only,
        search=search,
    )
    return {
        "category_sections": sections,
        "health_dashboard_compact": compact,
        "health_highlight_category": highlight_category,
    }
