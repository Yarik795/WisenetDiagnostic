"""ICMP ping для проверки доступности устройств СКУД и биотерминалов."""

from __future__ import annotations

import asyncio
import platform
import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PingResult:
    reachable: bool
    error: Optional[str] = None
    rtt_ms: Optional[float] = None


def _ping_command(host: str, timeout_ms: int) -> list[str]:
    system = platform.system().lower()
    if system == "windows":
        return ["ping", "-n", "1", "-w", str(timeout_ms), host]
    timeout_sec = max(1, (timeout_ms + 999) // 1000)
    return ["ping", "-c", "1", "-W", str(timeout_sec), host]


def _parse_rtt_ms(stdout: str) -> Optional[float]:
    match = re.search(r"(?:time[=<]\s*|time=)(\d+(?:\.\d+)?)\s*ms", stdout, re.I)
    if match:
        return float(match.group(1))
    match = re.search(r"(\d+)\s*ms", stdout)
    if match:
        return float(match.group(1))
    return None


def _ping_host_sync(host: str, timeout_ms: int) -> PingResult:
    import subprocess

    cmd = _ping_command(host, timeout_ms)
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=(timeout_ms / 1000.0) + 2.0,
        )
    except subprocess.TimeoutExpired:
        return PingResult(reachable=False, error="таймаут ping")
    except OSError as exc:
        return PingResult(reachable=False, error=str(exc))

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    combined = f"{stdout}\n{stderr}"
    if completed.returncode == 0:
        return PingResult(reachable=True, rtt_ms=_parse_rtt_ms(combined))
    detail = (stderr or stdout).strip().splitlines()
    message = detail[-1] if detail else f"ping exit code {completed.returncode}"
    return PingResult(reachable=False, error=message)


async def ping_host(host: str, *, timeout_ms: int = 3000) -> PingResult:
    return await asyncio.to_thread(_ping_host_sync, host, timeout_ms)
