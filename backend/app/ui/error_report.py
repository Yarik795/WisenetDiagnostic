from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal, Optional

from ..device_kinds import ALL_DEVICE_KINDS, DeviceKind, kind_label, recorder_device_kind
from ..display_time import format_for_display
from ..models import Credentials, MonitoringSettings, Recorder
from ..state_store import RecorderMetricsRow
from .grouping import STATUS_LABELS
from .health_dashboard import (
    CategoryDashboardSection,
    HealthProblemRow,
    health_dashboard_context,
)
from .health_classifiers import CATEGORY_LABELS
from .helpers import device_web_interface_url, device_web_link_title, display_recorder_name
from .metrics_helpers import format_skew, sync_type_label
from .time_dashboard import TimeProblemRow

DeviceAuthMode = Literal["", "userinfo"]

PING_CATEGORY_LABEL = "Доступность (ping)"
PING_DEVICE_KINDS: frozenset[DeviceKind] = frozenset({"skud", "bio"})
NVR_DEVICE_KINDS: frozenset[DeviceKind] = frozenset({"tsv", "sots"})

_STATUS_SORT_ORDER: dict[str, int] = {
    "error": 0,
    "offline": 0,
    "warn": 1,
    "unknown": 2,
    "ok": 3,
}


@dataclass
class ErrorReportRow:
    object_name: str
    recorder: Recorder
    recorder_display_name: str
    web_url: str
    web_link_title: str
    system_kind: str
    system_label: str
    category_label: str
    status: str
    status_label: str
    value_display: str
    reason: str
    polled_at_display: str
    problem_age_days_display: str = "—"
    problem_since_display: str = "—"
    problem_age_title: str = ""


@dataclass
class ReportSystemSection:
    system_kind: str
    system_label: str
    rows: list[ErrorReportRow]
    error_count: int
    warn_count: int
    is_ping_system: bool = False


@dataclass
class ErrorReportContext:
    generated_at: str
    problem_count: int
    rows: list[ErrorReportRow]
    sections: list[ReportSystemSection] = field(default_factory=list)
    error_count: int = 0
    warn_count: int = 0
    system_counts: dict[str, int] = field(default_factory=dict)


def _status_label(status: str) -> str:
    return STATUS_LABELS.get(status, status)


def _time_value_display(metrics: Optional[RecorderMetricsRow]) -> str:
    if metrics is None:
        return "—"
    parts: list[str] = []
    if metrics.local_time:
        parts.append(f"локальное {metrics.local_time}")
    parts.append(f"Δt {format_skew(metrics.time_skew_seconds)}")
    if metrics.sync_type:
        parts.append(sync_type_label(metrics.sync_type))
    if metrics.ntp_status:
        parts.append(f"NTP {metrics.ntp_status}")
    return " · ".join(parts) if parts else "—"


def _time_polled_at(metrics: Optional[RecorderMetricsRow]) -> str:
    if metrics and metrics.last_polled_at:
        return format_for_display(metrics.last_polled_at, "%Y-%m-%d %H:%M")
    return "—"


