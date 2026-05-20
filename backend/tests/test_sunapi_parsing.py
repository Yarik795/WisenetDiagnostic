from app.sunapi_extended import (
    merge_channels,
    parse_cameraregister,
    parse_eventstatus,
    parse_storage,
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


def test_merge_channels() -> None:
    a = [ChannelInfo(channel_no=0, name="A", source_state="On")]
    b = [ChannelInfo(channel_no=0, camera_ip="10.0.0.1")]
    merged = merge_channels(a, b)
    assert len(merged) == 1
    assert merged[0].name == "A"
    assert merged[0].camera_ip == "10.0.0.1"
