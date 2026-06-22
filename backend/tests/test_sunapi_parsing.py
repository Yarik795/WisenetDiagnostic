import json

from app.sunapi import DeviceInfo
from app.sunapi_parsing import (
    RECORD_FRAME_DROP_LOG_TYPE,
    parse_systemlog_latest_timestamp,
)
from app.sunapi_extended import (
    ChannelInfo,
    NvrApiProfile,
    _is_diskutility_error,
    _to_float,
    compute_stream_metrics,
    extract_disk_temperature,
    format_celsius_only_temperature,
    merge_channels,
    merge_disk_temperatures,
    normalize_disk_record,
    parse_cameraregister,
    parse_diskutility_detail,
    parse_diskutility_list,
    parse_eventstatus,
    parse_recording_period,
    parse_recording_storage,
    parse_storage,
    parse_sunapi_error_body,
    parse_temperature_from_smart,
    parse_videosource_channels,
)


def test_parse_videosource_text() -> None:
    body = """
Channel.0.Name=Cam 01
Channel.0.State=On
Channel.1.Name=Cam 02
Channel.1.State=Deactive
"""
    channels = parse_videosource_channels(body)
    assert len(channels) == 2
    assert channels[0].channel_no == 0
    assert channels[0].name == "Cam 01"
    assert channels[1].source_state == "Deactive"


def test_parse_cameraregister_json() -> None:
    body = """
{
  "RegisteredCameras": [
    {"Channel": 0, "Model": "XNV-6080", "IPAddress": "10.0.0.5", "Status": "Success"}
  ]
}
"""
    ch = parse_cameraregister(body)
    assert ch[0].camera_ip == "10.0.0.5"
    assert ch[0].camera_model == "XNV-6080"


def test_parse_eventstatus_videoloss() -> None:
    body = """
Channel.0.Videoloss=True
Channel.0.Connected=False
Channel.1.Videoloss=False
Channel.1.Connected=True
"""
    result = parse_eventstatus(body)
    by_ch = {e.channel_no: e for e in result.channels}
    assert by_ch[0].video_loss is True
    assert by_ch[0].connected is False
    assert by_ch[1].video_loss is False
    assert by_ch[1].connected is True


def test_parse_eventstatus_network_camera_connect() -> None:
    body = """
Channel.0.NetworkCameraConnect=True
Channel.22.NetworkCameraConnect=False
SystemEvent.CPUFanError=False
SystemEvent.FrameFanError=False
"""
    result = parse_eventstatus(body)
    by_ch = {e.channel_no: e for e in result.channels}
    assert by_ch[0].connected is True
    assert by_ch[22].connected is False
    assert result.system_events["CPUFanError"] is False
    assert result.system_events["FrameFanError"] is False


def test_parse_eventstatus_cpu_fan_error_active() -> None:
    body = "SystemEvent.CPUFanError=True\nSystemEvent.FrameFanError=False\n"
    result = parse_eventstatus(body)
    assert result.system_events["CPUFanError"] is True
    assert result.system_events["FrameFanError"] is False


def test_parse_storage_percent() -> None:
    body = "UsedSpace=1000\nTotalSpace=2000\n"
    info = parse_storage(body)
    assert info.used_percent == 50.0


def test_parse_storage_temperature_kv() -> None:
    body = """
UsedSpace=1000
TotalSpace=2000
Storage.1.Temperature=42
Storage.1.Model=WD_RED
Storage.1.UsedSpace=1000
Storage.1.TotalSpace=2000
"""
    info = parse_storage(body)
    assert len(info.disks) == 1
    assert info.disks[0]["Temperature"] == "42"


def test_parse_storage_temperature_celsius_xrn() -> None:
    body = """
Storage.1.Model=HGST HUH721010AL
Storage.1.TemperatureCelsius=38
Storage.1.TemperatureFahrenheit=100
Storage.1.UsedSpace=0
Storage.1.TotalSpace=9847032
Storage.2.Model=HGST HUH721010AL
Storage.2.TemperatureCelsius=40
Storage.2.UsedSpace=9895484
Storage.2.TotalSpace=9895484
"""
    info = parse_storage(body)
    assert len(info.disks) == 2
    assert info.disks[0]["Temperature"] == "38 °C"
    assert info.disks[1]["Temperature"] == "40 °C"
    assert info.used_percent is not None
    assert info.used_percent > 0


