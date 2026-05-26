import json
from types import SimpleNamespace

from app.models import MonitoringSettings
from app.ui.health_classifiers import (
    classify_archive_health,
    classify_category,
    classify_storage_health,
    classify_fans_health,
    classify_temperature_health,
    recorder_problem_badges,
)


def _rec(enabled=True, id="r1"):
    return SimpleNamespace(id=id, enabled=enabled, object_name="Obj", host="10.0.0.1", name="NVR")


def _metrics(**kwargs):
    base = dict(
        last_polled_at="2026-01-01",
        device_online=True,
        disks_json=None,
        system_events_json=None,
        storage_used_percent=50.0,
        storage_status="Normal",
        channel_count=4,
        channels_ok=4,
        channels_warn=0,
        channels_error=0,
        channels_unknown=0,
        archive_min_days=25.0,
        archive_max_days=30.0,
        archive_days=30.0,
        ntp_status="Success",
        time_skew_seconds=0.0,
        sync_type="ntp",
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def _settings() -> MonitoringSettings:
    return MonitoringSettings(
        hdd_temperature_warn_celsius=50,
        hdd_temperature_error_celsius=60,
        archive_days_required=30,
        archive_days_error_threshold=7,
    )


def test_temperature_warn_and_error() -> None:
    disks = [{"TemperatureCelsius": 55}]
    metrics = _metrics(disks_json=json.dumps(disks))
    status, reason = classify_temperature_health(_rec(), metrics, _settings())
    assert status == "warn"
    assert "55" in reason

    disks_hot = [{"TemperatureCelsius": 62}]
    metrics_hot = _metrics(disks_json=json.dumps(disks_hot))
    status2, _ = classify_temperature_health(_rec(), metrics_hot, _settings())
    assert status2 == "error"


def test_temperature_unknown_without_data() -> None:
    status, reason = classify_temperature_health(_rec(), _metrics(disks_json=None), _settings())
    assert status == "unknown"
    assert "не возвращается" in reason.lower()


def test_fans_error() -> None:
    events = json.dumps({"CPUFanError": True, "FrameFanError": False})
    status, reason = classify_fans_health(_rec(), _metrics(system_events_json=events), _settings())
    assert status == "error"
    assert "CPU" in reason


def test_archive_warn_and_critical() -> None:
    status, _ = classify_archive_health(
        _rec(), _metrics(archive_min_days=20.0), _settings()
    )
    assert status == "warn"

    status2, reason2 = classify_archive_health(
        _rec(), _metrics(archive_min_days=3.0), _settings()
    )
    assert status2 == "error"
    assert "критично" in reason2.lower()


def test_recorder_problem_badges() -> None:
    events = json.dumps({"CPUFanError": True})
    metrics = _metrics(
        disks_json=json.dumps([{"TemperatureCelsius": 55}]),
        system_events_json=events,
        archive_min_days=5.0,
    )
    badges = recorder_problem_badges(_rec(), metrics, _settings())
    codes = {b[0] for b in badges}
    assert "TEMP" in codes
    assert "FAN" in codes
    assert "ARCH" in codes


def test_classify_channels_mass_failure() -> None:
    settings = MonitoringSettings(channels_error_threshold_percent=25)
    metrics = _metrics(channel_count=4, channels_error=2, channels_ok=2)
    status, reason = classify_category("channels", _rec(), metrics, settings)
    assert status == "error"
    assert "50" in reason or "2" in reason


def test_classify_storage_ok_from_disks_without_aggregate_percent() -> None:
    disks = [
        {
            "Storage": "1",
            "Status": "Normal",
            "UsedSpace": 5877391,
            "TotalSpace": 5877391,
        },
        {
            "Storage": "2",
            "Status": "Normal",
            "UsedSpace": 5925804,
            "TotalSpace": 5925804,
        },
    ]
    metrics = _metrics(storage_used_percent=None, disks_json=json.dumps(disks))
    status, reason = classify_storage_health(_rec(), metrics, _settings())
    assert status == "ok"
    assert "94.3" in reason or "Заполнение" in reason


def test_classify_channels_single_error_is_warn() -> None:
    settings = MonitoringSettings(channels_error_threshold_percent=25)
    metrics = _metrics(channel_count=10, channels_error=1, channels_ok=9)
    status, reason = classify_category("channels", _rec(), metrics, settings)
    assert status == "warn"
    assert "1" in reason
