from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import pytest

from app.models import EmailReportSettings
from app.report_delivery import (
    SendDecision,
    should_send_report,
    report_metrics_from_context,
)
from app.report_delivery_history import (
    ReportDeliveryHistory,
    ReportDeliveryHistoryStore,
    ReportDeliveryRecord,
)
from app.ui.error_report import ErrorReportContext, ErrorReportRow


MSK = ZoneInfo("Europe/Moscow")


def _settings(**kwargs) -> EmailReportSettings:
    base = EmailReportSettings(enabled=True)
    return base.model_copy(update=kwargs)


def _success_at(when: datetime, **kwargs) -> ReportDeliveryRecord:
    defaults = dict(
        problem_count=10,
        recorders_with_errors=5,
        category_counts={"Время": 2},
        status="success",
        trigger="scheduled",
    )
    defaults.update(kwargs)
    return ReportDeliveryRecord(sent_at=when, **defaults)


def test_should_send_disabled() -> None:
    decision = should_send_report(
        datetime(2026, 6, 1, 6, 30, tzinfo=MSK),
        _settings(enabled=False),
        ReportDeliveryHistory(),
        display_tz=MSK,
    )
    assert decision.should_send is False


def test_should_send_catchup_when_no_history() -> None:
    decision = should_send_report(
        datetime(2026, 6, 1, 8, 0, tzinfo=MSK),
        _settings(),
        ReportDeliveryHistory(),
        display_tz=MSK,
    )
    assert decision.should_send is True
    assert decision.trigger == "catchup"


def test_should_send_scheduled_after_0930() -> None:
    yesterday = datetime(2026, 5, 31, 20, 0, tzinfo=timezone.utc)
    history = ReportDeliveryHistory(entries=[_success_at(yesterday)])
    decision = should_send_report(
        datetime(2026, 6, 1, 9, 31, tzinfo=MSK),
        _settings(),
        history,
        display_tz=MSK,
    )
    assert decision.should_send is True
    assert decision.trigger == "scheduled"


def test_should_not_send_before_0930_without_catchup() -> None:
    yesterday = datetime(2026, 5, 31, 6, 30, tzinfo=timezone.utc)
    history = ReportDeliveryHistory(entries=[_success_at(yesterday)])
    decision = should_send_report(
        datetime(2026, 6, 1, 6, 29, tzinfo=MSK),
        _settings(),
        history,
        display_tz=MSK,
    )
    assert decision.should_send is False


def test_should_not_send_twice_same_day() -> None:
    today_morning = datetime(2026, 6, 1, 6, 35, tzinfo=timezone.utc)
    history = ReportDeliveryHistory(entries=[_success_at(today_morning)])
    decision = should_send_report(
        datetime(2026, 6, 1, 12, 0, tzinfo=MSK),
        _settings(),
        history,
        display_tz=MSK,
    )
    assert decision.should_send is False


def test_manual_success_does_not_block_scheduled_same_day() -> None:
    today_morning = datetime(2026, 6, 1, 6, 35, tzinfo=timezone.utc)
    history = ReportDeliveryHistory(
        entries=[_success_at(today_morning, trigger="manual")]
    )
    decision = should_send_report(
        datetime(2026, 6, 1, 12, 0, tzinfo=MSK),
        _settings(),
        history,
        display_tz=MSK,
    )
    assert decision.should_send is True
    assert decision.trigger == "scheduled"


def test_catchup_after_24h() -> None:
    old = datetime(2026, 5, 29, 6, 30, tzinfo=timezone.utc)
    history = ReportDeliveryHistory(entries=[_success_at(old)])
    decision = should_send_report(
        datetime(2026, 6, 1, 6, 0, tzinfo=MSK),
        _settings(catchup_after_hours=24),
        history,
        display_tz=MSK,
    )
    assert decision.should_send is True
    assert decision.trigger == "catchup"


def test_failed_retry_throttle() -> None:
    now_utc = datetime(2026, 6, 1, 7, 0, tzinfo=timezone.utc)
    recent_fail = ReportDeliveryRecord(
        sent_at=now_utc - timedelta(minutes=10),
        problem_count=0,
        recorders_with_errors=0,
        category_counts={},
        status="failed",
        error="smtp",
    )
    last_ok = datetime(2026, 5, 31, 20, 0, tzinfo=timezone.utc)
    history = ReportDeliveryHistory(
        entries=[_success_at(last_ok), recent_fail]
    )
    decision = should_send_report(
        now_utc.astimezone(MSK),
        _settings(failed_retry_minutes=60),
        history,
        display_tz=MSK,
    )
    assert decision.should_send is False


def test_history_store_append_and_trim(tmp_path: Path) -> None:
    store = ReportDeliveryHistoryStore(tmp_path / "history.json")
    now = datetime(2026, 6, 1, tzinfo=timezone.utc)
    for i in range(5):
        store.append(
            ReportDeliveryRecord(
                sent_at=now + timedelta(days=i),
                problem_count=i,
                recorders_with_errors=i,
                category_counts={},
                status="success",
            ),
            max_entries=3,
        )
    loaded = store.load()
    assert len(loaded.entries) == 3
    assert loaded.entries[0].problem_count == 2


