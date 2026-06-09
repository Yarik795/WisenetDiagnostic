from __future__ import annotations

from ..device_kinds import ALL_DEVICE_KINDS, SYSTEM_KIND_LABELS, recorder_device_kind
from ..exclusions import excluded_ids_set
from ..models import Recorder
from ..state_store import RecorderMetricsRow, StateStore
from ..config_store import ConfigStore
from .grouping import ObjectGroup, aggregate_status, group_by_object, metrics_map_from_list
from .health_dashboard import fleet_overview_context


def kind_counts_for_recorders(recorders: list[Recorder]) -> dict[str, int]:
    counts = {kind: 0 for kind in ALL_DEVICE_KINDS}
    for rec in recorders:
        counts[recorder_device_kind(rec)] += 1
    return counts


def summary_page_context(store: ConfigStore, state: StateStore) -> dict:
    config = store.load()
    recorders = store.list_recorders()
    metrics = metrics_map_from_list(state.list_recorder_metrics())
    excluded = excluded_ids_set(config)
    settings = config.monitoring
    groups = group_by_object(
        recorders, "", "status", metrics, excluded_ids=excluded
    )
    ctx = fleet_overview_context(
        recorders, metrics, settings, excluded_ids=excluded
    )
    ctx.update(
        {
            "groups": groups,
            "metrics_map": metrics,
            "excluded_ids": excluded,
            "device_kinds": ALL_DEVICE_KINDS,
            "kind_labels": SYSTEM_KIND_LABELS,
            "kind_counts_fleet": kind_counts_for_recorders(recorders),
        }
    )
    return ctx


def object_group_kind_counts(group: ObjectGroup) -> dict[str, int]:
    return kind_counts_for_recorders(group.recorders)
