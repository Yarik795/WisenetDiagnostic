"""Дашборд «Регистраторы по времени» — распределение NVR по дате производства."""

from __future__ import annotations

from typing import Any, Optional

from ..config_store import ConfigStore
from ..state_store import StateStore
from .equipment_timeline import (
    PeriodGrouping,
    aggregate_recorders_by_period,
    distinct_recorder_models,
    format_period_label,
    list_tsv_recorders_with_metrics,
    normalize_period_filter,
    recorder_age_detail_rows,
    recorder_age_kpi,
    recorder_age_missing_rows,
)


def _parse_grouping(value: str) -> PeriodGrouping:
    if value in ("month", "quarter", "year"):
        return value  # type: ignore[return-value]
    return "month"


def recorder_age_page_context(
    store: ConfigStore,
    state: StateStore,
    *,
    date_from: str = "",
    date_to: str = "",
    grouping: str = "month",
    model: str = "",
) -> dict[str, Any]:
    grp = _parse_grouping(grouping)
    from_key = normalize_period_filter(date_from, grp)
    to_key = normalize_period_filter(date_to, grp)
    items = list_tsv_recorders_with_metrics(store, state)
    distribution = aggregate_recorders_by_period(
        items,
        grouping=grp,
        from_key=from_key,
        to_key=to_key,
        model=model,
    )
    kpi = recorder_age_kpi(items, model=model)
    model_options = distinct_recorder_models(items)
    has_data = kpi["total_recorders"] > 0
    has_distribution = kpi["with_date"] > 0

    query_parts = []
    if date_from:
        query_parts.append(f"date_from={date_from}")
    if date_to:
        query_parts.append(f"date_to={date_to}")
    if grouping and grouping != "month":
        query_parts.append(f"grouping={grouping}")
    if model:
        query_parts.append(f"model={model}")
    export_query = "&".join(query_parts)

    return {
        "recorder_age_date_from": date_from,
        "recorder_age_date_to": date_to,
        "recorder_age_grouping": grp,
        "recorder_age_model": model,
        "recorder_age_model_options": model_options,
        "recorder_age_kpi": kpi,
        "recorder_age_charts": {"distribution": distribution},
        "recorder_age_has_data": has_data,
        "recorder_age_has_distribution": has_distribution,
        "recorder_age_export_query": export_query,
    }


def recorder_age_detail_context(
    store: ConfigStore,
    state: StateStore,
    *,
    period: str = "",
    date_from: str = "",
    date_to: str = "",
    grouping: str = "month",
    model: str = "",
    missing: bool = False,
) -> dict[str, Any]:
    grp = _parse_grouping(grouping)
    from_key = normalize_period_filter(date_from, grp)
    to_key = normalize_period_filter(date_to, grp)
    items = list_tsv_recorders_with_metrics(store, state)
    if missing:
        rows = recorder_age_missing_rows(items, model=model)
        title = "Регистраторы без даты производства"
    else:
        rows = recorder_age_detail_rows(
            items,
            period=period,
            grouping=grp,
            from_key=from_key,
            to_key=to_key,
            model=model,
        )
        title = (
            f"Регистраторы, произв. {format_period_label(period, grp)}"
            if period
            else "Регистраторы"
        )
    return {
        "recorder_age_detail_title": title,
        "recorder_age_detail_count": len(rows),
        "recorder_age_detail_rows": rows,
        "recorder_age_detail_missing": missing,
        "recorder_age_detail_period": period,
        "recorder_age_date_from": date_from,
        "recorder_age_date_to": date_to,
        "recorder_age_grouping": grp,
        "recorder_age_model": model,
    }
