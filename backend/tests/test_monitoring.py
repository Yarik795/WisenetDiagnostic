from datetime import datetime, timezone
from pathlib import Path

from app.config_store import ConfigStore
from app.models import MonitoringSettings, Recorder
from app.monitoring import (
    apply_poll_result,
    archive_bounds,
    evaluate_channel_health,
    evaluate_recorder_health,
)
from app.state_store import StateStore
from app.sunapi import DeviceInfo
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


def test_network_camera_connect_false_is_error_for_on_channel() -> None:
    ch = ChannelInfo(channel_no=22, source_state="On", camera_ip="10.0.0.22")
    event = EventChannelStatus(channel_no=22, connected=False)
    status, reason = evaluate_channel_health(ch, event, _settings())
    assert status == "error"
    assert "не подключена" in reason.lower()


def test_deactive_with_disconnect_is_unknown() -> None:
    ch = ChannelInfo(channel_no=3, source_state="Deactive", register_status="Disconnected")
    event = EventChannelStatus(channel_no=3, connected=False)
    status, _ = evaluate_channel_health(ch, event, _settings())
    assert status == "unknown"


def test_on_connectfail_is_error_without_live_event() -> None:
    ch = ChannelInfo(
        channel_no=0,
        source_state="On",
        camera_ip="10.0.0.5",
        register_status="ConnectFail",
    )
    status, reason = evaluate_channel_health(ch, None, _settings())
    assert status == "error"
    assert "ConnectFail" in reason


def test_on_connectfail_is_error_on_unsupported_model() -> None:
    ch = ChannelInfo(
        channel_no=0,
        source_state="On",
        camera_ip="10.0.0.5",
        register_status="ConnectFail",
        data_rate=2.9,
    )
    event = EventChannelStatus(channel_no=0, connected=True, video_loss=False)
    status, reason = evaluate_channel_health(
        ch, event, _settings(), device_model="XRN-3210B2"
    )
    assert status == "error"
    assert "ConnectFail" in reason


def test_stale_connectfail_xrn2010_live_stream_is_ok() -> None:
    ch = ChannelInfo(
        channel_no=8,
        source_state="On",
        camera_ip="100.111.2.123",
        register_status="ConnectFail",
        data_rate=2.911,
    )
    event = EventChannelStatus(channel_no=8, connected=True, video_loss=False)
    status, reason = evaluate_channel_health(
        ch, event, _settings(), device_model="XRN-2010"
    )
    assert status == "ok"
    assert "ConnectFail" in reason
    assert "поток в норме" in reason


def test_stale_connectfail_hrx1620_live_stream_is_ok() -> None:
    ch = ChannelInfo(
        channel_no=4,
        source_state="On",
        register_status="ConnectFail",
        data_rate=1.2,
    )
    event = EventChannelStatus(channel_no=4, connected=True, video_loss=False)
    status, _ = evaluate_channel_health(
        ch, event, _settings(), device_model="HRX-1620"
    )
    assert status == "ok"


def test_stale_connectfail_zero_datarate_still_error() -> None:
    ch = ChannelInfo(
        channel_no=8,
        source_state="On",
        register_status="ConnectFail",
        data_rate=0.0,
    )
    event = EventChannelStatus(channel_no=8, connected=True, video_loss=False)
    status, reason = evaluate_channel_health(
        ch, event, _settings(), device_model="XRN-2010P"
    )
    assert status == "error"
    assert "ConnectFail" in reason


def test_stale_connectfail_video_loss_still_error() -> None:
    ch = ChannelInfo(
        channel_no=8,
        source_state="On",
        register_status="ConnectFail",
        data_rate=2.9,
    )
    event = EventChannelStatus(channel_no=8, connected=True, video_loss=True)
    status, reason = evaluate_channel_health(
        ch, event, _settings(), device_model="XRN-2010"
    )
    assert status == "error"
    assert "VideoLoss" in reason


def test_on_disconnected_is_error() -> None:
    ch = ChannelInfo(
        channel_no=1,
        source_state="On",
        register_status="Disconnected",
    )
    status, _ = evaluate_channel_health(ch, None, _settings())
    assert status == "error"


