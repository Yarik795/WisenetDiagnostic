import pytest

from app.models import Credentials, Recorder
from app.sunapi_extended import (
    RecordingPeriodInfo,
    fetch_channel_recording_periods,
)


def _period_body() -> str:
    return "StartTime=2014-09-22 16:05:34\nEndTime=2014-10-02 11:47:11\n"


@pytest.mark.asyncio
async def test_archive_poll_sample_then_global(monkeypatch) -> None:
    recorder = Recorder(
        id="nvr1",
        object_name="Obj",
        host="10.0.0.1",
        port=80,
    )
    credentials = Credentials(username="u", password="p")
    calls: list[str] = []

    async def fake_fetch(rec, creds, url, timeout):
        calls.append(url)
        return 200, _period_body(), None

    monkeypatch.setattr(
        "app.sunapi_extended._fetch",
        fake_fetch,
    )

    global_period = RecordingPeriodInfo(
        start_time="2014-09-22 16:05:34",
        end_time="2014-10-02 11:47:11",
        archive_days=10.0,
    )
    channel_nos = list(range(20))

    periods = await fetch_channel_recording_periods(
        recorder,
        credentials,
        channel_nos,
        global_period,
        detailed_archive=False,
        sample_verify_count=3,
    )

    assert len(periods) == 20
    assert len(calls) == 3
    assert all(p.archive_days is not None for p in periods.values())


@pytest.mark.asyncio
async def test_archive_poll_detailed_fetches_all(monkeypatch) -> None:
    recorder = Recorder(
        id="nvr1",
        object_name="Obj",
        host="10.0.0.1",
        port=80,
    )
    credentials = Credentials(username="u", password="p")
    calls: list[str] = []

    async def fake_fetch(rec, creds, url, timeout):
        calls.append(url)
        return 200, _period_body(), None

    monkeypatch.setattr("app.sunapi_extended._fetch", fake_fetch)

    global_period = RecordingPeriodInfo(
        start_time="2014-09-22 16:05:34",
        end_time="2014-10-02 11:47:11",
        archive_days=10.0,
    )
    channel_nos = [0, 1, 2]

    periods = await fetch_channel_recording_periods(
        recorder,
        credentials,
        channel_nos,
        global_period,
        detailed_archive=True,
    )

    assert len(periods) == 3
    assert len(calls) == 3
