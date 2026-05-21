from __future__ import annotations

import json

import pytest

from app.models import Credentials, Recorder
from app.sunapi_extended import (
    DEFAULT_NTP_POSIX_TIMEZONE,
    EnableNtpResult,
    enable_recorder_ntp,
    format_celsius_only_temperature,
    is_sunapi_set_success,
    normalize_disk_record,
    parse_date,
)


def test_is_sunapi_set_success() -> None:
    assert is_sunapi_set_success("OK") is True
    assert is_sunapi_set_success('{"Response": "Success"}') is True
    assert is_sunapi_set_success("error") is False
    assert is_sunapi_set_success("") is False


def test_parse_date_ntp_url_list_json_array() -> None:
    body = json.dumps(
        {
            "SyncType": "NTP",
            "NTPURLList": ["10.0.0.1", "10.0.0.2"],
            "NTPStatus": "Success",
        }
    )
    info = parse_date(body)
    assert info.sync_type == "NTP"
    assert info.ntp_url_list == "10.0.0.1,10.0.0.2"


def test_format_celsius_only_temperature() -> None:
    assert format_celsius_only_temperature("35°C/95°F") == "35 °C"
    assert format_celsius_only_temperature("33\u00b0C/91\u00b0F") == "33 °C"


def test_normalize_disk_temperature_xrn_2010() -> None:
    disk = {"Temperature": "35°C/95°F"}
    out = normalize_disk_record(disk, model="XRN-2010")
    assert out["Temperature"] == "35 °C"


def test_normalize_disk_temperature_other_model_unchanged() -> None:
    disk = {"Temperature": "35°C/95°F"}
    out = normalize_disk_record(disk, model="SNB-6000")
    assert out["Temperature"] == "35°C/95°F"


@pytest.mark.asyncio
async def test_enable_recorder_ntp_success(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = Recorder(
        id="nvr-1",
        object_name="Obj",
        host="10.0.0.1",
        port=80,
    )
    credentials = Credentials(username="admin", password="secret")

    calls: list[str] = []

    async def fake_fetch(rec, creds, url, timeout=20.0):
        calls.append(url)
        if "action=set" in url:
            return 200, "OK", None
        return 200, json.dumps({"SyncType": "NTP", "NTPStatus": "Success"}), None

    monkeypatch.setattr("app.sunapi_extended._fetch", fake_fetch)

    result = await enable_recorder_ntp(recorder, credentials, "203.248.240.140")
    assert result.success is True
    assert result.date_time is not None
    assert result.date_time.sync_type == "NTP"
    assert len(calls) == 2
    set_url = calls[0]
    assert "SyncType=NTP" in set_url
    assert "NTPURLList=203.248.240.140" in set_url
    assert "POSIXTimeZone=" in set_url
    assert DEFAULT_NTP_POSIX_TIMEZONE.replace(",", "%2C") in set_url or (
        "STWT-3" in set_url
    )
    assert "NTPServerEnable=False" in set_url
    assert "DSTEnable=False" in set_url
    assert "DateFormat=YYYY-MM-DD" in set_url
    assert "TimeFormat=HMS24" in set_url
    assert "ActivateServer" not in set_url
    assert "action=view" in calls[1]


@pytest.mark.asyncio
async def test_enable_recorder_ntp_applies_manual_when_skew_high(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder = Recorder(
        id="nvr-1",
        object_name="Obj",
        host="10.0.0.1",
        port=80,
    )
    credentials = Credentials(username="admin", password="secret")
    calls: list[str] = []
    view_calls = 0

    async def fake_fetch(rec, creds, url, timeout=20.0):
        nonlocal view_calls
        calls.append(url)
        if "action=set" in url:
            return 200, "OK", None
        view_calls += 1
        if view_calls == 1:
            return (
                200,
                json.dumps(
                    {
                        "SyncType": "NTP",
                        "NTPStatus": "Success",
                        "LocalTime": "2000-01-01 00:00:00",
                        "UTCTime": "2000-01-01 00:00:00",
                    }
                ),
                None,
            )
        return (
            200,
            json.dumps(
                {
                    "SyncType": "NTP",
                    "NTPStatus": "Success",
                    "LocalTime": "2026-05-21 12:00:00",
                    "UTCTime": "2026-05-21 09:00:00",
                }
            ),
            None,
        )

    monkeypatch.setattr("app.sunapi_extended._fetch", fake_fetch)

    result = await enable_recorder_ntp(recorder, credentials, "10.34.76.201")
    assert result.success is True
    set_urls = [u for u in calls if "action=set" in u]
    assert len(set_urls) == 3
    assert "SyncType=Manual" in set_urls[1]
    assert "SyncType=NTP" in set_urls[0]
    assert "SyncType=NTP" in set_urls[2]


@pytest.mark.asyncio
async def test_enable_recorder_ntp_set_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = Recorder(
        id="nvr-1",
        object_name="Obj",
        host="10.0.0.1",
        port=80,
    )
    credentials = Credentials(username="admin", password="secret")

    async def fake_fetch(rec, creds, url, timeout=20.0):
        if "action=set" in url:
            return 200, "NG\nError Code: 603", None
        return 200, json.dumps({"SyncType": "NTP"}), None

    monkeypatch.setattr("app.sunapi_extended._fetch", fake_fetch)

    result = await enable_recorder_ntp(recorder, credentials, "10.0.0.1")
    assert result.success is False
    assert "603" in (result.error or "")


@pytest.mark.asyncio
async def test_enable_recorder_ntp_network_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder = Recorder(
        id="nvr-1",
        object_name="Obj",
        host="10.0.0.1",
        port=80,
    )
    credentials = Credentials(username="admin", password="secret")

    async def fake_fetch(rec, creds, url, timeout=20.0):
        return 0, "", "Нет соединения"

    monkeypatch.setattr("app.sunapi_extended._fetch", fake_fetch)

    result = await enable_recorder_ntp(recorder, credentials, "10.0.0.1")
    assert result == EnableNtpResult(success=False, error="Нет соединения")


@pytest.mark.asyncio
async def test_enable_recorder_ntp_not_confirmed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder = Recorder(
        id="nvr-1",
        object_name="Obj",
        host="10.0.0.1",
        port=80,
    )
    credentials = Credentials(username="admin", password="secret")

    async def fake_fetch(rec, creds, url, timeout=20.0):
        if "action=set" in url:
            return 200, "OK", None
        return 200, json.dumps({"SyncType": "Manual", "NTPStatus": "Fail"}), None

    monkeypatch.setattr("app.sunapi_extended._fetch", fake_fetch)

    result = await enable_recorder_ntp(recorder, credentials, "10.0.0.1")
    assert result.success is False
    assert "SyncType=Manual" in (result.error or "")
