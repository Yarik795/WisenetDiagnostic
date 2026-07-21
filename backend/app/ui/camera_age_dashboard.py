"""Дашборд «Камеры по времени» — распределение IP-камер по дате производства / proxy."""

from __future__ import annotations

from typing import Any, Optional

from ..camera_inventory_jobs import CameraInventoryJob
from ..config_store import ConfigStore
from ..state_store import StateStore
from .equipment_timeline import (
    PeriodGrouping,
    aggregate_cameras_by_period,
    camera_age_detail_rows,
    camera_age_kpi,
    distinct_camera_brands,
    distinct_camera_models,
    format_period_label,
    list_tsv_cameras_with_context,
    normalize_period_filter,
)


def _parse_grouping(value: str) -> PeriodGrouping:
    if value in ("month", "quarter", "year"):
        return value  # type: ignore[return-value]
    return "month"


def camera_age_page_context(
    store: ConfigStore,
    state: StateStore,
    *,
    date_from: str = "",
    date_to: str = "",
    grouping: str = "month",
    model: str = "",
    brand: str = "",
    inventory_job: Optional[CameraInventoryJob] = None,
) -> dict[str, Any]:
    grp = _parse_grouping(grouping)
    from_key = normalize_period_filter(date_from, grp)
    to_key = normalize_period_filter(date_to, grp)
    items = list_tsv_cameras_with_context(store, state)
    distribution = aggregate_cameras_by_period(
        items,
        grouping=grp,
        from_key=from_key,
        to_key=to_key,
        model=model,
        brand=brand,
    )
    kpi = camera_age_kpi(items, model=model, brand=brand)
    has_data = kpi["with_date"] > 0

    query_parts = []
    if date_from:
        query_parts.append(f"date_from={date_from}")
    if date_to:
        query_parts.append(f"date_to={date_to}")
    if grouping and grouping != "month":
        query_parts.append(f"grouping={grouping}")
    if model:
        query_parts.append(f"model={model}")
    if brand:
        query_parts.append(f"brand={brand}")
    export_query = "&".join(query_parts)

    job = inventory_job
    return {
        "camera_age_date_from": date_from,
        "camera_age_date_to": date_to,
        "camera_age_grouping": grp,
        "camera_age_model": model,
        "camera_age_brand": brand,
        "camera_age_model_options": distinct_camera_models(items),
        "camera_age_brand_options": distinct_camera_brands(items),
        "camera_age_kpi": kpi,
        "camera_age_charts": {"distribution": distribution},
        "camera_age_has_data": has_data,
        "camera_age_has_cameras": len(items) > 0,
        "camera_age_export_query": export_query,
        "camera_inventory_job": job,
        "camera_inventory_active": bool(job and job.is_active),
        "camera_inventory_percent": job.percent if job else 0,
        "camera_inventory_message": job.message if job else None,
    }


def camera_age_detail_context(
    store: ConfigStore,
    state: StateStore,
    *,
    period: str = "",
    date_from: str = "",
    date_to: str = "",
    grouping: str = "month",
    model: str = "",
    brand: str = "",
) -> dict[str, Any]:
    grp = _parse_grouping(grouping)
    from_key = normalize_period_filter(date_from, grp)
    to_key = normalize_period_filter(date_to, grp)
    items = list_tsv_cameras_with_context(store, state)
    rows = camera_age_detail_rows(
        items,
        period=period,
        grouping=grp,
        from_key=from_key,
        to_key=to_key,
        model=model,
        brand=brand,
    )
    title = (
        f"Камеры, произв. {format_period_label(period, grp)}"
        if period
        else "Камеры"
    )
    return {
        "camera_age_detail_title": title,
        "camera_age_detail_count": len(rows),
        "camera_age_detail_rows": rows,
        "camera_age_detail_period": period,
        "camera_age_date_from": date_from,
        "camera_age_date_to": date_to,
        "camera_age_grouping": grp,
        "camera_age_model": model,
        "camera_age_brand": brand,
    }
