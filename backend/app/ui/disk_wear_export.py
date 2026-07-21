"""HTML-экспорт отчёта «Диски по времени»."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..config_store import ConfigStore
from ..display_time import format_for_display
from ..state_store import StateStore
from ..web.templates_env import templates
from .arsenal_export import render_vertical_bar_svg
from .disk_wear_dashboard import disk_wear_page_context
from .equipment_timeline import (
    disk_wear_detail_rows,
    disk_wear_missing_rows,
    explode_disk_rows,
    list_tsv_recorders_with_metrics,
)


def _bucket_label(bucket: str) -> str:
    return {"0.5": "0,5 года", "1": "1 год", "2": "2 года"}.get(bucket, bucket)


def build_disk_wear_export_context(
    store: ConfigStore,
    state: StateStore,
    *,
    bucket: str = "1",
    min_years: str = "",
    max_years: str = "",
    model: str = "",
) -> dict[str, Any]:
    page_ctx = disk_wear_page_context(
        store,
        state,
        bucket=bucket,
        min_years=min_years,
        max_years=max_years,
        model=model,
    )
    charts = page_ctx.get("disk_wear_charts") or {}
    distribution = charts.get("distribution") or {}
    labels = list(distribution.get("labels") or [])
    values = [float(v) for v in (distribution.get("values") or [])]
    keys = list(distribution.get("keys") or [])
    colors_map = distribution.get("colors") or {}
    bar_colors = [colors_map.get(k) or "#3b82f6" for k in keys]
    kpi = page_ctx.get("disk_wear_kpi") or {}
    bucket_val = page_ctx.get("disk_wear_bucket") or "1"

    items = list_tsv_recorders_with_metrics(store, state)
    disks = explode_disk_rows(items)
    min_val = None
    max_val = None
    if min_years.strip():
        try:
            min_val = float(min_years.replace(",", "."))
        except ValueError:
            pass
    if max_years.strip():
        try:
            max_val = float(max_years.replace(",", "."))
        except ValueError:
            pass

    detail_sections: list[dict[str, Any]] = []
    for key, label, count in zip(keys, labels, values):
        rows = disk_wear_detail_rows(
            disks,
            bucket_key=key,
            bucket=bucket_val,
            min_years=min_val,
            max_years=max_val,
            model=model,
        )
        detail_sections.append(
            {
                "bucket_key": key,
                "bucket_label": label,
                "count": int(count),
                "rows": rows,
            }
        )

    missing_rows = disk_wear_missing_rows(items, model=model)

    filter_parts = [f"Интервал: {_bucket_label(bucket_val)}"]
    if min_years:
        filter_parts.append(f"от {min_years} лет")
    if max_years:
        filter_parts.append(f"до {max_years} лет")
    if model:
        filter_parts.append(f"модель {model}")

    generated_at = format_for_display(datetime.now(timezone.utc), "%d.%m.%Y %H:%M") or "—"
    total = sum(values) or 1.0

    return {
        "title": "Диски по времени",
        "filter_label": ", ".join(filter_parts),
        "generated_at": generated_at,
        "kpi": kpi,
        "distribution": {
            "bar_svg": render_vertical_bar_svg(
                labels,
                values,
                bar_colors,
                title="Распределение по наработке",
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
        "missing_section": {
            "title": "Диски без наработки",
            "count": len(missing_rows),
            "rows": missing_rows,
        }
        if missing_rows
        else None,
    }


def render_disk_wear_export_html(context: dict[str, Any]) -> str:
    template = templates.env.get_template("exports/disk_wear_report.html")
    return template.render(export=context)


def disk_wear_export_filename() -> str:
    stamp = format_for_display(datetime.now(timezone.utc), "%Y%m%d-%H%M") or "export"
    return f"wisenet-disks-wear-{stamp}.html"
