from app.sunapi_extended import (
    extract_disk_temperature,
    merge_channels,
    merge_disk_temperatures,
    normalize_disk_record,
    parse_cameraregister,
    parse_diskutility_detail,
    parse_diskutility_list,
    parse_eventstatus,
    parse_recording_period,
    parse_storage,
    parse_temperature_from_smart,
    parse_videosource_channels,
)
from app.sunapi_extended import ChannelInfo


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
    events = parse_eventstatus(body)
    by_ch = {e.channel_no: e for e in events}
    assert by_ch[0].video_loss is True
    assert by_ch[0].connected is False
    assert by_ch[1].video_loss is False


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
