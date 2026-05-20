from __future__ import annotations

from enum import Enum


class HealthStatus(str, Enum):
    OK = "ok"
    WARN = "warn"
    ERROR = "error"
    UNKNOWN = "unknown"


HEALTH_LABELS: dict[str, str] = {
    "ok": "Исправно",
    "warn": "Деградация",
    "error": "Неисправно",
    "unknown": "Неизвестно",
}

HEALTH_SEVERITY: dict[HealthStatus, int] = {
    HealthStatus.ERROR: 4,
    HealthStatus.WARN: 3,
    HealthStatus.UNKNOWN: 2,
    HealthStatus.OK: 1,
}


def worst_status(*statuses: str) -> str:
    best = "unknown"
    best_score = -1
    for s in statuses:
        if not s:
            continue
        try:
            score = HEALTH_SEVERITY[HealthStatus(s)]
        except ValueError:
            score = HEALTH_SEVERITY[HealthStatus.UNKNOWN]
        if score > best_score:
            best_score = score
            best = s
    return best if best_score >= 0 else "unknown"