def test_short_poll_preserves_channels(tmp_path: Path) -> None:
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    config_store = ConfigStore(path=tmp_path / "config.json")
    recorder = Recorder(
        id="nvr1",
        object_name="Obj",
        host="10.0.0.1",
        port=80,
    )
    state.upsert_channel(
        "nvr1",
        0,
        name="Cam 0",
        source_state="On",
        health_status="ok",
    )
    state.upsert_channel(
        "nvr1",
        1,
        name="Cam 1",
        source_state="Deactive",
        health_status="unknown",
    )
    state.upsert_recorder_metrics(
        "nvr1",
        device_online=True,
        channel_count=2,
        channels_ok=1,
        channels_unknown=1,
    )
    poll = RecorderPollData(
        online=True,
        channels_polled=False,
        events=[EventChannelStatus(channel_no=0, connected=True)],
    )
    apply_poll_result(
        config_store,
        state,
        recorder,
        poll,
        _settings(),
        datetime.now(timezone.utc),
        update_config=False,
    )
    channels = state.list_channels("nvr1")
    assert len(channels) == 2
    metrics = state.get_recorder_metrics("nvr1")
    assert metrics is not None
    assert metrics.channel_count == 2
    assert metrics.channels_ok == 1
    assert metrics.channels_unknown == 1


def test_short_poll_deactive_channel_not_error(tmp_path: Path) -> None:
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    config_store = ConfigStore(path=tmp_path / "config.json")
    recorder = Recorder(
        id="nvr1",
        object_name="Obj",
        host="10.0.0.1",
        port=80,
    )
    poll = RecorderPollData(
        online=True,
        channels_polled=True,
        channels=[
            ChannelInfo(
                channel_no=3,
                source_state="Deactive",
                camera_model="UNKNOWN",
            )
        ],
        events=[EventChannelStatus(channel_no=3, connected=False)],
    )
    apply_poll_result(
        config_store,
        state,
        recorder,
        poll,
        _settings(),
        datetime.now(timezone.utc),
        update_config=False,
    )
    ch = state.get_channel("nvr1", 3)
    assert ch is not None
    assert ch.health_status == "unknown"
    assert "деактивирован" in (ch.health_reason or "").lower()
    assert "не подключена" not in (ch.health_reason or "").lower()
    assert ch.source_state == "Deactive"


def test_upsert_preserves_source_state_when_poll_missing_state(
    tmp_path: Path,
) -> None:
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    config_store = ConfigStore(path=tmp_path / "config.json")
    recorder = Recorder(
        id="nvr1",
        object_name="Obj",
        host="10.0.0.1",
        port=80,
    )
    state.upsert_channel(
        "nvr1",
        3,
        source_state="Deactive",
        health_status="unknown",
        health_reason="Канал деактивирован (не используется)",
    )
    poll = RecorderPollData(
        online=True,
        channels_polled=True,
        channels=[ChannelInfo(channel_no=3, camera_model="UNKNOWN")],
        events=[EventChannelStatus(channel_no=3, connected=False)],
    )
    apply_poll_result(
        config_store,
        state,
        recorder,
        poll,
        _settings(),
        datetime.now(timezone.utc),
        update_config=False,
    )
    ch = state.get_channel("nvr1", 3)
    assert ch is not None
    assert ch.source_state == "Deactive"
    assert ch.health_status == "unknown"
    assert "не подключена" not in (ch.health_reason or "").lower()


def test_recorder_cpu_fan_error() -> None:
    poll = RecorderPollData(
        online=True,
        system_events={"CPUFanError": True, "FrameFanError": False},
    )
    status, reason = evaluate_recorder_health(poll, ["ok"], _settings())
    assert status == "error"
    assert "Вентилятор CPU" in reason


def test_recorder_hdd_none_error() -> None:
    poll = RecorderPollData(
        online=True,
        system_events={"HDDNone": True},
    )
    status, reason = evaluate_recorder_health(poll, ["ok"], _settings())
    assert status == "error"
    assert "Накопитель отсутствует" in reason


def test_recorder_hdd_fail_and_cpu_overload_warn() -> None:
    poll = RecorderPollData(
        online=True,
        system_events={"HDDFail": True, "CpuOverload": True},
    )
    status, reason = evaluate_recorder_health(poll, ["ok"], _settings())
    assert status == "error"
    assert "Сбой HDD" in reason
    assert "Перегрузка CPU" in reason


def test_recorder_system_events_ok() -> None:
    poll = RecorderPollData(
        online=True,
        system_events={"CPUFanError": False, "FrameFanError": False},
    )
    status, reason = evaluate_recorder_health(poll, ["ok"], _settings())
    assert status == "ok"


