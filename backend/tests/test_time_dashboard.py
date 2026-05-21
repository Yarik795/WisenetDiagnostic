from types import SimpleNamespace

from app.models import MonitoringSettings
from app.ui.time_dashboard import (
    aggregate_time_stats,
    classify_time_health,
    is_fixable_recorder,
    list_fixable_recorders,
    list_problem_rows,
    object_time_problem_count,
)


def _rec(enabled=True, id="r1", object_name="Obj"):
    return SimpleNamespace(
        id=id,
        enabled=enabled,
        object_name=object_name,
        host="10.0.0.1",
        name="NVR",
    )


def _metrics(**kwargs):
    base = dict(
        last_polled_at="2026-01-01",
        device_online=True,
        health_status="ok",
        sync_type="NTP",
        ntp_status="Success",
        time_skew_seconds=0.5,
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_classify_ok() -> None:
    settings = MonitoringSettings()
    assert (
        classify_time_health(_rec(), _metrics(), settings) == "ok"
    )


def test_classify_error_skew() -> None:
    settings = MonitoringSettings(time_skew_error_seconds=300)
    assert (
        classify_time_health(
            _rec(), _metrics(time_skew_seconds=400), settings
        )
        == "error"
    )


def test_classify_warn_ntp_fail() -> None:
    settings = MonitoringSettings()
    assert (
        classify_time_health(
            _rec(), _metrics(ntp_status="Fail"), settings
        )
        == "warn"
    )


def test_aggregate_and_fixable() -> None:
    settings = MonitoringSettings()
    r1, r2 = _rec(id="a"), _rec(id="b")
    metrics_map = {
        "a": _metrics(time_skew_seconds=0.5),
        "b": _metrics(sync_type="Manual", time_skew_seconds=0.0),
    }
    stats = aggregate_time_stats([r1, r2], metrics_map, settings)
    assert stats.total_enabled == 2
    assert stats.ok == 1
    assert stats.warn == 1
    assert stats.fixable == 1
    assert stats.has_problems is True
    fixable = list_fixable_recorders([r1, r2], metrics_map)
    assert len(fixable) == 1
    assert fixable[0].id == "b"


def test_problem_rows_sorted() -> None:
    settings = MonitoringSettings()
    r1, r2 = _rec(id="a", object_name="B"), _rec(id="b", object_name="A")
    metrics_map = {
        "a": _metrics(time_skew_seconds=90),
        "b": _metrics(time_skew_seconds=400),
    }
    rows = list_problem_rows([r1, r2], metrics_map, settings)
    assert len(rows) == 2
    assert rows[0].category == "error"


def test_object_time_problem_count() -> None:
    settings = MonitoringSettings()
    recorders = [_rec(id="a"), _rec(id="b")]
    metrics_map = {
        "a": _metrics(),
        "b": _metrics(ntp_status="Fail"),
    }
    assert object_time_problem_count(recorders, metrics_map, settings) == 1