def test_parse_storage_xrn6410_slots_without_root_totals() -> None:
    """Реальный ответ XRN-6410B2: нет корневых UsedSpace, только Storage.N.* (MB)."""
    body = """
Status=Normal
Storage.1.SlotNumber=1
Storage.1.Model=WDC WD64PURZ-85B
Storage.1.UsedSpace=5877391
Storage.1.TotalSpace=5877391
Storage.1.Status=Normal
Storage.1.TemperatureCelsius=26
Storage.2.SlotNumber=2
Storage.2.Model=WDC WD64PURZ-85B
Storage.2.UsedSpace=5925804
Storage.2.TotalSpace=5925804
Storage.2.Status=Normal
Storage.3.UsedSpace=4912900
Storage.3.TotalSpace=5925804
Storage.3.Status=Normal
"""
    info = parse_storage(body, model="XRN-6410B2")
    assert len(info.disks) == 3
    assert info.used_percent == 94.3
    assert info.used_space_mb is not None
    assert info.total_space_mb is not None
    assert info.worst_status == "Normal"


def test_parse_storage_xrn3210_partial_slots() -> None:
    """XRN-3210B2: слот 1 с разным used/total, слоты без UsedSpace — в сумму не входят."""
    body = """
Status=Normal
Storage.1.UsedSpace=4112723
Storage.1.TotalSpace=5940384
Storage.1.Status=Normal
Storage.2.TemperatureCelsius=24
Storage.2.Status=Normal
"""
    info = parse_storage(body, model="XRN-3210B2")
    assert len(info.disks) == 2
    assert info.used_percent == 69.2


def test_normalize_disk_health_temperature() -> None:
    disk = {"Storage": 1, "Health": {"TemperatureInCelsius": 59}}
    normalized = normalize_disk_record(disk)
    assert normalized["Temperature"] == "59 °C"
    assert extract_disk_temperature(normalized) == "59 °C"


def test_parse_temperature_from_smart_html() -> None:
    smart = "<pre>Temperature : 35&#8451; / 95&#8457;</pre>"
    assert parse_temperature_from_smart(smart) == "35 °C"


def test_parse_diskutility_list_json() -> None:
    body = """
{
  "Disks": [
    {"Index": 14, "Name": "ST1000VM002"},
    {"Index": 15, "Name": "WDC WD60"}
  ]
}
"""
    disks = parse_diskutility_list(body)
    assert len(disks) == 2
    assert disks[0]["Index"] == 14


def test_parse_diskutility_detail_smart() -> None:
    body = """
Disk.0.Index=14
Disk.0.Name=ST1000VM002
Disk.0.SMART=<pre>Temperature : 41&#8451;</pre>
"""
    detail = parse_diskutility_detail(body)
    assert detail["Temperature"] == "41 °C"


def test_merge_disk_temperatures_by_order() -> None:
    storage = [{"Storage": "1", "Model": "A"}]
    utility = [{"Index": 14, "Name": "X", "Temperature": "38 °C"}]
    merged = merge_disk_temperatures(storage, utility)
    assert merged[0]["Temperature"] == "38 °C"


def test_parse_recording_period_global() -> None:
    body = "StartTime=2014-09-22 16:05:34\nEndTime=2014-10-02 11:47:11\n"
    info = parse_recording_period(body)
    assert info.archive_days is not None
    assert info.archive_days > 9


def test_parse_recording_period_per_channel_kv() -> None:
    body = """
Channel.0.StartTime=2014-09-22 16:05:34
Channel.0.EndTime=2014-09-25 16:05:34
Channel.1.StartTime=2014-09-22 16:05:34
Channel.1.EndTime=2014-10-02 11:47:11
"""
    info0 = parse_recording_period(body, channel_no=0)
    info1 = parse_recording_period(body, channel_no=1)
    assert info0.archive_days is not None
    assert info1.archive_days is not None
    assert info1.archive_days > info0.archive_days


def test_merge_channels() -> None:
    a = [ChannelInfo(channel_no=0, name="A", source_state="On")]
    b = [ChannelInfo(channel_no=0, camera_ip="10.0.0.1")]
    merged = merge_channels(a, b)
    assert len(merged) == 1
    assert merged[0].name == "A"
    assert merged[0].camera_ip == "10.0.0.1"


def test_parse_cameraregister_kv_connectfail() -> None:
    body = """
Channel.0.IPAddress=10.0.0.5
Channel.0.Model=XNV-6080
Channel.0.Status=ConnectFail
Channel.0.DataRate=2.911000
Channel.1.IPAddress=10.0.0.6
Channel.1.Model=XNV-6081
Channel.1.Status=Success
"""
    channels = parse_cameraregister(body)
    by_no = {c.channel_no: c for c in channels}
    assert by_no[0].camera_ip == "10.0.0.5"
    assert by_no[0].camera_model == "XNV-6080"
    assert by_no[0].register_status == "ConnectFail"
    assert by_no[0].data_rate == 2.911
    assert by_no[1].register_status == "Success"


