from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..models import CheckStatus, Recorder

SortMode = Literal["name", "status"]

SEVERITY: dict[CheckStatus, int] = {
    CheckStatus.OFFLINE: 4,
    CheckStatus.UNKNOWN: 2,
    CheckStatus.ONLINE: 1,
    CheckStatus.DISABLED: 0,
}

STATUS_LABELS: dict[str, str] = {
    "online": "Доступен",
    "offline": "Недоступен",
    "unknown": "Не проверялся",
    "disabled": "Выключен",
    "checking": "Проверка…",
}


@dataclass
class ObjectGroup:
    object_name: str
    recorders: list[Recorder]
    aggregate_status: str


def effective_status(recorder: Recorder) -> str:
    if not recorder.enabled:
        return "disabled"
    if recorder.last_status is None:
        return "unknown"
    return recorder.last_status.value


def aggregate_status(recorders: list[Recorder]) -> str:
    if not recorders:
        return "unknown"
    statuses = [effective_status(r) for r in recorders]
    if all(s == "disabled" for s in statuses):
        return "disabled"
    worst = "disabled"
    worst_score = -1
    for s in statuses:
        if s == "disabled":
            continue
        score = SEVERITY.get(CheckStatus(s), 0)
        if score > worst_score:
            worst_score = score
            worst = s
    return worst if worst_score >= 0 else "unknown"


def offline_count(recorders: list[Recorder]) -> int:
    return sum(1 for r in recorders if effective_status(r) == "offline")


def group_by_object(
    recorders: list[Recorder],
    search: str = "",
    sort: SortMode = "status",
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
            aggregate_status=aggregate_status(recs),
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
    order = {"offline": 4, "checking": 3, "unknown": 2, "online": 1, "disabled": 0}
    return order.get(status, 0)