def format_problem_age_display(since: datetime, ref: datetime) -> str:
    """Длительность эпизода: сутки и часы, без занижения коротких интервалов до «0 сут.»."""
    if since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    if ref.tzinfo is None:
        ref = ref.replace(tzinfo=timezone.utc)
    total_seconds = max(0.0, (ref - since).total_seconds())
    days = int(total_seconds // 86400)
    hours = int((total_seconds % 86400) // 3600)
    if days >= 1:
        if hours > 0:
            return f"{days} сут. {hours} ч."
        return f"{days} сут."
    if hours >= 1:
        return f"{hours} ч."
    return "менее 1 ч."


def _problem_age_fields(
    recorder_id: str,
    category: str,
    problem_since_map: dict[tuple[str, str], datetime],
    *,
    now: Optional[datetime] = None,
) -> tuple[str, str, str]:
    since = problem_since_map.get((recorder_id, category))
    if since is None:
        return "—", "—", ""
    ref = now or datetime.now(timezone.utc)
    since_display = format_for_display(since, "%d.%m.%Y %H:%M")
    age_display = format_problem_age_display(since, ref)
    return age_display, since_display, f"С {since_display} ({age_display})"


def _recorder_problem_age_fields(
    recorder_id: str,
    recorder_problem_since_map: dict[str, datetime],
    *,
    now: Optional[datetime] = None,
) -> tuple[str, str, str]:
    since = recorder_problem_since_map.get(recorder_id)
    if since is None:
        return "—", "—", ""
    ref = now or datetime.now(timezone.utc)
    since_display = format_for_display(since, "%d.%m.%Y %H:%M")
    age_display = format_problem_age_display(since, ref)
    return age_display, since_display, f"С {since_display} ({age_display})"


def _sort_report_rows(rows: list[ErrorReportRow]) -> list[ErrorReportRow]:
    return sorted(
        rows,
        key=lambda row: (
            _STATUS_SORT_ORDER.get(row.status, 9),
            row.object_name.lower(),
            row.recorder_display_name.lower(),
            row.category_label.lower(),
        ),
    )


def _build_system_sections(rows: list[ErrorReportRow]) -> list[ReportSystemSection]:
    by_kind: dict[str, list[ErrorReportRow]] = {kind: [] for kind in ALL_DEVICE_KINDS}
    for row in rows:
        by_kind.setdefault(row.system_kind, []).append(row)

    sections: list[ReportSystemSection] = []
    for kind in ALL_DEVICE_KINDS:
        kind_rows = by_kind.get(kind, [])
        if not kind_rows:
            continue
        sections.append(
            ReportSystemSection(
                system_kind=kind,
                system_label=kind_label(kind),
                rows=kind_rows,
                error_count=sum(
                    1 for row in kind_rows if row.status in ("error", "offline")
                ),
                warn_count=sum(1 for row in kind_rows if row.status == "warn"),
                is_ping_system=kind in PING_DEVICE_KINDS,
            )
        )
    return sections


def _system_counts(rows: list[ErrorReportRow]) -> dict[str, int]:
    counts = {kind: 0 for kind in ALL_DEVICE_KINDS}
    for row in rows:
        counts[row.system_kind] = counts.get(row.system_kind, 0) + 1
    return counts


def _enrich_row(
    rec: Recorder,
    *,
    credentials: Credentials | None,
    device_auth: DeviceAuthMode,
    category_label: str,
    status: str,
    value_display: str,
    reason: str,
    polled_at_display: str,
    category_key: str,
    problem_since_map: dict[tuple[str, str], datetime],
    report_at: Optional[datetime] = None,
) -> ErrorReportRow:
    days_display, since_display, age_title = _problem_age_fields(
        rec.id, category_key, problem_since_map, now=report_at
    )
    kind = recorder_device_kind(rec)
    return ErrorReportRow(
        object_name=rec.object_name,
        recorder=rec,
        recorder_display_name=display_recorder_name(rec),
        web_url=device_web_interface_url(
            rec, credentials=credentials, device_auth=device_auth
        ),
        web_link_title=device_web_link_title(rec),
        system_kind=kind,
        system_label=kind_label(kind),
        category_label=category_label,
        status=status,
        status_label=_status_label(status),
        value_display=value_display,
        reason=reason,
        polled_at_display=polled_at_display,
        problem_age_days_display=days_display,
        problem_since_display=since_display,
        problem_age_title=age_title,
    )


def _row_from_health(
    problem: HealthProblemRow,
    *,
    credentials: Credentials | None,
    device_auth: DeviceAuthMode,
    problem_since_map: dict[tuple[str, str], datetime],
    report_at: Optional[datetime] = None,
) -> ErrorReportRow:
    rec = problem.recorder
    return _enrich_row(
        rec,
        credentials=credentials,
        device_auth=device_auth,
        category_label=problem.category_label,
        status=problem.status,
        value_display=problem.value_display,
        reason=problem.reason,
        polled_at_display=problem.polled_at_display,
        category_key=problem.category,
        problem_since_map=problem_since_map,
        report_at=report_at,
    )


def _row_from_time(
    problem: TimeProblemRow,
    *,
    credentials: Credentials | None,
    device_auth: DeviceAuthMode,
    problem_since_map: dict[tuple[str, str], datetime],
    report_at: Optional[datetime] = None,
) -> ErrorReportRow:
    rec = problem.recorder
    metrics = problem.metrics
    reason = "—"
    if metrics and metrics.health_reason:
        reason = metrics.health_reason
    return _enrich_row(
        rec,
        credentials=credentials,
        device_auth=device_auth,
        category_label=CATEGORY_LABELS["time"],
        status=problem.category,
        value_display=_time_value_display(metrics),
        reason=reason,
        polled_at_display=_time_polled_at(metrics),
        category_key="time",
        problem_since_map=problem_since_map,
        report_at=report_at,
    )


def flatten_error_report_rows(
    category_sections: list[CategoryDashboardSection],
    *,
    credentials: Credentials | None = None,
    device_auth: DeviceAuthMode = "",
    problem_since_map: dict[tuple[str, str], datetime] | None = None,
    report_at: Optional[datetime] = None,
) -> list[ErrorReportRow]:
    since_map = problem_since_map or {}
    rows: list[ErrorReportRow] = []
    for section in category_sections:
        if section.is_time and section.time_context:
            for problem in section.time_context.time_problem_rows:
                rows.append(
                    _row_from_time(
                        problem,
                        credentials=credentials,
                        device_auth=device_auth,
                        problem_since_map=since_map,
                        report_at=report_at,
                    )
                )
            continue
        for problem in section.problem_rows:
            rows.append(
                _row_from_health(
                    problem,
                    credentials=credentials,
                    device_auth=device_auth,
                    problem_since_map=since_map,
                    report_at=report_at,
                )
            )
    return rows


def build_ping_problem_rows(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    *,
    credentials: Credentials | None = None,
    device_auth: DeviceAuthMode = "",
    recorder_problem_since_map: dict[str, datetime] | None = None,
    excluded_ids: set[str] | None = None,
    report_at: Optional[datetime] = None,
) -> list[ErrorReportRow]:
    excluded = excluded_ids or set()
    since_map = recorder_problem_since_map or {}
    rows: list[ErrorReportRow] = []
    for rec in recorders:
        if rec.id in excluded:
            continue
        kind = recorder_device_kind(rec)
        if kind not in PING_DEVICE_KINDS:
            continue
        metrics = metrics_map.get(rec.id)
        if metrics is None or metrics.last_polled_at is None:
            continue
        if metrics.health_status != "error":
            continue
        reason = metrics.health_reason or "нет ответа ping"
        polled_at_display = format_for_display(metrics.last_polled_at, "%Y-%m-%d %H:%M")
        days_display, since_display, age_title = _recorder_problem_age_fields(
            rec.id, since_map, now=report_at
        )
        rows.append(
            ErrorReportRow(
                object_name=rec.object_name,
                recorder=rec,
                recorder_display_name=display_recorder_name(rec),
                web_url=device_web_interface_url(
                    rec, credentials=credentials, device_auth=device_auth
                ),
                web_link_title=device_web_link_title(rec),
                system_kind=kind,
                system_label=kind_label(kind),
                category_label=PING_CATEGORY_LABEL,
                status="error",
                status_label=_status_label("error"),
                value_display=rec.host,
                reason=reason,
                polled_at_display=polled_at_display,
                problem_age_days_display=days_display,
                problem_since_display=since_display,
                problem_age_title=age_title,
            )
        )
    return rows


def build_error_report_context(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
    *,
    credentials: Credentials | None = None,
    ntp_server: str = "",
    device_auth: DeviceAuthMode = "",
    problem_since_map: dict[tuple[str, str], datetime] | None = None,
    recorder_problem_since_map: dict[str, datetime] | None = None,
    report_at: Optional[datetime] = None,
    excluded_ids: set[str] | None = None,
) -> ErrorReportContext:
    ref = report_at or datetime.now(timezone.utc)
    nvr_recorders = [
        rec for rec in recorders if recorder_device_kind(rec) in NVR_DEVICE_KINDS
    ]
    ping_recorders = [
        rec for rec in recorders if recorder_device_kind(rec) in PING_DEVICE_KINDS
    ]

    dashboard = health_dashboard_context(
        nvr_recorders,
        metrics_map,
        settings,
        ntp_server=ntp_server,
        problems_only=True,
        excluded_ids=excluded_ids,
    )
    nvr_rows = flatten_error_report_rows(
        dashboard["category_sections"],
        credentials=credentials,
        device_auth=device_auth,
        problem_since_map=problem_since_map,
        report_at=ref,
    )
    ping_rows = build_ping_problem_rows(
        ping_recorders,
        metrics_map,
        credentials=credentials,
        device_auth=device_auth,
        recorder_problem_since_map=recorder_problem_since_map,
        excluded_ids=excluded_ids,
        report_at=ref,
    )
    rows = _sort_report_rows(nvr_rows + ping_rows)
    if ref.tzinfo is None:
        ref = ref.replace(tzinfo=timezone.utc)
    error_count = sum(1 for row in rows if row.status in ("error", "offline"))
    warn_count = sum(1 for row in rows if row.status == "warn")
    return ErrorReportContext(
        generated_at=format_for_display(ref, "%d.%m.%Y %H:%M:%S"),
        problem_count=len(rows),
        rows=rows,
        sections=_build_system_sections(rows),
        error_count=error_count,
        warn_count=warn_count,
        system_counts=_system_counts(rows),
    )