def test_to_float_tb_and_gb() -> None:
    assert _to_float("5.98TB") == 5.98 * 1024 * 1024
    assert _to_float("41.92TB") == 41.92 * 1024 * 1024
    assert _to_float("1000GB") == 1000 * 1024
    assert _to_float("512MB") == 512


def test_parse_storage_tb_units_percent() -> None:
    body = "UsedSpace=1.5TB\nTotalSpace=5.98TB\n"
    info = parse_storage(body)
    assert info.used_space_mb is not None
    assert info.total_space_mb is not None
    assert info.used_percent is not None
    assert 0 < info.used_percent < 100


def test_nvr_profile_old_cgi_disables_diskutility() -> None:
    device = DeviceInfo(model="HRX-1620", cgi_version="2.5.6")
    profile = NvrApiProfile.from_device(device)
    assert profile.supports_diskutility is False
    assert profile.celsius_only_temperature is True


def test_nvr_profile_new_cgi_allows_diskutility() -> None:
    device = DeviceInfo(model="XRN-6410B2", cgi_version="2.6.0")
    profile = NvrApiProfile.from_device(device)
    assert profile.supports_diskutility is True


def test_parse_storage_combined_temperature_hrx() -> None:
    body = """
Storage.1.Temperature=46°C/114°F
Storage.1.Model=WD_RED
"""
    profile = NvrApiProfile.from_device(
        DeviceInfo(model="HRX-1620", cgi_version="2.5.6")
    )
    info = parse_storage(body, model="HRX-1620", profile=profile)
    assert info.disks[0]["Temperature"] == "46 °C"


def test_format_celsius_only_temperature() -> None:
    assert format_celsius_only_temperature("46°C/114°F") == "46 °C"


def test_is_diskutility_error_response() -> None:
    body = "NG\nError Code: 600\nSubmenu Not Found\n"
    assert _is_diskutility_error(body) is True


def test_parse_sunapi_error_body_604() -> None:
    body = "NG\nError Code: 604\nError Details:\nInvalid Input Value(s)\n"
    assert parse_sunapi_error_body(body) == "604"
    assert parse_sunapi_error_body("Status=Normal\n") is None


def test_parse_recording_storage_enable_false() -> None:
    body = "Enable=False\nOverWrite=False\n"
    enable, overwrite = parse_recording_storage(body)
    assert enable is False
    assert overwrite is False


def test_parse_storage_no_disks_skips_root_status() -> None:
    body = "Status=Normal\n"
    info = parse_storage(body, model="HRX-1634")
    assert info.disks == []
    assert info.worst_status is None


def test_parse_systemlog_record_frame_drop_bracket() -> None:
    body = """
Total=3
[2026-03-16 05:08:04] [RecordFrameDrop] Recording buffer overflow
[2026-03-10 12:00:00] [Network] link up
"""
    assert (
        parse_systemlog_latest_timestamp(body, RECORD_FRAME_DROP_LOG_TYPE)
        == "2026-03-16 05:08:04"
    )


def test_parse_systemlog_record_frame_drop_colon() -> None:
    body = """
2026-03-16 05:08:04 : Recording Frame Drop
2026-03-15 23:45:33 : Login(Admin) (admin)
"""
    assert (
        parse_systemlog_latest_timestamp(body, RECORD_FRAME_DROP_LOG_TYPE)
        == "2026-03-16 05:08:04"
    )


def test_parse_systemlog_record_frame_drop_json() -> None:
    body = json.dumps(
        {
            "SystemLog": [
                {
                    "Date": "2026-03-16 05:08:04",
                    "Type": "RecordFrameDrop",
                    "Description": "Recording Frame Drop",
                },
                {
                    "Date": "2026-03-15 23:45:33",
                    "Type": "AdminLogin",
                    "Description": "Login",
                },
            ]
        }
    )
    assert (
        parse_systemlog_latest_timestamp(body, RECORD_FRAME_DROP_LOG_TYPE)
        == "2026-03-16 05:08:04"
    )


def test_normalize_disk_combined_temp_xrn_2010a() -> None:
    profile = NvrApiProfile.from_device(
        DeviceInfo(model="XRN-2010A", cgi_version="2.5.4")
    )
    disk = {"Storage": 1, "Temperature": "35°C/95°F"}
    normalized = normalize_disk_record(disk, model="XRN-2010A", profile=profile)
    assert normalized["Temperature"] == "35 °C"
    assert extract_disk_temperature(normalized, profile=profile) == "35 °C"
