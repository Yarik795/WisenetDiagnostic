from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from ..display_time import to_display
from ..report_delivery_history import ReportDeliveryHistory, ReportDeliveryRecord


@dataclass(frozen=True)
class DayPoint:
    day: date
    date_label: str
    problem_count: Optional[int]
    recorders_with_errors: Optional[int]
    has_data: bool


def _entry_local_date(entry: ReportDeliveryRecord, tz: ZoneInfo) -> date:
    displayed = to_display(entry.sent_at)
    if displayed is not None:
        return displayed.date()
    sent = entry.sent_at
    if sent.tzinfo is None:
        sent = sent.replace(tzinfo=timezone.utc)
    return sent.astimezone(tz).date()


def aggregate_successful_by_local_day(
    history: ReportDeliveryHistory,
    *,
    tz: ZoneInfo,
    days: int,
    end_date: Optional[date] = None,
) -> list[DayPoint]:
    """Last *days* calendar slots ending on *end_date* (default: today in *tz*)."""
    if days < 1:
        days = 1
    if end_date is None:
        end_date = datetime.now(timezone.utc).astimezone(tz).date()

    by_day: dict[date, ReportDeliveryRecord] = {}
    for entry in history.entries:
        if entry.status != "success":
            continue
        d = _entry_local_date(entry, tz)
        prev = by_day.get(d)
        if prev is None or entry.sent_at > prev.sent_at:
            by_day[d] = entry

    start = end_date - timedelta(days=days - 1)
    points: list[DayPoint] = []
    d = start
    while d <= end_date:
        entry = by_day.get(d)
        label = d.strftime("%d.%m")
        if entry is None:
            points.append(
                DayPoint(
                    day=d,
                    date_label=label,
                    problem_count=None,
                    recorders_with_errors=None,
                    has_data=False,
                )
            )
        else:
            points.append(
                DayPoint(
                    day=d,
                    date_label=label,
                    problem_count=entry.problem_count,
                    recorders_with_errors=entry.recorders_with_errors,
                    has_data=True,
                )
            )
        d += timedelta(days=1)
    return points


def count_days_with_data(points: list[DayPoint]) -> int:
    return sum(1 for p in points if p.has_data)


def kpi_delta_vs_previous_day(
    points: list[DayPoint],
) -> tuple[Optional[int], Optional[int]]:
    """Delta for last day with data vs previous day with data."""
    with_data = [p for p in points if p.has_data]
    if len(with_data) < 2:
        return None, None
    today_p, prev_p = with_data[-1], with_data[-2]
    assert today_p.problem_count is not None and prev_p.problem_count is not None
    assert today_p.recorders_with_errors is not None and prev_p.recorders_with_errors is not None
    return (
        today_p.problem_count - prev_p.problem_count,
        today_p.recorders_with_errors - prev_p.recorders_with_errors,
    )


@dataclass(frozen=True)
class CategoryChange:
    name: str
    today: int
    prev: int
    delta: int


def build_category_changes(
    category_today: dict[str, int],
    category_prev: dict[str, int],
) -> list[CategoryChange]:
    names = sorted(set(category_today) | set(category_prev))
    changes: list[CategoryChange] = []
    for name in names:
        today = category_today.get(name, 0)
        prev = category_prev.get(name, 0)
        delta = today - prev
        if delta != 0:
            changes.append(CategoryChange(name=name, today=today, prev=prev, delta=delta))
    changes.sort(key=lambda c: abs(c.delta), reverse=True)
    return changes


def format_delta_display(value: Optional[int]) -> dict[str, str]:
    if value is None:
        return {"text": "—", "css": "delta-neutral"}
    if value > 0:
        return {"text": f"+{value}", "css": "delta-up"}
    if value < 0:
        return {"text": str(value), "css": "delta-down"}
    return {"text": "0", "css": "delta-neutral"}
