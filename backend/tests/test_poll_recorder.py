"""Тесты poll_recorder: videosource при каждом опросе, include_inventory — только архив."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.models import Credentials, Recorder
from app.sunapi_extended import poll_recorder

_DEVICEINFO = "Model=XRN-2010\nDeviceType=NVR\nCGIVersion=2.6.0"
_CAMREGISTER = (
    '{"RegisteredCameras": [{"Channel": 0, "Model": "XNV-6080", "IPAddress": "10.0.0.5"}]}'
)
_VIDEOSOURCE = "Channel.0.Channel=0\nChannel.0.State=On\nChannel.0.Name=Cam 01"


@pytest.fixture
def recorder() -> Recorder:
    return Recorder(
        id="nvr-test",
        object_name="Obj",
        host="10.0.0.1",
        port=80,
    )


@pytest.fixture
def credentials() -> Credentials:
    return Credentials(username="admin", password="secret")


def _make_fetch_side_effect(fetched_urls: list[str]):
    async def fake_fetch(
        _recorder: Recorder,
        _credentials: Credentials,
        url: str,
        timeout: float = 20.0,
    ) -> tuple[int, str, str | None]:
        fetched_urls.append(url)
        if "deviceinfo" in url:
            return 200, _DEVICEINFO, None
        if "cameraregister" in url:
            return 200, _CAMREGISTER, None
        if "videosource" in url:
            return 200, _VIDEOSOURCE, None
        if "storageinfo" in url:
            return 200, "", None
        if "eventstatus" in url:
            return 200, "Channel.0.Connected=True", None
        return 200, "", None

    return fake_fetch


@pytest.mark.asyncio
async def test_poll_recorder_fetches_videosource_when_not_inventory(
    recorder: Recorder,
    credentials: Credentials,
) -> None:
    fetched_urls: list[str] = []
    archive_mock = AsyncMock(return_value={})

    with (
        patch("app.sunapi_extended._fetch", side_effect=_make_fetch_side_effect(fetched_urls)),
        patch(
            "app.sunapi_extended.fetch_channel_recording_periods",
            archive_mock,
        ),
        patch(
            "app.sunapi_extended.enrich_storage_temperatures",
            new_callable=AsyncMock,
            return_value=[],
        ),
    ):
        result = await poll_recorder(
            recorder,
            credentials,
            include_inventory=False,
        )

    assert result.online
    assert any("videosource" in u for u in fetched_urls)
    assert result.channels
    assert result.channels[0].source_state == "On"
    archive_mock.assert_awaited_once()
    assert archive_mock.await_args.kwargs["detailed_archive"] is False


@pytest.mark.asyncio
async def test_poll_recorder_detailed_archive_when_inventory(
    recorder: Recorder,
    credentials: Credentials,
) -> None:
    fetched_urls: list[str] = []
    archive_mock = AsyncMock(return_value={})

    with (
        patch("app.sunapi_extended._fetch", side_effect=_make_fetch_side_effect(fetched_urls)),
        patch(
            "app.sunapi_extended.fetch_channel_recording_periods",
            archive_mock,
        ),
        patch(
            "app.sunapi_extended.enrich_storage_temperatures",
            new_callable=AsyncMock,
            return_value=[],
        ),
    ):
        await poll_recorder(
            recorder,
            credentials,
            include_inventory=True,
        )

    assert any("videosource" in u for u in fetched_urls)
    archive_mock.assert_awaited_once()
    assert archive_mock.await_args.kwargs["detailed_archive"] is True
