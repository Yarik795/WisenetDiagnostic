from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..health import HEALTH_SEVERITY, HealthStatus, worst_status
from ..models import Recorder
from ..state_store import RecorderMetricsRow

SortMode = Literal["name", "status"]

STATUS_LABELS: dict[str, str] = {
    "online": "Доступен",
    "offline": "Недоступен",
    "unknown": "Не проверялся",
    "disabled": "Выключен",
    "checking": "Проверка…",
    "ok": "Исправно",
    "warn": "Деградация",
    "error": "Неисправно",
}


@dataclass
class ObjectGroup:
    object_name: str
    recorders: list[Recorder]
    aggregate_status: str


def effective_status(
    recorder: Recorder,
    metrics: RecorderMetricsRow | None = None,
) -> str:
    if not recorder.enabled:
        return "disabled"
    if metrics and metrics.last_polled_at:
        return metrics.health_status
    if recorder.last_status is None:
        return "unknown"
    legacy = recorder.last_status.value
    if legacy == "online":
        return "ok"
    if legacy == "offline":
        return "error"
    return legacy


def aggregate_status(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow] | None = None,
) -> str:
    if not recorders:
        return "unknown"
    metrics_map = metrics_map or {}
    statuses = [
        effective_status(r, metrics_map.get(r.id)) for r in recorders
    ]
    if all(s == "disabled" for s in statuses):
        return "disabled"
    active = [s for s in statuses if s != "disabled"]
    return worst_status(*active) if active else "unknown"


def problem_count(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow] | None = None,
) -> int:
    metrics_map = metrics_map or {}
    return sum(
        1
        for r in recorders
        if effective_status(r, metrics_map.get(r.id))
        in ("offline", "error", "warn")
    )


def group_by_object(
    recorders: list[Recorder],
    search: str = "",
    sort: SortMode = "status",
    metrics_map: dict[str, RecorderMetricsRow] | None = None,
) -> list[ObjectGroup]:
    q = search.strip().lower()
    filtered = recorders
    if q:
        filtered = [
            r
            for r in recorders
            if q in r.object_name.lower()
            or q in r.host.lower()
            or q in (r.name or "").lower()
        ]

    groups_map: dict[str, list[Recorder]] = {}
    for r in filtered:
        groups_map.setdefault(r.object_name, []).append(r)

    groups = [
        ObjectGroup(
            object_name=name,
            recorders=recs,
            aggregate_status=aggregate_status(recs, metrics_map),
        )
        for name, recs in groups_map.items()
    ]

    if sort == "name":
        groups.sort(key=lambda g: g.object_name.lower())
    else:
        groups.sort(
            key=lambda g: (
                -_status_sort_key(g.aggregate_status),
                g.object_name.lower(),
            )
        )

    return groups


def _status_sort_key(status: str) -> int:
    try:
        return HEALTH_SEVERITY[HealthStatus(status)]
    except ValueError:
        pass
    order = {
        "error": 5,
        "offline": 5,
        "warn": 4,
        "checking": 3,
        "unknown": 2,
        "ok": 1,
        "online": 1,
        "disabled": 0,
    }
    return order.get(status, 0)


def metrics_map_from_list(rows: list[RecorderMetricsRow]) -> dict[str, RecorderMetricsRow]:
    return {r.recorder_id: r for r in rows}
