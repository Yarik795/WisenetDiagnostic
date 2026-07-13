"""Контекст страницы «Анализ повторных РВР»."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional
from urllib.parse import urlencode

from ..rvr_repeat_report import (
    OBJECT_TYPE_ADZ,
    OBJECT_TYPE_VSP,
    build_rvr_repeat_report,
    format_kind_cell,
)
from ..state_store import StateStore

OBJECT_TYPE_OPTIONS = (OBJECT_TYPE_VSP, OBJECT_TYPE_ADZ)


def _quarter_bounds(year: int, quarter: int) -> tuple[date, date]:
    start_month = (quarter - 1) * 3 + 1
    start = date(year, start_month, 1)
    if quarter == 4:
        end = date(year, 12, 31)
    else:
        end = date(year, start_month + 3, 1) - timedelta(days=1)
    return start, end


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    if month == 12:
        end = date(year, 12, 31)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return start, end


def _current_quarter_bounds(today: date) -> tuple[date, date]:
    quarter = (today.month - 1) // 3 + 1
    return _quarter_bounds(today.year, quarter)


def _previous_quarter_bounds(today: date) -> tuple[date, date]:
    quarter = (today.month - 1) // 3 + 1
    if quarter == 1:
        return _quarter_bounds(today.year - 1, 4)
    return _quarter_bounds(today.year, quarter - 1)


def period_presets(today: Optional[date] = None) -> list[dict[str, str]]:
    today = today or datetime.now(timezone.utc).date()
    cq_start, cq_end = _current_quarter_bounds(today)
    pq_start, pq_end = _previous_quarter_bounds(today)
    cm_start, cm_end = _month_bounds(today.year, today.month)
    if today.month == 1:
        pm_start, pm_end = _month_bounds(today.year - 1, 12)
    else:
        pm_start, pm_end = _month_bounds(today.year, today.month - 1)
    return [
        {
            "key": "current_quarter",
            "label": "Текущий квартал",
            "from": cq_start.isoformat(),
            "to": cq_end.isoformat(),
        },
        {
            "key": "previous_quarter",
            "label": "Прошлый квартал",
            "from": pq_start.isoformat(),
            "to": pq_end.isoformat(),
        },
        {
            "key": "current_month",
            "label": "Текущий месяц",
            "from": cm_start.isoformat(),
            "to": cm_end.isoformat(),
        },
        {
            "key": "previous_month",
            "label": "Прошлый месяц",
            "from": pm_start.isoformat(),
            "to": pm_end.isoformat(),
        },
    ]


def parse_period_dates(
    date_from: Optional[str],
    date_to: Optional[str],
    *,
    today: Optional[date] = None,
) -> tuple[date, date]:
    today = today or datetime.now(timezone.utc).date()
    default_from, default_to = _current_quarter_bounds(today)

    def _parse_one(value: Optional[str], fallback: date) -> date:
        if not value:
            return fallback
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            return fallback

    d_from = _parse_one(date_from, default_from)
    d_to = _parse_one(date_to, default_to)
    if d_from > d_to:
        d_from, d_to = d_to, d_from
    return d_from, d_to


def _datetime_bounds(date_from: date, date_to: date) -> tuple[datetime, datetime]:
    start = datetime(
        date_from.year, date_from.month, date_from.day, tzinfo=timezone.utc
    )
    end_exclusive = datetime(
        date_to.year, date_to.month, date_to.day, tzinfo=timezone.utc
    ) + timedelta(days=1)
    return start, end_exclusive


def normalize_object_type_filter(value: Optional[str]) -> str:
    if value in OBJECT_TYPE_OPTIONS:
        return value
    return ""


def filter_report_by_object_type(
    report: dict[str, Any], object_type: str
) -> dict[str, Any]:
    if object_type not in OBJECT_TYPE_OPTIONS:
        return report

    groups_ge2 = [
        group for group in report.get("groups_ge2", []) if group["object_type"] == object_type
    ]
    groups_ge3 = [
        group for group in report.get("groups_ge3", []) if group["object_type"] == object_type
    ]
    data_rows = [
        row for row in report.get("data_rows", []) if row.get("object_type") == object_type
    ]
    repeats_total = sum(group["repeat_count"] for group in groups_ge2)
    top_object = ""
    if groups_ge2:
        top = groups_ge2[0]
        top_object = f"{top['address']} ({top['object_type']})"

    filtered = dict(report)
    filtered["groups_ge2"] = groups_ge2
    filtered["groups_ge3"] = groups_ge3
    filtered["data_rows"] = data_rows
    filtered["kpi"] = {
        "groups_total": len(groups_ge2),
        "repeats_total": repeats_total,
        "top_object": top_object,
        "requests_total": len(data_rows),
    }
    filtered["has_data"] = bool(data_rows)
    return filtered


def build_rvr_repeat_query_string(
    *,
    date_from: str,
    date_to: str,
    threshold: int,
    object_type: str = "",
) -> str:
    params: dict[str, str | int] = {
        "from": date_from,
        "to": date_to,
        "threshold": threshold,
    }
    if object_type:
        params["object_type"] = object_type
    return urlencode(params)


def _prepare_table_groups(
    groups: list[dict[str, Any]], kinds: list[str]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in groups:
        cells: dict[str, str] = {}
        by_kind = group.get("by_kind") or {}
        for kind in kinds:
            cells[kind] = format_kind_cell(by_kind.get(kind, []))
        rows.append(
            {
                "address": group["address"],
                "object_type": group["object_type"],
                "repeat_count": group["repeat_count"],
                "cells": cells,
                "analysis": group.get("analysis"),
            }
        )
    return rows


def rvr_repeat_page_context(
    state: StateStore,
    *,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    threshold: int = 2,
    object_type: Optional[str] = None,
) -> dict[str, Any]:
    d_from, d_to = parse_period_dates(date_from, date_to)
    if threshold not in (2, 3):
        threshold = 2
    object_type_filter = normalize_object_type_filter(object_type)
    date_from_iso = d_from.isoformat()
    date_to_iso = d_to.isoformat()
    query_string = build_rvr_repeat_query_string(
        date_from=date_from_iso,
        date_to=date_to_iso,
        threshold=threshold,
        object_type=object_type_filter,
    )

    pp_count = state.count_pp_requests()
    latest_import = state.get_latest_source_import("requests")
    latest_naumen = state.get_latest_source_import("naumen")

    base_ctx = {
        "rvr_pp_count": pp_count,
        "rvr_date_from": date_from_iso,
        "rvr_date_to": date_to_iso,
        "rvr_threshold": threshold,
        "rvr_object_type": object_type_filter,
        "rvr_object_type_options": OBJECT_TYPE_OPTIONS,
        "rvr_period_presets": period_presets(),
        "rvr_latest_import": latest_import,
        "rvr_latest_naumen_import": latest_naumen,
        "rvr_query_string": query_string,
        "rvr_export_url": f"/rvr-repeat/export.xlsx?{query_string}",
    }

    if pp_count == 0:
        return {
            **base_ctx,
            "rvr_has_data": False,
            "rvr_report": None,
            "rvr_kpi": None,
            "rvr_table_groups": [],
            "rvr_kinds": [],
            "rvr_empty_message": (
                "Данные заявок ещё не загружены. Загрузите файл с «заявки» в названии "
                "на странице «Исходные данные»."
            ),
        }

    created_start, created_end = _datetime_bounds(d_from, d_to)
    rows = state.pp_requests_rows(
        created_from=created_start,
        created_to=created_end,
    )
    desc_map = state.naumen_description_by_sberdrug()
    report = build_rvr_repeat_report(rows, desc_map, date_from=d_from, date_to=d_to)
    report = filter_report_by_object_type(report, object_type_filter)

    groups = report["groups_ge3"] if threshold == 3 else report["groups_ge2"]
    kinds = report.get("kinds") or []
    has_groups = bool(groups)

    empty_message = ""
    if not report.get("has_data"):
        empty_message = (
            "За выбранный период нет заявок РВР, удовлетворяющих фильтрам отчёта."
        )
    elif not has_groups:
        empty_message = (
            "Нет групп с повторами для выбранного типа объекта и порога."
        )

    return {
        **base_ctx,
        "rvr_has_data": report.get("has_data", False) and has_groups,
        "rvr_report": report,
        "rvr_kpi": report.get("kpi"),
        "rvr_table_groups": _prepare_table_groups(groups, kinds),
        "rvr_kinds": kinds,
        "rvr_empty_message": empty_message,
        "rvr_filters_text": report.get("filters_text", ""),
    }
