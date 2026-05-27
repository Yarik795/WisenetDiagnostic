import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.models import Credentials, MonitoringSettings
from app.state_store import RecorderMetricsRow
from app.ui.helpers import device_web_interface_url, device_web_link_title
from app.ui.error_report import (
    build_error_report_context,
    format_problem_age_display,
    _problem_age_fields,
)


def _rec(**kwargs):
    base = dict(
        id="r1",
        object_name="ВСП-001",
        name="NVR-main",
        host="192.168.1.10",
        port=80,
        use_https=False,
        enabled=True,
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_device_web_interface_url_plain() -> None:
    url = device_web_interface_url(_rec())
    assert url == "http://192.168.1.10"


def test_device_web_interface_url_userinfo() -> None:
    creds = Credentials(username="admin", password="p@ss:word")
    url = device_web_interface_url(
        _rec(), credentials=creds, device_auth="userinfo"
    )
    assert url.startswith("http://admin:p%40ss%3Aword@192.168.1.10")


def test_device_web_link_title() -> None:
    assert device_web_link_title(_rec()) == "Открыть web-интерфейс NVR: NVR-main"


def test_build_error_report_empty() -> None:
    ctx = build_error_report_context([], {}, MonitoringSettings())
    assert ctx.problem_count == 0
    assert ctx.rows == []


def test_problem_age_fields() -> None:
    since = datetime(2026, 5, 10, 8, 0, tzinfo=timezone.utc)
    now = since + timedelta(days=5, hours=3)
    days, since_disp, title = _problem_age_fields(
        "r1",
        "archive",
        {("r1", "archive"): since},
        now=now,
    )
    assert days == "5 сут. 3 ч."
    assert since_disp == "10.05.2026 11:00"
    assert "10.05.2026" in title


def test_format_problem_age_display_hours() -> None:
    since = datetime(2026, 5, 26, 14, 33, tzinfo=timezone.utc)
    now = since + timedelta(hours=17)
    assert format_problem_age_display(since, now) == "17 ч."


def test_format_problem_age_display_less_than_hour() -> None:
    since = datetime(2026, 5, 26, 14, 0, tzinfo=timezone.utc)
    now = since + timedelta(minutes=20)
    assert format_problem_age_display(since, now) == "менее 1 ч."


def test_build_error_report_includes_problem_age() -> None:
    polled = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    since = polled - timedelta(days=3)
    rec = _rec()
    metrics = RecorderMetricsRow(
        recorder_id="r1",
        model=None,
        firmware_version=None,
        device_online=True,
        health_status="warn",
        health_reason=None,
        ntp_status="Success",
        time_skew_seconds=0.0,
        storage_used_percent=40.0,
        storage_status="Normal",
        archive_start=None,
        archive_end=None,
        archive_days=25.0,
        channel_count=2,
        channels_ok=2,
        channels_warn=0,
        channels_error=0,
        channels_unknown=0,
        last_polled_at=polled,
        disks_json='[{"TemperatureCelsius": 55}]',
        archive_min_days=25.0,
        archive_max_days=30.0,
    )
    ctx = build_error_report_context(
        [rec],
        {"r1": metrics},
        MonitoringSettings(
            hdd_temperature_warn_celsius=50,
            hdd_temperature_error_celsius=60,
        ),
        problem_since_map={("r1", "temperature"): since},
        report_at=polled,
    )
    assert ctx.problem_count >= 1
    temp_row = next(r for r in ctx.rows if r.category_label == "Температура HDD")
    assert temp_row.problem_age_days_display == "3 сут."
    assert "17.05.2026" in temp_row.problem_since_display


def test_build_error_report_hrx_no_hdd() -> None:
    polled = datetime(2026, 5, 27, 12, 0, tzinfo=timezone.utc)
    rec = _rec(id="hrx-no-hdd")
    metrics = RecorderMetricsRow(
        recorder_id="hrx-no-hdd",
        model="HRX-1634",
        firmware_version=None,
        device_online=True,
        health_status="error",
        health_reason=None,
        ntp_status="Success",
        time_skew_seconds=0.0,
        storage_used_percent=None,
        storage_status=None,
        archive_start=None,
        archive_end=None,
        archive_days=None,
        channel_count=18,
        channels_ok=13,
        channels_warn=0,
        channels_error=0,
        channels_unknown=5,
        last_polled_at=polled,
        disks_json="[]",
        system_events_json=json.dumps({"HDDNone": True, "HDDFail": False}),
        storageinfo_ok=True,
        archive_poll_error="604",
        recording_storage_enable=False,
        archive_min_days=None,
        archive_max_days=None,
    )
    ctx = build_error_report_context(
        [rec],
        {"hrx-no-hdd": metrics},
        MonitoringSettings(),
        report_at=polled,
    )
    storage_rows = [r for r in ctx.rows if r.category_label == "Накопители"]
    assert len(storage_rows) == 1
    assert storage_rows[0].status == "error"
    archive_rows = [r for r in ctx.rows if r.category_label == "Глубина архива"]
    assert len(archive_rows) == 1
    assert archive_rows[0].status == "error"
