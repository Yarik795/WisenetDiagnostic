"""Дашборд «Диски по времени» — распределение HDD по наработке (PowerOnDuration)."""

from __future__ import annotations

from typing import Any, Optional

from ..config_store import ConfigStore
from ..state_store import StateStore
from .equipment_timeline import (
    BucketYears,
    aggregate_disks_by_wear,
    disk_wear_detail_rows,
    disk_wear_kpi,
    distinct_disk_models,
    explode_disk_rows,
    format_wear_bucket_label,
    list_tsv_recorders_with_metrics,
)


def _parse_bucket(value: str) -> BucketYears:
    if value in ("0.5", "1", "2"):
        return value  # type: ignore[return-value]
    return "1"


def _parse_float(value: str) -> Optional[float]:
    value = (value or "").strip().replace(",", ".")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def disk_wear_page_context(
    store: ConfigStore,
    state: StateStore,
    *,
    bucket: str = "1",
    min_years: str = "",
    max_years: str = "",
    model: str = "",
) -> dict[str, Any]:
    bucket_val = _parse_bucket(bucket)
    min_val = _parse_float(min_years)
    max_val = _parse_float(max_years)
    items = list_tsv_recorders_with_metrics(store, state)
    disks = explode_disk_rows(items)
    distribution = aggregate_disks_by_wear(
        disks,
        bucket=bucket_val,
        min_years=min_val,
        max_years=max_val,
        model=model,
    )
    kpi = disk_wear_kpi(items, disks, model=model)
    model_options = distinct_disk_models(disks)
    has_data = kpi["with_wear"] > 0

    query_parts = []
    if bucket and bucket != "1":
        query_parts.append(f"bucket={bucket}")
    if min_years:
        query_parts.append(f"min_years={min_years}")
    if max_years:
        query_parts.append(f"max_years={max_years}")
    if model:
        query_parts.append(f"model={model}")
    export_query = "&".join(query_parts)

    return {
        "disk_wear_bucket": bucket_val,
        "disk_wear_min_years": min_years,
        "disk_wear_max_years": max_years,
        "disk_wear_model": model,
        "disk_wear_model_options": model_options,
        "disk_wear_kpi": kpi,
        "disk_wear_charts": {"distribution": distribution},
        "disk_wear_has_data": has_data,
        "disk_wear_export_query": export_query,
    }


def disk_wear_detail_context(
    store: ConfigStore,
    state: StateStore,
    *,
    bucket_key: str = "",
    bucket: str = "1",
    min_years: str = "",
    max_years: str = "",
    model: str = "",
) -> dict[str, Any]:
    bucket_val = _parse_bucket(bucket)
    min_val = _parse_float(min_years)
    max_val = _parse_float(max_years)
    items = list_tsv_recorders_with_metrics(store, state)
    disks = explode_disk_rows(items)
    rows = disk_wear_detail_rows(
        disks,
        bucket_key=bucket_key,
        bucket=bucket_val,
        min_years=min_val,
        max_years=max_val,
        model=model,
    )
    title = (
        f"Диски, наработка {format_wear_bucket_label(bucket_key)}"
        if bucket_key
        else "Диски"
    )
    return {
        "disk_wear_detail_title": title,
        "disk_wear_detail_count": len(rows),
        "disk_wear_detail_rows": rows,
        "disk_wear_detail_bucket_key": bucket_key,
        "disk_wear_bucket": bucket_val,
        "disk_wear_min_years": min_years,
        "disk_wear_max_years": max_years,
        "disk_wear_model": model,
    }
