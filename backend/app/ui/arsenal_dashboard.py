"""Контекст дашборда АС Арсенал."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any, Optional

from ..arsenal_import import DOC_COLUMNS, ERROR_SECTIONS, FILL_SECTIONS, SYSTEM_SHEETS
from ..state_store import ArsenalAnalyticsDbRow, ArsenalSystemDbRow, StateStore

_FILL_LABELS = [label for label, _ in FILL_SECTIONS]
_ERROR_LABELS = [label for label, _ in ERROR_SECTIONS]
_DOC_LABELS = [label for label, _ in DOC_COLUMNS]
_SYSTEM_TYPES = [spec.system_type for spec in SYSTEM_SHEETS]

_CHART_COLORS = [
    "#3b82f6",
    "#10b981",
    "#f59e0b",
    "#ef4444",
    "#8b5cf6",
    "#06b6d4",
    "#ec4899",
    "#84cc16",
    "#f97316",
    "#6366f1",
]

_TOP_MANUFACTURERS = 10


def _parse_json_dict(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _filter_rows(
    analytics: list[ArsenalAnalyticsDbRow],
    systems: list[ArsenalSystemDbRow],
    object_type: str,
) -> tuple[list[ArsenalAnalyticsDbRow], list[ArsenalSystemDbRow]]:
    if not object_type:
        return analytics, systems
    filtered_analytics = [row for row in analytics if row.object_type == object_type]
    filtered_systems = [row for row in systems if row.object_type == object_type]
    return filtered_analytics, filtered_systems


def _object_type_options(analytics: list[ArsenalAnalyticsDbRow]) -> list[str]:
    types = sorted({row.object_type for row in analytics if row.object_type})
    return types


def _build_kpi(analytics: list[ArsenalAnalyticsDbRow]) -> dict[str, Any]:
    count = len(analytics)
    if count == 0:
        return {
            "passport_count": 0,
            "avg_fill_total": 0.0,
            "total_errors": 0,
            "passports_with_errors": 0,
            "passports_with_errors_pct": 0.0,
            "avg_fill_project": 0.0,
            "photos_pct": 0.0,
        }

    fill_values = [row.fill_total for row in analytics]
    project_values = [row.fill_project_docs for row in analytics]
    errors = [row.errors_total for row in analytics]
    with_errors = sum(1 for value in errors if value > 0)
    with_photos = sum(
        1 for row in analytics if str(row.has_photos).strip().lower() in ("да", "yes")
    )

    return {
        "passport_count": count,
        "avg_fill_total": round(sum(fill_values) / count, 1),
        "total_errors": sum(errors),
        "passports_with_errors": with_errors,
        "passports_with_errors_pct": round(with_errors / count * 100, 1),
        "avg_fill_project": round(sum(project_values) / count, 1),
        "photos_pct": round(with_photos / count * 100, 1),
    }


def _build_object_type_chart(analytics: list[ArsenalAnalyticsDbRow]) -> dict[str, Any]:
    counter = Counter(row.object_type or "Не указан" for row in analytics)
    entries = counter.most_common()
    colors = {
        name: _CHART_COLORS[idx % len(_CHART_COLORS)]
        for idx, (name, _) in enumerate(entries)
    }
    return {
        "entries": [{"name": name, "value": value} for name, value in entries],
        "colors": colors,
    }


def _build_fill_sections_chart(analytics: list[ArsenalAnalyticsDbRow]) -> dict[str, Any]:
    if not analytics:
        return {"labels": _FILL_LABELS, "values": [0] * len(_FILL_LABELS)}

    totals = defaultdict(float)
    for row in analytics:
        sections = _parse_json_dict(row.fill_sections_json)
        for label in _FILL_LABELS:
            totals[label] += float(sections.get(label, 0))

    count = len(analytics)
    values = [round(totals[label] / count, 1) for label in _FILL_LABELS]
    return {"labels": _FILL_LABELS, "values": values}


def _build_errors_chart(analytics: list[ArsenalAnalyticsDbRow]) -> dict[str, Any]:
    totals = defaultdict(int)
    for row in analytics:
        sections = _parse_json_dict(row.errors_sections_json)
        for label in _ERROR_LABELS:
            totals[label] += int(sections.get(label, 0))

    return {
        "labels": _ERROR_LABELS,
        "values": [totals[label] for label in _ERROR_LABELS],
    }


def _normalize_doc_value(value: str) -> str:
    text = (value or "").strip().lower()
    if text in ("да", "yes"):
        return "Да"
    if text in ("нет", "no"):
        return "Нет"
    return "—"


def _build_docs_chart(analytics: list[ArsenalAnalyticsDbRow]) -> dict[str, Any]:
    yes_counts = [0] * len(_DOC_LABELS)
    no_counts = [0] * len(_DOC_LABELS)
    dash_counts = [0] * len(_DOC_LABELS)

    for row in analytics:
        docs = _parse_json_dict(row.docs_json)
        for idx, label in enumerate(_DOC_LABELS):
            bucket = _normalize_doc_value(str(docs.get(label, "-")))
            if bucket == "Да":
                yes_counts[idx] += 1
            elif bucket == "Нет":
                no_counts[idx] += 1
            else:
                dash_counts[idx] += 1

    return {
        "systems": _DOC_LABELS,
        "yes": yes_counts,
        "no": no_counts,
        "dash": dash_counts,
    }


def _top_manufacturers(counter: Counter[str]) -> tuple[list[str], list[int]]:
    items = counter.most_common()
    if len(items) <= _TOP_MANUFACTURERS:
        return [name for name, _ in items], [count for _, count in items]

    top = items[:_TOP_MANUFACTURERS]
    other_count = sum(count for _, count in items[_TOP_MANUFACTURERS:])
    names = [name for name, _ in top]
    counts = [count for _, count in top]
    if other_count:
        names.append("Прочие")
        counts.append(other_count)
    return names, counts


def _build_system_charts(
    systems: list[ArsenalSystemDbRow],
) -> dict[str, dict[str, Any]]:
    by_type: dict[str, Counter[str]] = {key: Counter() for key in _SYSTEM_TYPES}
    totals: dict[str, int] = {key: 0 for key in _SYSTEM_TYPES}

    for row in systems:
        if row.system_type not in by_type:
            continue
        manufacturer = row.manufacturer or "Не указан"
        by_type[row.system_type][manufacturer] += 1
        totals[row.system_type] += 1

    charts: dict[str, dict[str, Any]] = {}
    for system_type in _SYSTEM_TYPES:
        names, counts = _top_manufacturers(by_type[system_type])
        colors = {
            name: _CHART_COLORS[idx % len(_CHART_COLORS)]
            for idx, name in enumerate(names)
        }
        charts[system_type] = {
            "total": totals[system_type],
            "manufacturers": names,
            "counts": counts,
            "colors": colors,
        }
    return charts


def arsenal_dashboard_context(
    analytics: list[ArsenalAnalyticsDbRow],
    systems: list[ArsenalSystemDbRow],
    *,
    object_type: str = "",
) -> dict[str, Any]:
    filtered_analytics, filtered_systems = _filter_rows(analytics, systems, object_type)
    return {
        "arsenal_object_type": object_type,
        "arsenal_object_type_options": _object_type_options(analytics),
        "arsenal_kpi": _build_kpi(filtered_analytics),
        "arsenal_charts": {
            "object_types": _build_object_type_chart(
                filtered_analytics if object_type else analytics
            ),
            "fill_sections": _build_fill_sections_chart(filtered_analytics),
            "errors": _build_errors_chart(filtered_analytics),
            "docs": _build_docs_chart(filtered_analytics),
            "systems": _build_system_charts(filtered_systems),
        },
        "arsenal_has_data": bool(analytics),
        "arsenal_system_types": _SYSTEM_TYPES,
    }


def arsenal_page_context(
    state: StateStore,
    *,
    object_type: str = "",
) -> dict[str, Any]:
    analytics = state.arsenal_analytics_rows()
    systems = state.arsenal_systems_rows()
    latest_import = state.get_latest_source_import("arsenal")
    return {
        "latest_arsenal_import": latest_import,
        **arsenal_dashboard_context(
            analytics,
            systems,
            object_type=object_type,
        ),
    }
