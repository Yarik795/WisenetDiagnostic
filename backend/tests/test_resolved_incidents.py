"""Тесты парсера устранённых эпизодов (scripts/episode_parser.py)."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from episode_parser import (  # noqa: E402
    DEFAULT_PROBLEM_STATUSES,
    DEFAULT_TRANSPARENT_STATUSES,
    RECORDER_PROBLEM_STATUSES,
    filter_episodes_by_resolved_at,
    parse_resolved_episodes,
    text_matches_any_pattern,
)


@dataclass
class Row:
    status: str
    recorded_at: datetime
    reason: str | None = None


def _t(hours: int = 0) -> datetime:
    return datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc) + timedelta(hours=hours)


def test_warn_to_ok_one_incident() -> None:
    rows = [
        Row("warn", _t(0), "тест"),
        Row("ok", _t(2)),
    ]
    eps = parse_resolved_episodes(rows)
    assert len(eps) == 1
    assert eps[0].severity_peak == "warn"
    assert eps[0].started_at == _t(0)
    assert eps[0].resolved_at == _t(2)


def test_warn_error_ok_one_incident_peak_error() -> None:
    rows = [
        Row("warn", _t(0)),
        Row("error", _t(1)),
        Row("ok", _t(3)),
    ]
    eps = parse_resolved_episodes(rows)
    assert len(eps) == 1
    assert eps[0].severity_peak == "error"


def test_warn_unknown_ok_one_incident() -> None:
    rows = [
        Row("warn", _t(0)),
        Row("unknown", _t(1)),
        Row("ok", _t(2)),
    ]
    eps = parse_resolved_episodes(rows)
    assert len(eps) == 1


def test_two_separate_incidents() -> None:
    rows = [
        Row("warn", _t(0)),
        Row("ok", _t(1)),
        Row("error", _t(5)),
        Row("ok", _t(8)),
    ]
    eps = parse_resolved_episodes(rows)
    assert len(eps) == 2
    assert eps[0].severity_peak == "warn"
    assert eps[1].severity_peak == "error"


def test_recorder_offline_resolves() -> None:
    rows = [
        Row("offline", _t(0)),
        Row("ok", _t(4)),
    ]
    eps = parse_resolved_episodes(
        rows,
        problem_statuses=RECORDER_PROBLEM_STATUSES,
    )
    assert len(eps) == 1
    assert eps[0].severity_peak == "offline"


def test_filter_by_resolved_at() -> None:
    rows = [
        Row("warn", _t(0)),
        Row("ok", _t(2)),
        Row("warn", _t(10)),
        Row("ok", _t(20)),
    ]
    eps = parse_resolved_episodes(rows)
    since = _t(15)
    filtered = filter_episodes_by_resolved_at(eps, since=since)
    assert len(filtered) == 1
    assert filtered[0].resolved_at == _t(20)

    until = _t(5)
    filtered2 = filter_episodes_by_resolved_at(eps, until=until)
    assert len(filtered2) == 1
    assert filtered2[0].resolved_at == _t(2)


def test_no_incident_without_ok() -> None:
    rows = [Row("warn", _t(0)), Row("error", _t(1))]
    assert parse_resolved_episodes(rows) == []


def test_unknown_does_not_start_episode() -> None:
    rows = [
        Row("unknown", _t(0)),
        Row("warn", _t(1)),
        Row("ok", _t(2)),
    ]
    eps = parse_resolved_episodes(
        rows,
        problem_statuses=DEFAULT_PROBLEM_STATUSES,
        transparent_statuses=DEFAULT_TRANSPARENT_STATUSES,
    )
    assert len(eps) == 1
    assert eps[0].started_at == _t(1)


def test_text_matches_any_pattern() -> None:
    assert text_matches_any_pattern("Статус регистрации: AuthFail", ["AuthFail"])
    assert text_matches_any_pattern(
        "[Канал] PoE выключен на канале 3", ["PoE выключен на канале"]
    )
    assert not text_matches_any_pattern("Потеря видео (VideoLoss)", ["AuthFail"])
