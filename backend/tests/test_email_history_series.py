from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from app.report_delivery_history import ReportDeliveryHistory, ReportDeliveryRecord
from app.ui.email_charts import render_trend_sparkline_svg
from app.ui.email_history_series import (
    aggregate_successful_by_local_day,
    build_category_changes,
    count_days_with_data,
    kpi_delta_vs_previous_day,
)
from app.ui.error_report_render import build_email_dashboard_context, render_email_dashboard_html
from app.models import EmailReportSettings
from app.ui.error_report import ErrorReportContext

MSK = ZoneInfo("Europe/Moscow")


def _success_at(when: datetime, **kwargs) -> ReportDeliveryRecord:
    defaults = dict(
        problem_count=10,
        recorders_with_errors=5,
        category_counts={},
        status="success",
        trigger="scheduled",
    )
    defaults.update(kwargs)
    return ReportDeliveryRecord(sent_at=when, **defaults)


def test_aggregate_seven_slots_with_gaps() -> None:
    end = date(2026, 6, 7)
    entries = [
        _success_at(
            datetime(2026, 6, 1, 6, 30, tzinfo=timezone.utc),
            problem_count=5,
            recorders_with_errors=2,
        ),
        _success_at(
            datetime(2026, 6, 7, 6, 30, tzinfo=timezone.utc),
            problem_count=8,
            recorders_with_errors=4,
        ),
    ]
    history = ReportDeliveryHistory(entries=entries)
    points = aggregate_successful_by_local_day(
        history, tz=MSK, days=7, end_date=end
    )
    assert len(points) == 7
    assert points[0].day == date(2026, 6, 1)
    assert points[0].has_data is True
    assert points[0].problem_count == 5
    assert points[1].has_data is False
    assert points[-1].problem_count == 8
    assert count_days_with_data(points) == 2


def test_aggregate_last_send_per_day() -> None:
    d = date(2026, 6, 3)
    morning = datetime(2026, 6, 3, 3, 0, tzinfo=timezone.utc)
    evening = datetime(2026, 6, 3, 18, 0, tzinfo=timezone.utc)
    history = ReportDeliveryHistory(
        entries=[
            _success_at(morning, problem_count=1, recorders_with_errors=1),
            _success_at(evening, problem_count=9, recorders_with_errors=9),
        ]
    )
    points = aggregate_successful_by_local_day(
        history, tz=MSK, days=1, end_date=d
    )
    assert len(points) == 1
    assert points[0].problem_count == 9


def test_kpi_delta_vs_previous_day() -> None:
    end = date(2026, 6, 3)
    history = ReportDeliveryHistory(
        entries=[
            _success_at(
                datetime(2026, 6, 2, 6, 30, tzinfo=timezone.utc),
                problem_count=5,
                recorders_with_errors=2,
            ),
            _success_at(
                datetime(2026, 6, 3, 6, 30, tzinfo=timezone.utc),
                problem_count=8,
                recorders_with_errors=4,
            ),
        ]
    )
    points = aggregate_successful_by_local_day(
        history, tz=MSK, days=3, end_date=end
    )
    delta_p, delta_r = kpi_delta_vs_previous_day(points)
    assert delta_p == 3
    assert delta_r == 2


def test_build_category_changes_only_nonzero() -> None:
    changes = build_category_changes(
        {"Каналы": 10, "HDD": 3},
        {"Каналы": 10, "HDD": 1},
    )
    assert len(changes) == 1
    assert changes[0].name == "HDD"
    assert changes[0].delta == 2


def test_sparkline_svg_nonempty() -> None:
    end = date(2026, 6, 2)
    history = ReportDeliveryHistory(
        entries=[
            _success_at(
                datetime(2026, 6, 1, 6, 30, tzinfo=timezone.utc),
                problem_count=5,
            ),
            _success_at(
                datetime(2026, 6, 2, 6, 30, tzinfo=timezone.utc),
                problem_count=8,
            ),
        ]
    )
    points = aggregate_successful_by_local_day(
        history, tz=MSK, days=2, end_date=end
    )
    svg = render_trend_sparkline_svg(points)
    assert "<svg" in svg
    assert "polyline" in svg


def test_render_email_dashboard_html() -> None:
    report = ErrorReportContext(
        generated_at="03.06.2026 09:00",
        problem_count=31,
        rows=[],
    )
    history = ReportDeliveryHistory(
        entries=[
            _success_at(
                datetime(2026, 6, 1, 6, 30, tzinfo=timezone.utc),
                problem_count=30,
                category_counts={"Каналы": 10},
            ),
        ]
    )
    ctx = build_email_dashboard_context(
        report=report,
        history=history,
        trigger="scheduled",
        settings=EmailReportSettings(send_time="09:30", email_trend_days=7),
        recorders_with_errors=29,
    )
    html = render_email_dashboard_html(ctx)
    assert "31" in html
    assert "Динамика за 7 дней" in html
    assert "<svg" in html
