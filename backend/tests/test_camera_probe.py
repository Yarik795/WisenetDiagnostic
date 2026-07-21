"""Тесты ONVIF парсинга и cameraregister."""

from app.onvif_deviceinfo import _extract_device_info_xml, _normalize_brand
from app.sunapi_extended import parse_cameraregister


def test_extract_device_info_xml():
    xml = """<?xml version="1.0"?>
    <Envelope>
      <Body>
        <GetDeviceInformationResponse>
          <Manufacturer>Dahua</Manufacturer>
          <Model>IPC-HFW1230</Model>
          <SerialNumber>ABC123</SerialNumber>
        </GetDeviceInformationResponse>
      </Body>
    </Envelope>"""
    info = _extract_device_info_xml(xml)
    assert info["Manufacturer"] == "Dahua"
    assert info["SerialNumber"] == "ABC123"


def test_normalize_brand():
    assert _normalize_brand("Dahua Technology") == "dahua"
    assert _normalize_brand("Hanwha Vision") == "hanwha"


def test_parse_cameraregister_user_fields():
    body = """
Channel.0.IPAddress=10.0.0.5
Channel.0.Model=IPC-HFW1230
Channel.0.UserID=camadmin
Channel.0.HTTPPort=8080
Channel.0.Protocol=ONVIF
Channel.0.Status=Success
"""
    channels = parse_cameraregister(body)
    assert len(channels) == 1
    ch = channels[0]
    assert ch.camera_ip == "10.0.0.5"
    assert ch.camera_user_id == "camadmin"
    assert ch.camera_http_port == 8080
    assert ch.camera_protocol == "ONVIF"
