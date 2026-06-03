from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from ..display_time import format_for_display, get_display_tz, to_display
from ..models import EmailReportSettings
from ..report_delivery_history import (
    DeliveryTrigger,
    ReportDeliveryHistory,
    ReportDeliveryRecord,
)
from ..web.templates_env import templates
from .email_charts import render_trend_sparkline_svg
from .email_history_series import (
    aggregate_successful_by_local_day,
    build_category_changes,
    count_days_with_data,
    format_delta_display,
    kpi_delta_vs_previous_day,
)
from .error_report import ErrorReportContext


def render_error_report_html(report: ErrorReportContext) -> str:
    template = templates.env.get_template("exports/error_report.html")
    return template.render(report=report)


def render_email_dashboard_html(context: dict[str, Any]) -> str:
    template = templates.env.get_template("email/report_dashboard.html")
    return template.render(**context)


@dataclass
class EmailDashboardContext:
    report: ErrorReportContext
    trigger: DeliveryTrigger
    trigger_label: str
    category_today: dict[str, int]
    category_yesterday: dict[str, int]
    show_category_compare: bool


def _trigger_label(trigger: DeliveryTrigger, send_time: str) -> str:
    labels = {
        "scheduled": f"По расписанию ({send_time})",
        "catchup": "Догон (пропуск >24 ч)",
        "manual": "Вручную",
    }
    return labels.get(trigger, trigger)


def _format_delta(value: Optional[int]) -> dict[str, Any]:
    return format_delta_display(value)


def _previous_successful(
    entry: ReportDeliveryRecord, all_entries: list[ReportDeliveryRecord]
) -> Optional[ReportDeliveryRecord]:
    try:
        idx = all_entries.index(entry)
    except ValueError:
        return None
    for i in range(idx - 1, -1, -1):
        if all_entries[i].status == "success":
            return all_entries[i]
    return None


def build_email_dashboard_context(
    *,
    report: ErrorReportContext,
    history: ReportDeliveryHistory,
    trigger: DeliveryTrigger,
    settings: EmailReportSettings,
    recorders_with_errors: int,
) -> dict[str, Any]:
    tz = get_display_tz()
    trend_days_n = settings.email_trend_days
    trend_points = aggregate_successful_by_local_day(
        history, tz=tz, days=trend_days_n
    )
    trend_available = count_days_with_data(trend_points)
    delta_p, delta_r = kpi_delta_vs_previous_day(trend_points)

    successful = history.successful_entries()
    category_today = report_metrics_category(report)
    category_yesterday = successful[-1].category_counts if successful else {}
    show_category_compare = bool(successful)
    category_changes = (
        build_category_changes(category_today, category_yesterday)
        if successful
        else []
    )

    ctx = EmailDashboardContext(
        report=report,
        trigger=trigger,
        trigger_label=_trigger_label(trigger, settings.send_time),
        category_today=category_today,
        category_yesterday=category_yesterday,
        show_category_compare=show_category_compare,
    )

    trend_rows = [
        {
            "date_label": p.date_label,
            "problem_count": p.problem_count if p.has_data else "—",
            "recorders_with_errors": p.recorders_with_errors if p.has_data else "—",
            "has_data": p.has_data,
        }
        for p in trend_points
    ]

    return {
        "report": ctx.report,
        "trigger_label": ctx.trigger_label,
        "recorders_with_errors": recorders_with_errors,
        "category_today": ctx.category_today,
        "category_yesterday": ctx.category_yesterday,
        "show_category_compare": ctx.show_category_compare,
        "category_changes": category_changes,
        "trend_points": trend_points,
        "trend_rows": trend_rows,
        "trend_svg": render_trend_sparkline_svg(trend_points),
        "trend_days_total": trend_days_n,
        "trend_days_available": trend_available,
        "kpi_delta_problems": _format_delta(delta_p),
        "kpi_delta_nvr": _format_delta(delta_r),
    }


def report_metrics_category(report: ErrorReportContext) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in report.rows:
        counts[row.category_label] = counts.get(row.category_label, 0) + 1
    return counts


def build_email_subject(
    settings: EmailReportSettings,
    *,
    problem_count: int,
    recorders_with_errors: int,
    delta_problems: Optional[int],
    sent_at: datetime,
) -> str:
    date_part = format_for_display(sent_at, "%d.%m") or ""
    delta_part = ""
    if delta_problems is not None and delta_problems != 0:
        sign = "+" if delta_problems > 0 else ""
        delta_part = f" ({sign}{delta_problems})"
    elif delta_problems == 0:
        delta_part = " (без изм.)"
    return (
        f"{settings.subject}: {problem_count} проблем{delta_part}, "
        f"{recorders_with_errors} NVR — {date_part}"
    )
