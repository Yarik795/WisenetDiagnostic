from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, Optional

from ..models import MonitoringSettings, Recorder
from ..state_store import RecorderMetricsRow
from .grouping import aggregate_status, effective_status
from .health_classifiers import (
    BADGE_CODES,
    CATEGORY_LABELS,
    HealthCategory,
    HealthCategoryStatus,
    classify_category,
    is_problem_status,
    worst_category_status,
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


_STATUS_ORDER = {"error": 4, "offline": 4, "warn": 3, "unknown": 2, "ok": 1, "online": 1, "disabled": 0}


@dataclass
class FleetStatusCounts:
    ok: int = 0
    warn: int = 0
    error: int = 0
    unknown: int = 0
    disabled: int = 0

    @property
    def stacked_segments(self) -> list[tuple[str, int, str]]:
        return [
            ("ok", self.ok, "time-stack-ok"),
            ("warn", self.warn, "time-stack-warn"),
            ("error", self.error, "time-stack-error"),
            ("unknown", self.unknown, "time-stack-unknown"),
            ("disabled", self.disabled, "fleet-stack-disabled"),
        ]

    @property
    def stacked_total(self) -> int:
        return self.ok + self.warn + self.error + self.unknown + self.disabled


@dataclass
class CategoryProblemBar:
    category: HealthCategory
    label: str
    code: str
    problem_count: int
    error_count: int
    warn_count: int


@dataclass
class TopProblemObject:
    object_name: str
    nvr_count: int
    problem_nvr_count: int
    worst_status: str


@dataclass
class ObjectMatrixCell:
    column: str
    status: str
    problem_count: int
    title: str


@dataclass
class ObjectMatrixRow:
    object_name: str
    nvr_count: int
    problem_nvr_count: int
    aggregate_status: str
    cells: list[ObjectMatrixCell]


_MATRIX_COLUMNS: list[tuple[str, Optional[HealthCategory]]] = [
    ("nvr", None),
    ("time", "time"),
    ("storage", "storage"),
    ("temperature", "temperature"),
    ("fans", "fans"),
    ("channels", "channels"),
    ("archive", "archive"),
]

_MATRIX_HEADERS: dict[str, str] = {
    "nvr": "NVR",
    "time": "NTP",
    "storage": "HDD",
    "temperature": "TEMP",
    "fans": "FAN",
    "channels": "CH",
    "archive": "ARCH",
}


def _status_rank(status: str) -> int:
    return _STATUS_ORDER.get(status, 0)


def _recorder_has_poll_data(
    recorder: Recorder,
    metrics: Optional[RecorderMetricsRow],
) -> bool:
    if not recorder.enabled:
        return False
    if metrics is None or metrics.last_polled_at is None:
        return False
    return metrics.device_online


def aggregate_fleet_status_counts(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
) -> FleetStatusCounts:
    counts = FleetStatusCounts()
    for rec in recorders:
        if not rec.enabled:
            counts.disabled += 1
            continue
        status = effective_status(rec, metrics_map.get(rec.id))
        if status in ("ok", "online"):
            counts.ok += 1
        elif status == "warn":
            counts.warn += 1
        elif status in ("error", "offline"):
            counts.error += 1
        else:
            counts.unknown += 1
    return counts


def count_nvr_without_poll_data(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
) -> int:
    n = 0
    for rec in recorders:
        if not rec.enabled:
            continue
        if not _recorder_has_poll_data(rec, metrics_map.get(rec.id)):
            n += 1
    return n


def recorder_has_health_problems(
    recorder: Recorder,
    metrics: Optional[RecorderMetricsRow],
    settings: MonitoringSettings,
) -> bool:
    if not recorder.enabled:
        return False
    statuses = [
        classify_category(c, recorder, metrics, settings)[0]
        for c in CATEGORY_LABELS
    ]
    eff = effective_status(recorder, metrics)
    return eff in ("warn", "error", "offline") or any(
        is_problem_status(s) for s in statuses
    )


def fleet_health_percent(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
) -> int:
    enabled = [r for r in recorders if r.enabled]
    if not enabled:
        return 100
    healthy = sum(
        1
        for r in enabled
        if not recorder_has_health_problems(r, metrics_map.get(r.id), settings)
    )
    return round(100 * healthy / len(enabled))


def build_category_problem_bars(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
) -> list[CategoryProblemBar]:
    bars: list[CategoryProblemBar] = []
    for cat, label in CATEGORY_LABELS.items():
        stats = aggregate_category_stats(cat, recorders, metrics_map, settings)
        bars.append(
            CategoryProblemBar(
                category=cat,
                label=label,
                code=BADGE_CODES[cat],
                problem_count=stats.warn + stats.error,
                error_count=stats.error,
                warn_count=stats.warn,
            )
        )
    bars.sort(key=lambda b: (-b.problem_count, b.label))
    return bars


def build_top_problem_objects(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
    *,
    limit: int = 8,
) -> list[TopProblemObject]:
    by_object: dict[str, list[Recorder]] = {}
    for rec in recorders:
        by_object.setdefault(rec.object_name, []).append(rec)

    rows: list[TopProblemObject] = []
    for name, recs in by_object.items():
        problem_nvr = sum(
            1
            for r in recs
            if r.enabled
            and recorder_has_health_problems(r, metrics_map.get(r.id), settings)
        )
        if problem_nvr == 0:
            continue
        agg = aggregate_status(recs, metrics_map)
        rows.append(
            TopProblemObject(
                object_name=name,
                nvr_count=len(recs),
                problem_nvr_count=problem_nvr,
                worst_status=agg,
            )
        )
    rows.sort(
        key=lambda row: (
            -_status_rank(row.worst_status),
            -row.problem_nvr_count,
            row.object_name.lower(),
        )
    )
    return rows[:limit]


def _cell_for_column(
    column: str,
    category: Optional[HealthCategory],
    recs: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
) -> ObjectMatrixCell:
    enabled = [r for r in recs if r.enabled]
    if not enabled:
        return ObjectMatrixCell(
            column=column,
            status="disabled",
            problem_count=0,
            title="Все NVR выключены",
        )

    if category is None:
        statuses = [
            effective_status(r, metrics_map.get(r.id)) for r in enabled
        ]
        worst = max(statuses, key=_status_rank) if statuses else "unknown"
        problems = sum(
            1
            for r in enabled
            if effective_status(r, metrics_map.get(r.id))
            in ("warn", "error", "offline", "unknown")
        )
        return ObjectMatrixCell(
            column=column,
            status=worst,
            problem_count=problems,
            title=f"{problems} из {len(enabled)} NVR с отклонением",
        )

    statuses: list[HealthCategoryStatus] = []
    problems = 0
    for rec in enabled:
        st, reason = classify_category(
            category, rec, metrics_map.get(rec.id), settings
        )
        statuses.append(st)
        if is_problem_status(st):
            problems += 1
    worst = worst_category_status(*statuses) if statuses else "unknown"
    label = CATEGORY_LABELS[category]
    if problems:
        title = f"{label}: {problems} из {len(enabled)} NVR"
    elif worst == "unknown":
        title = f"{label}: нет суммарных данных API"
    else:
        title = f"{label}: в норме"
    return ObjectMatrixCell(
        column=column,
        status=worst,
        problem_count=problems,
        title=title,
    )


def build_object_health_matrix(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
) -> list[ObjectMatrixRow]:
    by_object: dict[str, list[Recorder]] = {}
    for rec in recorders:
        by_object.setdefault(rec.object_name, []).append(rec)

    rows: list[ObjectMatrixRow] = []
    for name, recs in by_object.items():
        enabled = [r for r in recs if r.enabled]
        problem_nvr = sum(
            1
            for r in enabled
            if recorder_has_health_problems(r, metrics_map.get(r.id), settings)
        )
        cells = [
            _cell_for_column(col, cat, recs, metrics_map, settings)
            for col, cat in _MATRIX_COLUMNS
        ]
        rows.append(
            ObjectMatrixRow(
                object_name=name,
                nvr_count=len(recs),
                problem_nvr_count=problem_nvr,
                aggregate_status=aggregate_status(recs, metrics_map),
                cells=cells,
            )
        )

    rows.sort(
        key=lambda row: (
            -_status_rank(row.aggregate_status),
            -row.problem_nvr_count,
            row.object_name.lower(),
        )
    )
    return rows


def _fleet_last_polled_display(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
) -> str:
    latest: Optional[Any] = None
    for rec in recorders:
        if not rec.enabled:
            continue
        metrics = metrics_map.get(rec.id)
        if metrics and metrics.last_polled_at:
            if latest is None or metrics.last_polled_at > latest:
                latest = metrics.last_polled_at
    if latest is None:
        return "—"
    return latest.strftime("%Y-%m-%d %H:%M")


def fleet_overview_context(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
) -> dict:
    object_names = {r.object_name for r in recorders}
    enabled_recs = [r for r in recorders if r.enabled]
    status_counts = aggregate_fleet_status_counts(recorders, metrics_map)
    category_counts = object_category_problem_counts(
        recorders, metrics_map, settings
    )
    critical_nvr = 0
    warn_nvr = 0
    for rec in enabled_recs:
        metrics = metrics_map.get(rec.id)
        eff = effective_status(rec, metrics)
        cat_statuses = [
            classify_category(c, rec, metrics, settings)[0]
            for c in CATEGORY_LABELS
        ]
        is_critical = eff in ("error", "offline") or any(s == "error" for s in cat_statuses)
        is_warn = not is_critical and (
            eff == "warn" or any(s == "warn" for s in cat_statuses)
        )
        if is_critical:
            critical_nvr += 1
        elif is_warn:
            warn_nvr += 1

    return {
        "fleet_object_count": len(object_names),
        "fleet_nvr_count": len(recorders),
        "fleet_enabled_count": len(enabled_recs),
        "fleet_problem_nvr_count": object_health_problem_count(
            recorders, metrics_map, settings
        ),
        "fleet_no_data_count": count_nvr_without_poll_data(recorders, metrics_map),
        "fleet_status_counts": status_counts,
        "fleet_category_counts": category_counts,
        "fleet_health_percent": fleet_health_percent(
            recorders, metrics_map, settings
        ),
        "fleet_last_polled_display": _fleet_last_polled_display(
            recorders, metrics_map
        ),
        "fleet_critical_count": critical_nvr,
        "fleet_warn_count": warn_nvr,
        "fleet_unknown_count": status_counts.unknown,
        "health_category_options": list(CATEGORY_LABELS.items()),
        "object_matrix_rows": build_object_health_matrix(
            recorders, metrics_map, settings
        ),
        "object_matrix_headers": _MATRIX_HEADERS,
        "top_problem_objects": build_top_problem_objects(
            recorders, metrics_map, settings
        ),
        "category_problem_bars": build_category_problem_bars(
            recorders, metrics_map, settings
        ),
    }


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
    if highlight_category:
        for section in sections:
            if section.is_time and highlight_category == "time":
                section.default_expanded = True
            elif section.category == highlight_category:
                section.default_expanded = True
    return {
        "category_sections": sections,
        "health_dashboard_compact": compact,
        "health_highlight_category": highlight_category,
        **fleet_overview_context(recorders, metrics_map, settings),
    }
