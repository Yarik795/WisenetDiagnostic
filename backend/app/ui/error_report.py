from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Optional

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


@dataclass
class ErrorReportRow:
    object_name: str
    recorder: Recorder
    recorder_display_name: str
    web_url: str
    web_link_title: str
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
class ErrorReportContext:
    generated_at: str
    problem_count: int
    rows: list[ErrorReportRow]


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
        return metrics.last_polled_at.strftime("%Y-%m-%d %H:%M")
    return "—"


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
    if since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    ref = now or datetime.now(timezone.utc)
    if ref.tzinfo is None:
        ref = ref.replace(tzinfo=timezone.utc)
    days = max(0, (ref - since).days)
    since_display = since.strftime("%d.%m.%Y %H:%M")
    return f"{days} сут.", since_display, f"С {since_display}"


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
    return ErrorReportRow(
        object_name=rec.object_name,
        recorder=rec,
        recorder_display_name=display_recorder_name(rec),
        web_url=device_web_interface_url(
            rec, credentials=credentials, device_auth=device_auth
        ),
        web_link_title=device_web_link_title(rec),
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


def build_error_report_context(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    settings: MonitoringSettings,
    *,
    credentials: Credentials | None = None,
    ntp_server: str = "",
    device_auth: DeviceAuthMode = "",
    problem_since_map: dict[tuple[str, str], datetime] | None = None,
    report_at: Optional[datetime] = None,
) -> ErrorReportContext:
    ref = report_at or datetime.now()
    dashboard = health_dashboard_context(
        recorders,
        metrics_map,
        settings,
        ntp_server=ntp_server,
        problems_only=True,
    )
    rows = flatten_error_report_rows(
        dashboard["category_sections"],
        credentials=credentials,
        device_auth=device_auth,
        problem_since_map=problem_since_map,
        report_at=ref,
    )
    if ref.tzinfo is None:
        ref = ref.replace(tzinfo=timezone.utc)
    return ErrorReportContext(
        generated_at=ref.strftime("%d.%m.%Y %H:%M:%S"),
        problem_count=len(rows),
        rows=rows,
    )
