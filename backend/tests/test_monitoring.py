from app.models import MonitoringSettings
from app.monitoring import (
    archive_bounds,
    evaluate_channel_health,
    evaluate_recorder_health,
)
from app.sunapi_extended import (
    ChannelInfo,
    EventChannelStatus,
    RecorderPollData,
    RecordingPeriodInfo,
)


def _settings() -> MonitoringSettings:
    return MonitoringSettings()


def test_deactive_channel_is_unknown_not_error() -> None:
    ch = ChannelInfo(channel_no=1, source_state="Deactive")
    status, reason = evaluate_channel_health(ch, None, _settings())
    assert status == "unknown"
    assert "деактивирован" in reason.lower()


def test_off_channel_is_warn() -> None:
    ch = ChannelInfo(channel_no=2, source_state="Off")
    status, reason = evaluate_channel_health(ch, None, _settings())
    assert status == "warn"
    assert "выключен" in reason.lower()


def test_on_with_video_loss_is_error() -> None:
    ch = ChannelInfo(channel_no=0, source_state="On", camera_ip="10.0.0.1")
    event = EventChannelStatus(channel_no=0, video_loss=True)
    status, reason = evaluate_channel_health(ch, event, _settings())
    assert status == "error"
    assert "VideoLoss" in reason


def test_deactive_ignores_video_loss() -> None:
    ch = ChannelInfo(channel_no=1, source_state="Deactive")
    event = EventChannelStatus(channel_no=1, video_loss=True)
    status, _ = evaluate_channel_health(ch, event, _settings())
    assert status == "unknown"


def test_archive_bounds_min_max() -> None:
    periods = {
        0: RecordingPeriodInfo(archive_days=12.5),
        1: RecordingPeriodInfo(archive_days=31.2),
        2: RecordingPeriodInfo(archive_days=20.0),
    }
    min_d, max_d = archive_bounds(periods)
    assert min_d == 12.5
    assert max_d == 31.2


def test_recorder_warn_when_min_archive_below_norm() -> None:
    poll = RecorderPollData(online=True)
    status, reason = evaluate_recorder_health(
        poll,
        ["ok"],
        _settings(),
        archive_min_days=8.0,
        archive_max_days=25.0,
    )
    assert status == "warn"
    assert "8.0-25.0" in reason


def test_recorder_ok_when_only_deactive_channels() -> None:
    poll = RecorderPollData(online=True)
    status, reason = evaluate_recorder_health(poll, ["unknown", "unknown"], _settings())
    assert status == "ok"
    assert "неисправные каналы" not in reason.lower()
