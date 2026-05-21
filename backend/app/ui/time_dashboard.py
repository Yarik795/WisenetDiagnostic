from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from ..models import MonitoringSettings, Recorder
from ..state_store import RecorderMetricsRow
from ..ui.metrics_helpers import is_manual_sync, show_ntp_action_button
from ..ui.grouping import effective_status

TimeCategory = Literal["ok", "warn", "error", "unknown"]


@dataclass
class TimeDashboardStats:
    total_enabled: int = 0
    ok: int = 0
    warn: int = 0
    error: int = 0
    unknown: int = 0
    fixable: int = 0
    has_problems: bool = False

    @property
    def stacked_segments(self) -> list[tuple[str, int, str]]:
        """(label, count, css_class) for stacked bar."""
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
class TimeProblemRow:
    recorder: Recorder
    metrics: Optional[RecorderMetricsRow]
    category: TimeCategory
    effective: str


def classify_time_health(
    recorder: Recorder,
    metrics: Optional[RecorderMetricsRow],
    settings: MonitoringSettings,
) -> TimeCategory:
    if not recorder.enabled:
        return "unknown"

    if metrics is None or metrics.last_polled_at is None:
        return "unknown"

    if not metrics.device_online:
        return "unknown"

    skew = metrics.time_skew_seconds
    if skew is not None:
        if skew >= settings.time_skew_error_seconds:
            return "error"
        if skew >= settings.time_skew_warn_seconds:
            return "warn"

    ntp = (metrics.ntp_status or "").strip().lower()
    if ntp == "fail":
        return "warn"

    if is_manual_sync(metrics.sync_type):
        return "warn"

    sync = (metrics.sync_type or "").strip().lower()
    if sync and sync != "ntp":
        return "warn"

    return "ok"


def is_time_problem_category(category: TimeCategory) -> bool:
    return category in ("warn", "error")


def is_fixable_recorder(
    recorder: Recorder,
    metrics: Optional[RecorderMetricsRow],
) -> bool:
    if not recorder.enabled:
        return False
    if metrics is None or not metrics.device_online:
        return False
    return show_ntp_action_button(metrics)


def aggregate_time_stats(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
) -> TimeDashboardStats:
    stats = TimeDashboardStats()
    for rec in recorders:
        if not rec.enabled:
            continue
        stats.total_enabled += 1
        metrics = metrics_map.get(rec.id)
        cat = classify_time_health(rec, metrics, settings)
        if cat == "ok":
            stats.ok += 1
        elif cat == "warn":
            stats.warn += 1
            stats.has_problems = True
        elif cat == "error":
            stats.error += 1
            stats.has_problems = True
        else:
            stats.unknown += 1
        if is_fixable_recorder(rec, metrics):
            stats.fixable += 1
    return stats


def list_problem_rows(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
    *,
    problems_only: bool = True,
    search: str = "",
) -> list[TimeProblemRow]:
    q = search.strip().lower()
    rows: list[TimeProblemRow] = []
    for rec in recorders:
        if not rec.enabled:
            continue
        metrics = metrics_map.get(rec.id)
        cat = classify_time_health(rec, metrics, settings)
        if problems_only and not is_time_problem_category(cat):
            continue
        if q:
            hay = f"{rec.object_name} {rec.host} {rec.name or ''}".lower()
            if q not in hay:
                continue
        rows.append(
            TimeProblemRow(
                recorder=rec,
                metrics=metrics,
                category=cat,
                effective=effective_status(rec, metrics),
            )
        )
    rows.sort(
        key=lambda r: (
            0 if r.category == "error" else 1,
            -(r.metrics.time_skew_seconds or 0) if r.metrics else 0,
            r.recorder.object_name.lower(),
        )
    )
    return rows


def list_fixable_recorders(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
) -> list[Recorder]:
    return [
        r
        for r in recorders
        if is_fixable_recorder(r, metrics_map.get(r.id))
    ]


def object_time_problem_count(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
) -> int:
    return sum(
        1
        for r in recorders
        if r.enabled
        and is_time_problem_category(
            classify_time_health(r, metrics_map.get(r.id), settings)
        )
    )


def time_dashboard_context(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
    *,
    ntp_server: str,
    compact: bool = False,
    problems_only: bool = True,
    search: str = "",
    show_all_table: bool = False,
) -> dict:
    stats = aggregate_time_stats(recorders, metrics_map, settings)
    problem_rows = list_problem_rows(
        recorders,
        metrics_map,
        settings,
        problems_only=not show_all_table and problems_only,
        search=search,
    )
    if show_all_table and not problems_only:
        problem_rows = list_problem_rows(
            recorders,
            metrics_map,
            settings,
            problems_only=False,
            search=search,
        )
    return {
        "time_stats": stats,
        "time_problem_rows": problem_rows,
        "time_ntp_server": (ntp_server or "").strip() or "—",
        "time_skew_warn": settings.time_skew_warn_seconds,
        "time_skew_error": settings.time_skew_error_seconds,
        "time_dashboard_compact": compact,
        "time_default_expanded": stats.has_problems,
    }
