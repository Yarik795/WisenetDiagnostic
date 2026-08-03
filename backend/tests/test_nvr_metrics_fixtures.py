"""Парсинг и profile-gating по фрагментам из docs/nvr-api-check (санитизированные fixtures)."""

from pathlib import Path

from app.models import MonitoringSettings
from app.monitoring import evaluate_channel_health, evaluate_recorder_health
from app.sunapi_extended import is_analog_channel
from app.sunapi import DeviceInfo
from app.sunapi_extended import (
    ChannelInfo,
    EventChannelStatus,
    NvrApiProfile,
    RecorderPollData,
    StorageInfo,
    compute_stream_metrics,
    parse_cameraregister,
    parse_eventstatus,
    parse_storage,
)
from app.ui.metrics_helpers import (
    any_disk_format_required,
    disk_drop_datarate_percent,
    disk_power_on_hours,
    max_disk_drop_datarate_percent,
)

_FIXTURES = Path(__file__).parent / "fixtures"


def _read(name: str) -> str:
    return (_FIXTURES / name).read_text(encoding="utf-8")


def test_fixture_hrx1634_cameraregister_cpu() -> None:
    channels = parse_cameraregister(_read("hrx1634_cameraregister.txt"))
    by_no = {c.channel_no: c for c in channels}
    assert by_no[0].cpu_usage is not None
    assert by_no[0].data_rate is not None
    profile = NvrApiProfile.from_device(
        DeviceInfo(model="HRX-1634", cgi_version="2.6.0")
    )
    cpu_max, cpu_avg, rate_sum, zero_br, poe_off = compute_stream_metrics(
        channels, profile=profile
    )
    assert cpu_max is not None
    assert rate_sum is not None
    assert poe_off == 0


def test_fixture_hrx1620_cameraregister_no_poe_field() -> None:
    channels = parse_cameraregister(_read("hrx1620_cameraregister.txt"))
    assert all(ch.poe_status is None for ch in channels)
    assert channels[0].cpu_usage is not None
    profile = NvrApiProfile.from_device(
        DeviceInfo(model="HRX-1620", cgi_version="2.5.6")
    )
    assert profile.supports_poe_status is False
    _, _, _, _, poe_off = compute_stream_metrics(channels, profile=profile)
    assert poe_off == 0


def test_fixture_hrx1634_storage_modern_fields() -> None:
    profile = NvrApiProfile.from_device(
        DeviceInfo(model="HRX-1634", cgi_version="2.6.0")
    )
    info = parse_storage(
        _read("hrx1634_storageinfo.txt"), model="HRX-1634", profile=profile
    )
    assert profile.supports_modern_storage_metrics is True
    assert len(info.disks) >= 1
    disk = info.disks[0]
    assert disk_drop_datarate_percent(disk) == 0.0
    assert disk_power_on_hours(disk) is not None
    assert any_disk_format_required(info.disks) is False


def test_fixture_hrx1620_storage_no_drop_fields() -> None:
    body = "Storage.1.Model=WD_RED\nStorage.1.Temperature=46°C/114°F\n"
    profile = NvrApiProfile.from_device(
        DeviceInfo(model="HRX-1620", cgi_version="2.5.6")
    )
    info = parse_storage(body, model="HRX-1620", profile=profile)
    assert profile.supports_modern_storage_metrics is False
    assert max_disk_drop_datarate_percent(info.disks) is None


def test_fixture_hrx1620_storage_sample_from_nvr_samples() -> None:
    body = _read("hrx1620_storageinfo.txt")
    profile = NvrApiProfile.from_device(
        DeviceInfo(model="HRX-1620", cgi_version="2.5.6")
    )
    info = parse_storage(body, model="HRX-1620", profile=profile)
    assert len(info.disks) == 1
    assert disk_power_on_hours(info.disks[0]) is None


def test_fixture_xrn2010_storage_sample_from_nvr_samples() -> None:
    body = _read("xrn2010_storageinfo.txt")
    profile = NvrApiProfile.from_device(
        DeviceInfo(model="XRN-2010A", cgi_version="2.5.4")
    )
    info = parse_storage(body, model="XRN-2010A", profile=profile)
    assert len(info.disks) == 2
    assert all(disk_power_on_hours(d) is None for d in info.disks)


def test_eventstatus_quality_flags_from_fixture() -> None:
    body = _read("hrx1634_eventstatus_snippet.txt")
    body += "Channel.0.LowFps=True\nChannel.0.Tampering=False\n"
    result = parse_eventstatus(body)
    ch0 = next(e for e in result.channels if e.channel_no == 0)
    assert ch0.low_fps is True
    assert ch0.tampering is False


def test_analog_channel_zero_bitrate_is_ok() -> None:
    ch = ChannelInfo(
        channel_no=0,
        name="Analog CAM",
        camera_model="Analog CAM",
        video_state="On",
        data_rate=0.0,
        cpu_usage=0.0,
    )
    assert is_analog_channel(ch)
    status, reason = evaluate_channel_health(ch, None, MonitoringSettings())
    assert status == "ok"
    assert "аналог" in reason.lower()


def test_poe_off_does_not_affect_channel_health() -> None:
    ch = ChannelInfo(
        channel_no=0,
        source_state="On",
        camera_ip="10.0.0.5",
        camera_model="QND-6082R",
        video_state="On",
        data_rate=2.5,
        poe_status=False,
    )
    profile = NvrApiProfile.from_device(
        DeviceInfo(model="XRN-6410B2", cgi_version="2.6.0")
    )
    status, reason = evaluate_channel_health(
        ch, None, MonitoringSettings(), profile=profile
    )
    assert status == "ok"
    assert "poe" not in reason.lower()


def test_channel_health_low_fps_warn() -> None:
    ch = ChannelInfo(
        channel_no=0,
        source_state="On",
        camera_ip="10.0.0.1",
        video_state="On",
    )
    event = EventChannelStatus(channel_no=0, low_fps=True)
    status, reason = evaluate_channel_health(ch, event, MonitoringSettings())
    assert status == "warn"
    assert "FPS" in reason


def test_recorder_health_format_required_disk() -> None:
    poll = RecorderPollData(
        online=True,
        storage=StorageInfo(
            disks=[{"Storage": "1", "FormatRequired": "true"}],
            storageinfo_ok=True,
        ),
    )
    profile = NvrApiProfile.from_device(
        DeviceInfo(model="XRN-3210B2", cgi_version="2.6.0")
    )
    status, reason = evaluate_recorder_health(
        poll, ["ok"], MonitoringSettings(), profile=profile
    )
    assert status == "error"
    assert "форматирован" in reason.lower()
