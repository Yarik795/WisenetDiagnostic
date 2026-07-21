"""Отчёт «Инвентарь регистраторов»: объект, модель, MAC, серийный номер."""

from __future__ import annotations

from typing import Any

from ..config_store import ConfigStore
from ..state_store import StateStore
from .equipment_timeline import list_tsv_recorders_with_metrics


def _display_value(value: str | None) -> str:
    return (value or "").strip() or "—"


def build_recorder_inventory_rows(
    store: ConfigStore,
    state: StateStore,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in list_tsv_recorders_with_metrics(store, state):
        rec = item.recorder
        metrics = item.metrics
        rows.append(
            {
                "object_name": _display_value(rec.object_name),
                "model": _display_value(metrics.model if metrics else None),
                "mac": _display_value(rec.mac),
                "serial_number": _display_value(
                    metrics.serial_number if metrics else None
                ),
                "recorder_name": rec.name or rec.host,
                "host": rec.host,
            }
        )
    rows.sort(key=lambda r: (r["object_name"].lower(), r["recorder_name"].lower()))
    return rows


def _filter_rows(rows: list[dict[str, Any]], search: str) -> list[dict[str, Any]]:
    q = search.strip().lower()
    if not q:
        return rows
    filtered: list[dict[str, Any]] = []
    for row in rows:
        haystack = " ".join(
            str(row.get(key, "") or "")
            for key in (
                "object_name",
                "model",
                "mac",
                "serial_number",
                "recorder_name",
                "host",
            )
        ).lower()
        if q in haystack:
            filtered.append(row)
    return filtered


def _build_kpi(rows: list[dict[str, Any]]) -> dict[str, int]:
    def filled(value: str) -> bool:
        return bool(value) and value != "—"

    return {
        "total": len(rows),
        "with_model": sum(1 for row in rows if filled(row["model"])),
        "with_mac": sum(1 for row in rows if filled(row["mac"])),
        "with_serial": sum(1 for row in rows if filled(row["serial_number"])),
    }


def recorder_inventory_page_context(
    store: ConfigStore,
    state: StateStore,
    *,
    search: str = "",
) -> dict[str, Any]:
    all_rows = build_recorder_inventory_rows(store, state)
    rows = _filter_rows(all_rows, search)
    return {
        "recorder_inventory_search": search,
        "recorder_inventory_has_data": bool(all_rows),
        "recorder_inventory_rows": rows,
        "recorder_inventory_kpi": _build_kpi(rows),
    }
