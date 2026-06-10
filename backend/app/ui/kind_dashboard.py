from __future__ import annotations

from dataclasses import dataclass

from ..device_kinds import DeviceKind, SYSTEM_KIND_LABELS, recorder_device_kind
from ..exclusions import excluded_ids_set
from ..models import Recorder
from ..state_store import RecorderMetricsRow, StateStore
from ..config_store import ConfigStore
from .grouping import SortMode, aggregate_status, effective_status, group_by_object, metrics_map_from_list
from .health_dashboard import (
    ObjectMatrixCell,
    _status_rank,
    aggregate_fleet_status_counts,
)


@dataclass
class KindObjectRow:
    object_name: str
    device_count: int
    problem_count: int
    aggregate_status: str
    ping_cell: ObjectMatrixCell


def _ping_problem_status(status: str) -> bool:
    return status in ("warn", "error", "offline", "unknown")


def kind_device_has_problems(
    recorder: Recorder,
    metrics: RecorderMetricsRow | None,
    *,
    excluded_ids: set[str] | None = None,
) -> bool:
    if excluded_ids and recorder.id in excluded_ids:
        return False
    return _ping_problem_status(
        effective_status(recorder, metrics, excluded_ids=excluded_ids)
    )


def kind_health_percent(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    *,
    excluded_ids: set[str] | None = None,
) -> int:
    excluded = excluded_ids or set()
    monitored = [r for r in recorders if r.id not in excluded]
    if not monitored:
        return 100
    healthy = sum(
        1
        for r in monitored
        if effective_status(r, metrics_map.get(r.id), excluded_ids=excluded)
        in ("ok", "online")
    )
    return round(100 * healthy / len(monitored))


def count_kind_without_poll_data(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    *,
    excluded_ids: set[str] | None = None,
) -> int:
    excluded = excluded_ids or set()
    return sum(
        1
        for r in recorders
        if r.id not in excluded
        and effective_status(r, metrics_map.get(r.id), excluded_ids=excluded)
        == "unknown"
    )


def count_kind_problems(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    *,
    excluded_ids: set[str] | None = None,
) -> int:
    excluded = excluded_ids or set()
    return sum(
        1
        for r in recorders
        if r.id not in excluded
        and kind_device_has_problems(
            r, metrics_map.get(r.id), excluded_ids=excluded
        )
    )


def _ping_cell_for_object(
    recs: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    *,
    excluded_ids: set[str] | None = None,
) -> ObjectMatrixCell:
    excluded = excluded_ids or set()
    monitored = [r for r in recs if r.id not in excluded]
    if not monitored:
        return ObjectMatrixCell(
            column="ping",
            status="excluded",
            problem_count=0,
            title="Все устройства исключены из мониторинга",
        )
    statuses = [
        effective_status(r, metrics_map.get(r.id), excluded_ids=excluded)
        for r in monitored
    ]
    worst = max(statuses, key=_status_rank) if statuses else "unknown"
    problems = sum(1 for status in statuses if _ping_problem_status(status))
    if problems:
        title = f"Ping: {problems} из {len(monitored)} с отклонением"
    elif worst == "unknown":
        title = "Ping: нет данных опроса"
    else:
        title = "Ping: в норме"
    return ObjectMatrixCell(
        column="ping",
        status=worst,
        problem_count=problems,
        title=title,
    )


def build_kind_object_rows(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    *,
    excluded_ids: set[str] | None = None,
) -> list[KindObjectRow]:
    excluded = excluded_ids or set()
    by_object: dict[str, list[Recorder]] = {}
    for rec in recorders:
        by_object.setdefault(rec.object_name, []).append(rec)

    rows: list[KindObjectRow] = []
    for name, recs in by_object.items():
        monitored = [r for r in recs if r.id not in excluded]
        problem_count = sum(
            1
            for r in monitored
            if kind_device_has_problems(
                r, metrics_map.get(r.id), excluded_ids=excluded
            )
        )
        rows.append(
            KindObjectRow(
                object_name=name,
                device_count=len(recs),
                problem_count=problem_count,
                aggregate_status=aggregate_status(recs, metrics_map),
                ping_cell=_ping_cell_for_object(
                    recs, metrics_map, excluded_ids=excluded
                ),
            )
        )
    rows.sort(
        key=lambda row: (
            -_status_rank(row.aggregate_status),
            -row.problem_count,
            row.object_name.lower(),
        )
    )
    return rows


def kind_fleet_overview_context(
    recorders: list[Recorder],
    metrics_map: dict[str, RecorderMetricsRow],
    *,
    excluded_ids: set[str] | None = None,
    kind: DeviceKind,
) -> dict:
    excluded = excluded_ids or set()
    object_names = {r.object_name for r in recorders}
    monitored_recs = [r for r in recorders if r.id not in excluded]
    status_counts = aggregate_fleet_status_counts(
        recorders, metrics_map, excluded_ids=excluded
    )
    return {
        "fleet_object_count": len(object_names),
        "fleet_nvr_count": len(recorders),
        "fleet_enabled_count": len(monitored_recs),
        "fleet_excluded_count": status_counts.excluded,
        "fleet_problem_nvr_count": count_kind_problems(
            recorders, metrics_map, excluded_ids=excluded
        ),
        "fleet_no_data_count": count_kind_without_poll_data(
            recorders, metrics_map, excluded_ids=excluded
        ),
        "fleet_status_counts": status_counts,
        "fleet_health_percent": kind_health_percent(
            recorders, metrics_map, excluded_ids=excluded
        ),
        "fleet_count_label": f"{SYSTEM_KIND_LABELS[kind]} всего",
        "section_kind": kind,
        "section_kind_label": SYSTEM_KIND_LABELS[kind],
    }


def kind_section_page_context(
    store: ConfigStore,
    state: StateStore,
    kind: DeviceKind,
    *,
    sort: SortMode = "status",
) -> dict:
    config = store.load()
    all_recorders = store.list_recorders()
    recorders = [
        r for r in all_recorders if recorder_device_kind(r) == kind
    ]
    metrics = metrics_map_from_list(state.list_recorder_metrics())
    excluded = excluded_ids_set(config)
    groups = group_by_object(
        recorders, "", sort, metrics, excluded_ids=excluded
    )
    ctx = kind_fleet_overview_context(
        recorders, metrics, excluded_ids=excluded, kind=kind
    )
    ctx.update(
        {
            "groups": groups,
            "kind_object_rows": build_kind_object_rows(
                recorders, metrics, excluded_ids=excluded
            ),
            "metrics_map": metrics,
            "excluded_ids": excluded,
            "sort": sort,
            "visible_device_kinds": (kind,),
        }
    )
    return ctx
