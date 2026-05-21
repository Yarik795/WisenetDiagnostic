import json
from types import SimpleNamespace

from app.models import MonitoringSettings
from app.ui.health_dashboard import (
    aggregate_health_stats,
    list_health_problem_rows,
    object_health_problem_count,
)


def _rec(id="a", enabled=True):
    return SimpleNamespace(
        id=id,
        enabled=enabled,
        object_name="Obj",
        host="10.0.0.1",
        name="NVR",
    )


def _metrics(**kwargs):
    from datetime import datetime, timezone

    base = dict(
        last_polled_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        device_online=True,
        health_status="warn",
        disks_json=json.dumps([{"TemperatureCelsius": 55}]),
        system_events_json=json.dumps({"CPUFanError": False}),
        storage_used_percent=40.0,
        storage_status="Normal",
        channel_count=2,
        channels_ok=2,
        channels_warn=0,
        channels_error=0,
        channels_unknown=0,
        archive_min_days=25.0,
        archive_max_days=30.0,
        ntp_status="Success",
        time_skew_seconds=0.0,
        sync_type="ntp",
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_aggregate_health_stats_has_category_kpis() -> None:
    settings = MonitoringSettings()
    r1 = _rec("a")
    metrics_map = {"a": _metrics()}
    stats = aggregate_health_stats([r1], metrics_map, settings)
    assert stats.total_enabled == 1
    assert len(stats.category_kpis) == 6
    assert any(k.category == "temperature" for k in stats.category_kpis)


def test_problem_rows_include_temperature() -> None:
    settings = MonitoringSettings()
    r1 = _rec("a")
    metrics_map = {"a": _metrics()}
    rows = list_health_problem_rows([r1], metrics_map, settings)
    categories = {row.category for row in rows}
    assert "temperature" in categories


def test_object_health_problem_count() -> None:
    settings = MonitoringSettings()
    r1, r2 = _rec("a"), _rec("b")
    metrics_map = {
        "a": _metrics(),
        "b": _metrics(
            disks_json=json.dumps([{"TemperatureCelsius": 30}]),
            archive_min_days=31.0,
            archive_max_days=31.0,
        ),
    }
    assert object_health_problem_count([r1, r2], metrics_map, settings) == 1
