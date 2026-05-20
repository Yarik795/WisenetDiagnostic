from __future__ import annotations

import json

import pytest

from app.models import Credentials, Recorder
from app.sunapi_extended import (
    EnableNtpResult,
    enable_recorder_ntp,
    is_sunapi_set_success,
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
    assert "SyncType=NTP" in calls[0]
    assert "NTPURLList=203.248.240.140" in calls[0]


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
