from app.models import CheckStatus, Credentials, Recorder
from app.sunapi import build_deviceinfo_url, parse_deviceinfo_response


def test_build_deviceinfo_url_http() -> None:
    r = Recorder(
        id="1",
        object_name="A",
        host="10.0.0.1",
        port=80,
        use_https=False,
    )
    url = build_deviceinfo_url(r)
    assert url == (
        "http://10.0.0.1:80/stw-cgi/system.cgi"
        "?msubmenu=deviceinfo&action=view"
    )


def test_build_deviceinfo_url_https() -> None:
    r = Recorder(
        id="1",
        object_name="A",
        host="nvr.local",
        port=443,
        use_https=True,
    )
    url = build_deviceinfo_url(r)
    assert url.startswith("https://nvr.local:443/")


def test_parse_deviceinfo() -> None:
    body = """
Model=XND-8080R
FirmwareVersion=1.29.99
DeviceType=NVR
"""
    info = parse_deviceinfo_response(body)
    assert info.model == "XND-8080R"
    assert info.firmware_version == "1.29.99"
    assert info.device_type == "NVR"
