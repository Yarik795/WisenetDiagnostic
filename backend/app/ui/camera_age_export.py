"""HTML-экспорт и email отчёта «Камеры по времени»."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..camera_manufacturer_lookup import camera_brand_label
from ..config_store import ConfigStore
from ..display_time import format_for_display
from ..state_store import StateStore
from ..web.templates_env import templates
from .arsenal_export import render_vertical_bar_svg
from .camera_age_dashboard import camera_age_page_context
from .equipment_timeline import (
    camera_age_detail_rows,
    camera_age_missing_rows,
    list_tsv_cameras_with_context,
    normalize_period_filter,
)


def _grouping_label(grouping: str) -> str:
    return {
        "month": "по месяцам",
        "quarter": "по кварталам",
        "year": "по годам",
    }.get(grouping, grouping)


def _brand_label(brand: str) -> str:
    return camera_brand_label(brand)


def build_camera_age_export_context(
    store: ConfigStore,
    state: StateStore,
    *,
    date_from: str = "",
    date_to: str = "",
    grouping: str = "month",
    model: str = "",
    brand: str = "",
) -> dict[str, Any]:
    page_ctx = camera_age_page_context(
        store,
        state,
        date_from=date_from,
        date_to=date_to,
        grouping=grouping,
        model=model,
        brand=brand,
    )
    charts = page_ctx.get("camera_age_charts") or {}
    distribution = charts.get("distribution") or {}
    manufacturers = charts.get("manufacturers") or {}
    labels = list(distribution.get("labels") or [])
    values = [float(v) for v in (distribution.get("values") or [])]
    keys = list(distribution.get("keys") or [])
    colors_map = distribution.get("colors") or {}
    bar_colors = [colors_map.get(k) or "#3b82f6" for k in keys]
    kpi = page_ctx.get("camera_age_kpi") or {}
    grp = page_ctx.get("camera_age_grouping") or "month"
    from_key = normalize_period_filter(date_from, grp)
    to_key = normalize_period_filter(date_to, grp)

    items = list_tsv_cameras_with_context(store, state)
    detail_sections: list[dict[str, Any]] = []
    for key, label, count in zip(keys, labels, values):
        rows = camera_age_detail_rows(
            items,
            period=key,
            grouping=grp,
            from_key=from_key,
            to_key=to_key,
            model=model,
            brand=brand,
        )
        detail_sections.append(
            {
                "period_key": key,
                "period_label": label,
                "count": int(count),
                "rows": rows,
            }
        )

    missing_rows = camera_age_missing_rows(items, model=model, brand=brand)

    filter_parts = [f"Группировка: {_grouping_label(grp)}"]
    if date_from:
        filter_parts.append(f"с {date_from}")
    if date_to:
        filter_parts.append(f"по {date_to}")
    if model:
        filter_parts.append(f"модель {model}")
    if brand:
        filter_parts.append(f"бренд {_brand_label(brand)}")

    generated_at = format_for_display(datetime.now(timezone.utc), "%d.%m.%Y %H:%M") or "—"
    total = sum(values) or 1.0
    mfr_labels = list(manufacturers.get("labels") or [])
    mfr_values = [float(v) for v in (manufacturers.get("values") or [])]
    mfr_keys = list(manufacturers.get("keys") or [])
    mfr_colors_map = manufacturers.get("colors") or {}
    mfr_bar_colors = [mfr_colors_map.get(k) or "#3b82f6" for k in mfr_keys]
    mfr_total = sum(mfr_values) or 1.0

    return {
        "title": "Камеры по времени",
        "subtitle": (
            "Для Dahua дата — proxy по сборке прошивки (build); "
            "для Hanwha/Samsung — декод серийного номера."
        ),
        "filter_label": ", ".join(filter_parts),
        "generated_at": generated_at,
        "kpi": kpi,
        "manufacturers": {
            "bar_svg": render_vertical_bar_svg(
                mfr_labels,
                mfr_values,
                mfr_bar_colors,
                title="Камеры по производителям",
            )
            if mfr_labels
            else "",
            "table_rows": [
                {
                    "label": label,
                    "count": int(val),
                    "pct": f"{round(100.0 * val / mfr_total)}%",
                }
                for label, val in zip(mfr_labels, mfr_values)
            ],
        },
        "distribution": {
            "bar_svg": render_vertical_bar_svg(
                labels,
                values,
                bar_colors,
                title="Распределение камер по дате",
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
            "title": "Камеры без даты производства",
            "count": len(missing_rows),
            "rows": missing_rows,
        }
        if missing_rows
        else None,
    }


def render_camera_age_export_html(context: dict[str, Any]) -> str:
    template = templates.env.get_template("exports/camera_age_report.html")
    return template.render(export=context)


def camera_age_export_filename() -> str:
    stamp = format_for_display(datetime.now(timezone.utc), "%Y%m%d-%H%M") or "export"
    return f"wisenet-cameras-age-{stamp}.html"


def render_camera_age_email_body(context: dict[str, Any]) -> str:
    kpi = context.get("kpi") or {}
    return (
        '<html><body style="font-family:system-ui,sans-serif;color:#1a1d21;">'
        f"<p>Отчёт <strong>Камеры по времени</strong> — {context['filter_label']}.</p>"
        f"<p>{context.get('subtitle', '')}</p>"
        f"<p>Сформирован: {context['generated_at']}</p>"
        f"<p>Камер: <strong>{kpi.get('total_cameras', 0)}</strong>, "
        f"с датой: <strong>{kpi.get('with_date', 0)}</strong>, "
        f"Dahua: <strong>{kpi.get('dahua_count', 0)}</strong>.</p>"
        "<p>Полный отчёт во вложении (HTML).</p>"
        "</body></html>"
    )


def camera_age_email_subject(
    *,
    date_from: str = "",
    date_to: str = "",
    brand: str = "",
) -> str:
    stamp = format_for_display(datetime.now(timezone.utc), "%d.%m.%Y %H:%M") or ""
    parts = []
    if date_from or date_to:
        parts.append(f"{date_from or '…'}–{date_to or '…'}")
    if brand:
        parts.append(_brand_label(brand))
    label = ", ".join(parts) if parts else "все камеры"
    return f"Камеры по времени ({label}) — {stamp}"
