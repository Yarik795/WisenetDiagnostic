from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from ..device_kinds import ALL_DEVICE_KINDS, DeviceKind, recorder_device_kind
from ..health import HEALTH_SEVERITY, HealthStatus, worst_status
from ..models import Recorder
from ..state_store import RecorderMetricsRow

SortMode = Literal["name", "status"]

STATUS_LABELS: dict[str, str] = {
    "online": "Доступен",
    "offline": "Недоступен",
    "unknown": "Не проверялся",
    "disabled": "Выключен",
    "excluded": "Исключён",
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
    devices_by_kind: dict[str, list[Recorder]] = field(default_factory=dict)
    total_device_count: int = 0


def build_devices_by_kind(recorders: list[Recorder]) -> dict[str, list[Recorder]]:
    by_kind: dict[str, list[Recorder]] = {kind: [] for kind in ALL_DEVICE_KINDS}
    for rec in recorders:
        kind: DeviceKind = recorder_device_kind(rec)
        by_kind[kind].append(rec)
    return by_kind


def effective_status(
    recorder: Recorder,
    metrics: RecorderMetricsRow | None = None,
    *,
    excluded_ids: set[str] | None = None,
) -> str:
    if excluded_ids is not None and recorder.id in excluded_ids:
        return "excluded"
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
    *,
    excluded_ids: set[str] | None = None,
) -> str:
    if not recorders:
        return "unknown"
    metrics_map = metrics_map or {}
    excluded = excluded_ids or set()
    statuses = [
        effective_status(r, metrics_map.get(r.id), excluded_ids=excluded)
        for r in recorders
    ]
    if all(s in ("disabled", "excluded") for s in statuses):
        return "excluded" if all(s == "excluded" for s in statuses) else "disabled"
    active = [s for s in statuses if s not in ("disabled", "excluded")]
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
    *,
    excluded_ids: set[str] | None = None,
) -> list[ObjectGroup]:
    excluded = excluded_ids or set()
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

    groups = []
    for name, recs in groups_map.items():
        by_kind = build_devices_by_kind(recs)
        groups.append(
            ObjectGroup(
                object_name=name,
                recorders=recs,
                aggregate_status=aggregate_status(
                    recs, metrics_map, excluded_ids=excluded
                ),
                devices_by_kind=by_kind,
                total_device_count=len(recs),
            )
        )

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
        "excluded": 0,
    }
    return order.get(status, 0)


def metrics_map_from_list(rows: list[RecorderMetricsRow]) -> dict[str, RecorderMetricsRow]:
    return {r.recorder_id: r for r in rows}
