"""Тесты Dahua CGI и парсинга даты прошивки."""

from app.dahua_cgi import (
    is_dahua_vendor,
    looks_like_dahua_model,
    parse_firmware_build_date,
    parse_key_value_body,
)


def test_parse_key_value_body():
    text = "vendor=Dahua\ndeviceType=IPC-HDW1230\n"
    assert parse_key_value_body(text)["vendor"] == "Dahua"


def test_is_dahua_vendor():
    assert is_dahua_vendor("Dahua") is True
    assert is_dahua_vendor("Hikvision") is False


def test_looks_like_dahua_model():
    assert looks_like_dahua_model("IPC-HDW5831R-ZE") is True
    assert looks_like_dahua_model("QND-6070R") is False


def test_parse_firmware_build_date():
    assert parse_firmware_build_date("version=2.8,build:2020-06-05") == "2020-06"
    assert parse_firmware_build_date("no date here") is None
