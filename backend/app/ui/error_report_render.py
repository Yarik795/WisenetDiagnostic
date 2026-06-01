from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from ..display_time import format_for_display, to_display
from ..models import EmailReportSettings
from ..report_delivery_history import (
    DeliveryTrigger,
    ReportDeliveryHistory,
    ReportDeliveryRecord,
)
from ..web.templates_env import templates
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
    history_rows: list[dict[str, Any]]
    category_today: dict[str, int]
    category_yesterday: dict[str, int]
    show_category_compare: bool


def _trigger_label(trigger: DeliveryTrigger) -> str:
    return {
        "scheduled": "По расписанию (09:30)",
        "catchup": "Догон (пропуск >24 ч)",
        "manual": "Вручную",
    }.get(trigger, trigger)


def _format_delta(value: Optional[int]) -> dict[str, Any]:
    if value is None:
        return {"text": "—", "css": "delta-neutral"}
    if value > 0:
        return {"text": f"+{value} ↑", "css": "delta-up"}
    if value < 0:
        return {"text": f"{value} ↓", "css": "delta-down"}
    return {"text": "0", "css": "delta-neutral"}


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


def build_history_table_rows(
    history: ReportDeliveryHistory,
    *,
    limit: int,
) -> list[dict[str, Any]]:
    entries = history.entries[-limit:] if limit else history.entries
    rows: list[dict[str, Any]] = []
    for entry in reversed(entries):
        displayed = to_display(entry.sent_at)
        date_label = (
            format_for_display(entry.sent_at, "%d.%m.%Y %H:%M")
            if displayed
            else entry.sent_at.isoformat()
        )
        delta_p = delta_r = None
        if entry.status == "success":
            prev = _previous_successful(entry, history.entries)
            if prev is not None:
                delta_p = entry.problem_count - prev.problem_count
                delta_r = entry.recorders_with_errors - prev.recorders_with_errors
        trigger_short = {
            "scheduled": "план",
            "catchup": "догон",
            "manual": "ручн.",
        }.get(entry.trigger, entry.trigger)
        status_label = "OK" if entry.status == "success" else "ошибка"
        rows.append(
            {
                "date_label": date_label,
                "problem_count": entry.problem_count,
                "recorders_with_errors": entry.recorders_with_errors,
                "delta_problems": _format_delta(delta_p),
                "delta_recorders": _format_delta(delta_r),
                "status_label": status_label,
                "status_css": "status-ok" if entry.status == "success" else "status-fail",
                "trigger_short": trigger_short,
                "error": entry.error or "",
            }
        )
    return rows


def build_email_dashboard_context(
    *,
    report: ErrorReportContext,
    history: ReportDeliveryHistory,
    trigger: DeliveryTrigger,
    settings: EmailReportSettings,
    recorders_with_errors: int,
) -> dict[str, Any]:
    successful = history.successful_entries()
    category_today = report_metrics_category(report)
    category_yesterday = successful[-1].category_counts if successful else {}
    show_category_compare = bool(category_yesterday)

    ctx = EmailDashboardContext(
        report=report,
        trigger=trigger,
        trigger_label=_trigger_label(trigger),
        history_rows=build_history_table_rows(
            history, limit=settings.dashboard_history_days
        ),
        category_today=category_today,
        category_yesterday=category_yesterday,
        show_category_compare=show_category_compare,
    )
    return {
        "report": ctx.report,
        "trigger_label": ctx.trigger_label,
        "recorders_with_errors": recorders_with_errors,
        "history_rows": ctx.history_rows,
        "category_today": ctx.category_today,
        "category_yesterday": ctx.category_yesterday,
        "show_category_compare": ctx.show_category_compare,
        "all_categories": sorted(
            set(category_today) | set(category_yesterday)
        ),
    }


def report_metrics_category(report: ErrorReportContext) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in report.rows:
        counts[row.category_label] = counts.get(row.category_label, 0) + 1
    return counts
