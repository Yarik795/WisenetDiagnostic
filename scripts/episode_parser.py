"""
Парсинг завершённых эпизодов warn/error → ok из хронологии статусов.

Используется scripts/resolved_incidents_report.py и backend/tests/test_resolved_incidents.py.
Логика «прозрачного» статуса unknown зеркалит backend/app/state_store.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import FrozenSet, Literal, Optional, Protocol, Sequence

DEFAULT_PROBLEM_STATUSES: FrozenSet[str] = frozenset({"warn", "error"})
DEFAULT_TRANSPARENT_STATUSES: FrozenSet[str] = frozenset({"unknown"})
RECORDER_PROBLEM_STATUSES: FrozenSet[str] = frozenset({"warn", "error", "offline"})

_SEVERITY_RANK = {"warn": 1, "offline": 2, "error": 3}


class HistoryEntry(Protocol):
    status: str
    recorded_at: datetime
    reason: Optional[str]


@dataclass(frozen=True)
class ResolvedEpisode:
    severity_peak: str
    started_at: datetime
    resolved_at: datetime
    reason: Optional[str]


def _peak_severity(current: Optional[str], new: str) -> str:
    if current is None:
        return new
    return new if _SEVERITY_RANK.get(new, 0) > _SEVERITY_RANK.get(current, 0) else current


def parse_resolved_episodes(
    rows: Sequence[HistoryEntry],
    *,
    problem_statuses: FrozenSet[str] = DEFAULT_PROBLEM_STATUSES,
    transparent_statuses: FrozenSet[str] = DEFAULT_TRANSPARENT_STATUSES,
    resolved_statuses: FrozenSet[str] = frozenset({"ok"}),
) -> list[ResolvedEpisode]:
    """
    Обход хронологии слева направо. Каждый переход из эпизода проблемы в ok — один инцидент.
    unknown не прерывает эпизод (как в StateStore._problem_episode_start).
    """
    episodes: list[ResolvedEpisode] = []
    in_problem = False
    episode_start: Optional[datetime] = None
    episode_reason: Optional[str] = None
    severity_peak: Optional[str] = None

    for row in rows:
        status = row.status
        if status in problem_statuses:
            if not in_problem:
                in_problem = True
                episode_start = row.recorded_at
                episode_reason = row.reason
                severity_peak = status
            else:
                severity_peak = _peak_severity(severity_peak, status)
                if episode_reason is None and row.reason:
                    episode_reason = row.reason
        elif status in transparent_statuses:
            if in_problem:
                continue
        elif status in resolved_statuses:
            if in_problem and episode_start is not None:
                episodes.append(
                    ResolvedEpisode(
                        severity_peak=severity_peak or status,
                        started_at=episode_start,
                        resolved_at=row.recorded_at,
                        reason=episode_reason,
                    )
                )
            in_problem = False
            episode_start = None
            episode_reason = None
            severity_peak = None
        else:
            in_problem = False
            episode_start = None
            episode_reason = None
            severity_peak = None

    return episodes


def count_active_episodes(
    rows: Sequence[HistoryEntry],
    *,
    problem_statuses: FrozenSet[str] = DEFAULT_PROBLEM_STATUSES,
    transparent_statuses: FrozenSet[str] = DEFAULT_TRANSPARENT_STATUSES,
) -> int:
    """1, если последний эпизод warn/error ещё не завершён переходом в ok."""
    if not rows:
        return 0
    latest = rows[-1]
    if latest.status not in problem_statuses:
        return 0
    return 1


def filter_episodes_by_resolved_at(
    episodes: Sequence[ResolvedEpisode],
    *,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
) -> list[ResolvedEpisode]:
    result: list[ResolvedEpisode] = []
    for ep in episodes:
        if since is not None and ep.resolved_at < since:
            continue
        if until is not None and ep.resolved_at > until:
            continue
        result.append(ep)
    return result


def episode_duration_hours(ep: ResolvedEpisode) -> float:
    return max(0.0, (ep.resolved_at - ep.started_at).total_seconds() / 3600.0)


def text_matches_any_pattern(text: str, patterns: Sequence[str]) -> bool:
    """Проверка вхождения любого шаблона (без учёта регистра)."""
    if not patterns:
        return False
    haystack = text.lower()
    return any(p.lower() in haystack for p in patterns if p.strip())
