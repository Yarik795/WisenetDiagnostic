"""Тесты ICMP ping."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.ping_check import PingResult, _ping_host_sync, ping_host


def test_ping_host_sync_success() -> None:
    completed = MagicMock()
    completed.returncode = 0
    completed.stdout = "Reply from 10.0.0.1: bytes=32 time=12ms TTL=64"
    completed.stderr = ""
    with patch("subprocess.run", return_value=completed):
        result = _ping_host_sync("10.0.0.1", 3000)
    assert result.reachable is True
    assert result.rtt_ms == 12.0


def test_ping_host_sync_failure() -> None:
    completed = MagicMock()
    completed.returncode = 1
    completed.stdout = "Request timed out."
    completed.stderr = ""
    with patch("subprocess.run", return_value=completed):
        result = _ping_host_sync("10.0.0.1", 3000)
    assert result.reachable is False
    assert result.error


@pytest.mark.asyncio
async def test_ping_host_async_wrapper() -> None:
    with patch(
        "app.ping_check._ping_host_sync",
        return_value=PingResult(reachable=True, rtt_ms=5.0),
    ):
        result = await ping_host("10.0.0.1")
    assert result.reachable is True
    assert result.rtt_ms == 5.0
