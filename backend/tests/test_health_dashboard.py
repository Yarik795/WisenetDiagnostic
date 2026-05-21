import json
from types import SimpleNamespace

from app.models import MonitoringSettings
from app.ui.health_dashboard import (
    aggregate_category_stats,
    build_category_sections,
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


def test_build_category_sections_count_and_order() -> None:
    settings = MonitoringSettings()
    sections = build_category_sections([_rec()], {"a": _metrics()}, settings)
    assert len(sections) == 6
    assert sections[0].category == "time"
    assert sections[0].is_time is True
    assert sections[1].category == "temperature"


def test_temperature_section_rows_only_temperature() -> None:
    settings = MonitoringSettings()
    metrics_map = {"a": _metrics()}
    sections = build_category_sections([_rec()], metrics_map, settings)
    temp = next(s for s in sections if s.category == "temperature")
    assert temp.stats is not None
    assert temp.stats.warn >= 1
    assert all(r.category == "temperature" for r in temp.problem_rows)


def test_aggregate_category_stats() -> None:
    settings = MonitoringSettings()
    stats = aggregate_category_stats(
        "temperature", [_rec()], {"a": _metrics()}, settings
    )
    assert stats.total_enabled == 1
    assert stats.warn == 1
    assert stats.has_problems is True


def test_list_health_problem_rows_filtered() -> None:
    settings = MonitoringSettings()
    rows = list_health_problem_rows(
        [_rec()],
        {"a": _metrics()},
        settings,
        category_filter="temperature",
    )
    assert len(rows) == 1
    assert rows[0].category == "temperature"


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
