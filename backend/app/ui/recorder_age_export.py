"""HTML-экспорт отчёта «Регистраторы по времени»."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from ..config_store import ConfigStore
from ..display_time import format_for_display
from ..state_store import StateStore
from ..web.templates_env import templates
from .arsenal_export import render_vertical_bar_svg
from .equipment_timeline import (
    list_tsv_recorders_with_metrics,
    normalize_period_filter,
    recorder_age_detail_rows,
)
from .recorder_age_dashboard import recorder_age_page_context


def _grouping_label(grouping: str) -> str:
    return {
        "month": "по месяцам",
        "quarter": "по кварталам",
        "year": "по годам",
    }.get(grouping, grouping)


def build_recorder_age_export_context(
    store: ConfigStore,
    state: StateStore,
    *,
    date_from: str = "",
    date_to: str = "",
    grouping: str = "month",
    model: str = "",
) -> dict[str, Any]:
    page_ctx = recorder_age_page_context(
        store,
        state,
        date_from=date_from,
        date_to=date_to,
        grouping=grouping,
        model=model,
    )
    charts = page_ctx.get("recorder_age_charts") or {}
    distribution = charts.get("distribution") or {}
    labels = list(distribution.get("labels") or [])
    values = [float(v) for v in (distribution.get("values") or [])]
    keys = list(distribution.get("keys") or [])
    colors_map = distribution.get("colors") or {}
    bar_colors = [colors_map.get(k) or "#3b82f6" for k in keys]
    kpi = page_ctx.get("recorder_age_kpi") or {}
    grp = page_ctx.get("recorder_age_grouping") or "month"
    from_key = normalize_period_filter(date_from, grp)
    to_key = normalize_period_filter(date_to, grp)

    items = list_tsv_recorders_with_metrics(store, state)
    detail_sections: list[dict[str, Any]] = []
    for key, label, count in zip(keys, labels, values):
        rows = recorder_age_detail_rows(
            items,
            period=key,
            grouping=grp,
            from_key=from_key,
            to_key=to_key,
            model=model,
        )
        detail_sections.append(
            {
                "period_key": key,
                "period_label": label,
                "count": int(count),
                "rows": rows,
            }
        )

    filter_parts = [f"Группировка: {_grouping_label(grp)}"]
    if date_from:
        filter_parts.append(f"с {date_from}")
    if date_to:
        filter_parts.append(f"по {date_to}")
    if model:
        filter_parts.append(f"модель {model}")

    generated_at = format_for_display(datetime.now(timezone.utc), "%d.%m.%Y %H:%M") or "—"
    total = sum(values) or 1.0

    return {
        "title": "Регистраторы по времени",
        "filter_label": ", ".join(filter_parts),
        "generated_at": generated_at,
        "kpi": kpi,
        "distribution": {
            "bar_svg": render_vertical_bar_svg(
                labels,
                values,
                bar_colors,
                title="Распределение по дате производства",
            ),
            "table_rows": [
                {
                    "label": label,
                    "count": int(val),
                    "pct": f"{round(100.0 * val / total)}%",
                }
                for label, val in zip(labels, values)
            ],
        },
        "detail_sections": detail_sections,
    }


def render_recorder_age_export_html(context: dict[str, Any]) -> str:
    template = templates.env.get_template("exports/recorder_age_report.html")
    return template.render(export=context)


def recorder_age_export_filename() -> str:
    stamp = format_for_display(datetime.now(timezone.utc), "%Y%m%d-%H%M") or "export"
    return f"wisenet-recorders-age-{stamp}.html"