def test_recorder_hdd_temperature_warn() -> None:
    from app.sunapi_extended import StorageInfo

    poll = RecorderPollData(
        online=True,
        storage=StorageInfo(
            disks=[{"TemperatureCelsius": 52}],
            used_percent=40.0,
        ),
    )
    settings = MonitoringSettings(
        hdd_temperature_warn_celsius=50,
        hdd_temperature_error_celsius=60,
    )
    status, reason = evaluate_recorder_health(poll, ["ok"], settings)
    assert status == "warn"
    assert "Температура HDD" in reason


def test_recorder_archive_critical_error() -> None:
    settings = MonitoringSettings(archive_days_error_threshold=7)
    poll = RecorderPollData(online=True)
    status, reason = evaluate_recorder_health(
        poll,
        ["ok"],
        settings,
        archive_min_days=3.0,
        archive_max_days=10.0,
    )
    assert status == "error"
    assert "критично" in reason.lower()


def test_apply_poll_result_records_category_history(tmp_path: Path) -> None:
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    config_store = ConfigStore(path=tmp_path / "config.json")
    recorder = Recorder(
        id="nvr1",
        object_name="Obj",
        host="10.0.0.1",
        port=80,
    )
    polled_at = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    poll = RecorderPollData(
        online=True,
        system_events={"CPUFanError": True},
        channels_polled=False,
    )
    state.upsert_recorder_metrics(
        "nvr1",
        device_online=True,
        last_polled_at=polled_at,
    )
    apply_poll_result(
        config_store,
        state,
        recorder,
        poll,
        _settings(),
        polled_at,
        update_config=False,
    )
    history = state.list_category_history(recorder_id="nvr1")
    categories = {row.category for row in history}
    assert "fans" in categories
    assert "time" in categories
    fans_rows = [r for r in history if r.category == "fans"]
    assert fans_rows[-1].status == "error"
    assert state.get_category_problem_since("nvr1", "fans") == polled_at


def test_apply_poll_result_stores_serial_and_manufacture_date(tmp_path: Path) -> None:
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    config_store = ConfigStore(path=tmp_path / "config.json")
    recorder = Recorder(id="nvr1", object_name="Obj", host="10.0.0.1", port=80)
    poll = RecorderPollData(
        online=True,
        device=DeviceInfo(
            model="XRN-3210B2",
            device_type="NVR",
            serial_number="ZNWH6V4N90000KJ",
        ),
    )
    apply_poll_result(
        config_store,
        state,
        recorder,
        poll,
        _settings(),
        datetime.now(timezone.utc),
        update_config=False,
    )
    metrics = state.get_recorder_metrics("nvr1")
    assert metrics is not None
    assert metrics.serial_number == "ZNWH6V4N90000KJ"
    assert metrics.manufacture_date == "2020-09"


def test_apply_poll_result_preserves_serial_when_offline(tmp_path: Path) -> None:
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    config_store = ConfigStore(path=tmp_path / "config.json")
    recorder = Recorder(id="nvr1", object_name="Obj", host="10.0.0.1", port=80)
    state.upsert_recorder_metrics(
        "nvr1",
        serial_number="ZNWH6V4N90000KJ",
        manufacture_date="2020-09",
    )
    poll = RecorderPollData(online=False, error="timeout")
    apply_poll_result(
        config_store,
        state,
        recorder,
        poll,
        _settings(),
        datetime.now(timezone.utc),
        update_config=False,
    )
    metrics = state.get_recorder_metrics("nvr1")
    assert metrics is not None
    assert metrics.serial_number == "ZNWH6V4N90000KJ"
    assert metrics.manufacture_date == "2020-09"


def test_apply_poll_result_ignores_camera_serial(tmp_path: Path) -> None:
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    config_store = ConfigStore(path=tmp_path / "config.json")
    recorder = Recorder(id="nvr1", object_name="Obj", host="10.0.0.1", port=80)
    poll = RecorderPollData(
        online=True,
        device=DeviceInfo(
            model="QND-6082R",
            device_type="NWC",
            serial_number="ZNWH6V4N90000KJ",
        ),
    )
    apply_poll_result(
        config_store,
        state,
        recorder,
        poll,
        _settings(),
        datetime.now(timezone.utc),
        update_config=False,
    )
    metrics = state.get_recorder_metrics("nvr1")
    assert metrics is not None
    assert metrics.serial_number is None
    assert metrics.manufacture_date is None