def test_report_metrics_from_context() -> None:
    rec = SimpleNamespace(
        id="r1",
        object_name="Obj",
        name="NVR",
        host="1.2.3.4",
        port=80,
        use_https=False,
    )
    report = ErrorReportContext(
        generated_at="01.06.2026",
        problem_count=2,
        rows=[
            ErrorReportRow(
                object_name="Obj",
                recorder=rec,
                recorder_display_name="NVR",
                web_url="http://x",
                web_link_title="x",
                system_kind="tsv",
                system_label="ТСВ",
                category_label="Время",
                status="error",
                status_label="Ошибка",
                value_display="—",
                reason="skew",
                polled_at_display="—",
            ),
            ErrorReportRow(
                object_name="Obj",
                recorder=rec,
                recorder_display_name="NVR",
                web_url="http://x",
                web_link_title="x",
                system_kind="tsv",
                system_label="ТСВ",
                category_label="HDD",
                status="warn",
                status_label="Внимание",
                value_display="—",
                reason="hot",
                polled_at_display="—",
            ),
        ],
    )
    pc, nvr, cats = report_metrics_from_context(report)
    assert pc == 2
    assert nvr == 1
    assert cats == {"Время": 1, "HDD": 1}


def test_tick_sync_sends_and_records(tmp_path: Path) -> None:
    from app.report_delivery import ReportDeliveryService

    config = SimpleNamespace(
        email_report=_settings(
            from_email="from@test",
            to_emails=["to@test"],
            smtp_user="user",
        ),
        monitoring=SimpleNamespace(ntp_server="", display_timezone="Europe/Moscow"),
        credentials=SimpleNamespace(username="a", password="b"),
        exclusions=SimpleNamespace(recorder_ids=[]),
        recorders=[
            SimpleNamespace(
                id="r1",
                object_name="O",
                name="N",
                host="1.1.1.1",
                port=80,
                use_https=False,
            )
        ],
    )
    config_store = MagicMock()
    config_store.load.return_value = config
    config_store.list_recorders.return_value = config.recorders

    metrics_row = SimpleNamespace(recorder_id="r1")
    state_store = MagicMock()
    state_store.list_recorder_metrics.return_value = [metrics_row]
    state_store.category_problem_since_map.return_value = {}

    history_path = tmp_path / "hist.json"
    history_store = ReportDeliveryHistoryStore(history_path)

    service = ReportDeliveryService(
        config_store=config_store,
        state_store=state_store,
        history_store=history_store,
    )

    report = ErrorReportContext(
        generated_at="now",
        problem_count=1,
        rows=[],
    )

    with (
        patch(
            "app.report_delivery.build_error_report_context",
            return_value=report,
        ),
        patch(
            "app.report_delivery.render_error_report_html",
            return_value="<report/>",
        ),
        patch(
            "app.report_delivery.render_email_dashboard_html",
            return_value="<dash/>",
        ),
        patch("app.report_delivery.send_report_email") as send_mock,
        patch(
            "app.report_delivery.should_send_report",
            return_value=SendDecision(True, trigger="catchup", reason="test"),
        ),
    ):
        service.tick_sync()

    send_mock.assert_called_once()
    loaded = history_store.load()
    assert len(loaded.entries) == 1
    assert loaded.entries[0].status == "success"


def test_send_report_now_manual(tmp_path: Path) -> None:
    from app.report_delivery import ReportDeliveryService

    config = SimpleNamespace(
        email_report=_settings(
            from_email="from@test",
            to_emails=["to@test"],
        ),
        monitoring=SimpleNamespace(ntp_server="", display_timezone="Europe/Moscow"),
        credentials=SimpleNamespace(username="a", password="b"),
        exclusions=SimpleNamespace(recorder_ids=[]),
        recorders=[
            SimpleNamespace(
                id="r1",
                object_name="O",
                name="N",
                host="1.1.1.1",
                port=80,
                use_https=False,
            )
        ],
    )
    config_store = MagicMock()
    config_store.load.return_value = config
    config_store.list_recorders.return_value = config.recorders

    state_store = MagicMock()
    state_store.list_recorder_metrics.return_value = [
        SimpleNamespace(recorder_id="r1")
    ]
    state_store.category_problem_since_map.return_value = {}

    history_store = ReportDeliveryHistoryStore(tmp_path / "hist.json")
    service = ReportDeliveryService(
        config_store=config_store,
        state_store=state_store,
        history_store=history_store,
    )
    report = ErrorReportContext(generated_at="now", problem_count=2, rows=[])

    with (
        patch(
            "app.report_delivery.build_error_report_context",
            return_value=report,
        ),
        patch("app.report_delivery.render_error_report_html", return_value="<r/>"),
        patch("app.report_delivery.render_email_dashboard_html", return_value="<d/>"),
        patch("app.report_delivery.send_report_email") as send_mock,
    ):
        result = service.send_report_now(trigger="manual")

    assert result.ok is True
    send_mock.assert_called_once()
    assert history_store.load().entries[0].trigger == "manual"


def test_send_report_email_validates_recipients() -> None:
    from app.email_sender import send_report_email

    with pytest.raises(ValueError, match="to_emails"):
        send_report_email(
            _settings(from_email="a@b.c", to_emails=[]),
            body_html="",
            attachment_html="",
            attachment_filename="x.html",
        )
