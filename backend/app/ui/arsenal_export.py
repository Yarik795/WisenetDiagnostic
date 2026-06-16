"""HTML-экспорт и email дашборда АС Арсенал."""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Any

from ..display_time import format_for_display
from ..web.templates_env import templates

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

_DOC_YES_COLOR = "#10b981"
_DOC_NO_COLOR = "#ef4444"
_DOC_DASH_COLOR = "#9ca3af"


def _slug_object_type(object_type: str) -> str:
    if not object_type:
        return "all"
    slug = re.sub(r"[^\w\-]+", "-", object_type.strip(), flags=re.UNICODE)
    return slug.strip("-") or "filtered"


def _color_for_index(idx: int) -> str:
    return _CHART_COLORS[idx % len(_CHART_COLORS)]


def _donut_arc_path(
    cx: float,
    cy: float,
    outer_r: float,
    inner_r: float,
    start_angle: float,
    end_angle: float,
) -> str:
    if end_angle - start_angle >= 2 * math.pi - 1e-6:
        end_angle = start_angle + 2 * math.pi - 1e-6
    x1o = cx + outer_r * math.cos(start_angle)
    y1o = cy + outer_r * math.sin(start_angle)
    x2o = cx + outer_r * math.cos(end_angle)
    y2o = cy + outer_r * math.sin(end_angle)
    x1i = cx + inner_r * math.cos(end_angle)
    y1i = cy + inner_r * math.sin(end_angle)
    x2i = cx + inner_r * math.cos(start_angle)
    y2i = cy + inner_r * math.sin(start_angle)
    large = 1 if end_angle - start_angle > math.pi else 0
    return (
        f"M {x1o:.2f} {y1o:.2f} A {outer_r:.2f} {outer_r:.2f} 0 {large} 1 "
        f"{x2o:.2f} {y2o:.2f} L {x1i:.2f} {y1i:.2f} A {inner_r:.2f} {inner_r:.2f} "
        f"0 {large} 0 {x2i:.2f} {y2i:.2f} Z"
    )


def render_donut_svg(
    entries: list[tuple[str, float]],
    colors: dict[str, str] | None = None,
    *,
    width: int = 360,
    height: int = 280,
    title: str = "Распределение",
) -> str:
    items = [(name, float(val)) for name, val in entries if float(val) > 0]
    if not items:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="Нет данных">'
            f'<rect width="{width}" height="{height}" fill="#f8f9fa"/>'
            f'<text x="{width // 2}" y="{height // 2}" text-anchor="middle" '
            f'font-size="14" fill="#5c6370">Нет данных</text></svg>'
        )

    cx = width * 0.38
    cy = height * 0.48
    outer_r = min(width, height) * 0.32
    inner_r = outer_r * 0.62
    total = sum(val for _, val in items)
    start = -math.pi / 2

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{title}">',
        f'<rect width="{width}" height="{height}" fill="#f8f9fa"/>',
    ]
    for idx, (name, val) in enumerate(items):
        angle = 2 * math.pi * val / total
        end = start + angle
        color = (colors or {}).get(name) or _color_for_index(idx)
        path = _donut_arc_path(cx, cy, outer_r, inner_r, start, end)
        parts.append(f'<path d="{path}" fill="{color}"/>')
        start = end

    parts.append(
        f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" font-size="11" fill="#1a1d21">'
        f"Итого</text>"
        f'<text x="{cx:.1f}" y="{cy + 14:.1f}" text-anchor="middle" font-size="10" fill="#5c6370">'
        f"{int(total)}</text>"
    )

    legend_x = width * 0.62
    legend_y = 24
    for idx, (name, val) in enumerate(items[:12]):
        color = (colors or {}).get(name) or _color_for_index(idx)
        pct = round(100.0 * val / total) if total else 0
        parts.append(
            f'<rect x="{legend_x:.1f}" y="{legend_y - 8:.1f}" width="10" height="10" fill="{color}"/>'
            f'<text x="{legend_x + 14:.1f}" y="{legend_y:.1f}" font-size="10" fill="#1a1d21">'
            f"{name} ({int(val)}, {pct}%)</text>"
        )
        legend_y += 16

    parts.append("</svg>")
    return "".join(parts)


def render_vertical_bar_svg(
    labels: list[str],
    values: list[float],
    colors: list[str] | None = None,
    *,
    width: int = 640,
    height: int = 320,
    value_suffix: str = "",
    title: str = "График",
) -> str:
    if not labels:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="Нет данных">'
            f'<rect width="{width}" height="{height}" fill="#f8f9fa"/>'
            f'<text x="{width // 2}" y="{height // 2}" text-anchor="middle" '
            f'font-size="14" fill="#5c6370">Нет данных</text></svg>'
        )

    pad_left = 48
    pad_right = 16
    pad_top = 16
    pad_bottom = 72
    chart_w = width - pad_left - pad_right
    chart_h = height - pad_top - pad_bottom
    max_val = max(values) if values else 1.0
    if max_val <= 0:
        max_val = 1.0
    bar_gap = 8
    bar_w = chart_w / max(len(labels), 1) - bar_gap

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{title}">',
        f'<rect width="{width}" height="{height}" fill="#f8f9fa"/>',
    ]

    grid_lines = 4
    for i in range(grid_lines + 1):
        y = pad_top + chart_h * i / grid_lines
        parts.append(
            f'<line x1="{pad_left}" y1="{y:.1f}" x2="{width - pad_right}" y2="{y:.1f}" '
            f'stroke="#d8dce3" stroke-width="1"/>'
        )
        val = max_val * (1 - i / grid_lines)
        label = f"{val:.0f}{value_suffix}" if value_suffix == "%" else f"{val:.0f}"
        parts.append(
            f'<text x="{pad_left - 6}" y="{y + 4:.1f}" text-anchor="end" '
            f'font-size="10" fill="#5c6370">{label}</text>'
        )

    y_bottom = pad_top + chart_h
    for idx, (label, val) in enumerate(zip(labels, values)):
        x = pad_left + idx * (chart_w / max(len(labels), 1)) + bar_gap / 2
        bar_h = chart_h * float(val) / max_val
        y_top = y_bottom - bar_h
        color = (colors[idx] if colors and idx < len(colors) else _color_for_index(idx))
        parts.append(
            f'<rect x="{x:.1f}" y="{y_top:.1f}" width="{bar_w:.1f}" '
            f'height="{max(bar_h, 0.5):.1f}" fill="{color}" rx="2"/>'
        )
        short = label if len(label) <= 14 else label[:12] + "…"
        parts.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{height - 10}" text-anchor="middle" '
            f'font-size="9" fill="#5c6370" transform="rotate(-30 {x + bar_w / 2:.1f} {height - 10})">'
            f"{short}</text>"
        )

    parts.append("</svg>")
    return "".join(parts)


def render_grouped_bar_svg(
    systems: list[str],
    yes: list[int],
    no: list[int],
    dash: list[int],
    *,
    width: int = 640,
    height: int = 320,
) -> str:
    if not systems:
        return render_vertical_bar_svg([], [], title="Документация")

    pad_left = 48
    pad_right = 16
    pad_top = 24
    pad_bottom = 56
    chart_w = width - pad_left - pad_right
    chart_h = height - pad_top - pad_bottom
    totals = [y + n + d for y, n, d in zip(yes, no, dash)]
    max_val = max(totals) if totals else 1
    if max_val <= 0:
        max_val = 1

    group_w = chart_w / max(len(systems), 1)
    bar_w = group_w / 4

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Наличие документации">',
        f'<rect width="{width}" height="{height}" fill="#f8f9fa"/>',
    ]

    y_bottom = pad_top + chart_h
    for idx, system in enumerate(systems):
        group_x = pad_left + idx * group_w + group_w * 0.15
        segments = [
            ("Да", yes[idx], _DOC_YES_COLOR),
            ("Нет", no[idx], _DOC_NO_COLOR),
            ("—", dash[idx], _DOC_DASH_COLOR),
        ]
        for seg_idx, (_name, val, color) in enumerate(segments):
            if val <= 0:
                continue
            x = group_x + seg_idx * (bar_w + 2)
            bar_h = chart_h * val / max_val
            parts.append(
                f'<rect x="{x:.1f}" y="{y_bottom - bar_h:.1f}" width="{bar_w:.1f}" '
                f'height="{max(bar_h, 0.5):.1f}" fill="{color}" rx="2"/>'
            )
        parts.append(
            f'<text x="{group_x + bar_w * 1.5:.1f}" y="{height - 12}" text-anchor="middle" '
            f'font-size="10" fill="#5c6370">{system}</text>'
        )

    legend_y = 8
    for name, color in (("Да", _DOC_YES_COLOR), ("Нет", _DOC_NO_COLOR), ("—", _DOC_DASH_COLOR)):
        lx = pad_left + {"Да": 0, "Нет": 48, "—": 96}[name]
        parts.append(
            f'<rect x="{lx}" y="{legend_y}" width="10" height="10" fill="{color}"/>'
            f'<text x="{lx + 14}" y="{legend_y + 9}" font-size="10" fill="#1a1d21">{name}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


def build_arsenal_export_context(page_ctx: dict[str, Any]) -> dict[str, Any]:
    charts = page_ctx.get("arsenal_charts") or {}
    kpi = page_ctx.get("arsenal_kpi") or {}
    object_type = page_ctx.get("arsenal_object_type") or ""
    filter_label = object_type if object_type else "Все типы"

    latest = page_ctx.get("latest_arsenal_import")
    import_info = "—"
    if latest is not None:
        imported = format_for_display(latest.imported_at, "%d.%m.%Y %H:%M") or "—"
        import_info = f"{imported} ({latest.record_count} паспортов, {latest.filename or 'файл'})"

    generated_at = format_for_display(datetime.now(timezone.utc), "%d.%m.%Y %H:%M") or "—"

    object_types = charts.get("object_types") or {}
    ot_entries = [
        (item["name"], float(item["value"]))
        for item in (object_types.get("entries") or [])
    ]
    ot_colors = object_types.get("colors") or {}

    fill = charts.get("fill_sections") or {}
    fill_labels = list(fill.get("labels") or [])
    fill_values = [float(v) for v in (fill.get("values") or [])]

    errors = charts.get("errors") or {}
    error_labels = list(errors.get("labels") or [])
    error_values = [float(v) for v in (errors.get("values") or [])]

    docs = charts.get("docs") or {}
    doc_systems = list(docs.get("systems") or [])
    doc_yes = list(docs.get("yes") or [])
    doc_no = list(docs.get("no") or [])
    doc_dash = list(docs.get("dash") or [])

    system_sections: list[dict[str, Any]] = []
    for system_type in page_ctx.get("arsenal_system_types") or []:
        sys_chart = (charts.get("systems") or {}).get(system_type) or {}
        names = list(sys_chart.get("manufacturers") or [])
        counts = [int(c) for c in (sys_chart.get("counts") or [])]
        colors_map = sys_chart.get("colors") or {}
        bar_colors = [colors_map.get(n) or _color_for_index(i) for i, n in enumerate(names)]
        total = int(sys_chart.get("total") or 0)
        table_rows = [
            {
                "name": name,
                "count": count,
                "pct": f"{round(100.0 * count / total)}%" if total else "0%",
            }
            for name, count in zip(names, counts)
        ]
        system_sections.append(
            {
                "system_type": system_type,
                "total": total,
                "bar_svg": render_vertical_bar_svg(
                    names,
                    [float(c) for c in counts],
                    bar_colors,
                    title=f"Производители {system_type}",
                ),
                "table_rows": table_rows,
            }
        )

    return {
        "title": f"Арсенал — {filter_label}",
        "filter_label": filter_label,
        "generated_at": generated_at,
        "import_info": import_info,
        "kpi": kpi,
        "object_types": {
            "donut_svg": render_donut_svg(ot_entries, ot_colors, title="Тип объекта"),
            "table_rows": [
                {
                    "name": name,
                    "count": int(val),
                    "pct": f"{round(100.0 * val / sum(v for _, v in ot_entries))}%"
                    if ot_entries and sum(v for _, v in ot_entries)
                    else "0%",
                }
                for name, val in ot_entries
            ],
        },
        "fill_sections": {
            "bar_svg": render_vertical_bar_svg(
                fill_labels,
                fill_values,
                value_suffix="%",
                title="Заполнение по разделам",
            ),
            "table_rows": [
                {"label": label, "value": f"{val:.1f}%"}
                for label, val in zip(fill_labels, fill_values)
            ],
        },
        "errors": {
            "bar_svg": render_vertical_bar_svg(
                error_labels,
                error_values,
                title="Ошибки по разделам",
            ),
            "table_rows": [
                {"label": label, "value": int(val)}
                for label, val in zip(error_labels, error_values)
            ],
        },
        "docs": {
            "bar_svg": render_grouped_bar_svg(
                doc_systems, doc_yes, doc_no, doc_dash
            ),
            "table_rows": [
                {
                    "system": system,
                    "yes": yes,
                    "no": no,
                    "dash": dash,
                }
                for system, yes, no, dash in zip(
                    doc_systems, doc_yes, doc_no, doc_dash
                )
            ],
        },
        "system_sections": system_sections,
    }


def render_arsenal_export_html(context: dict[str, Any]) -> str:
    template = templates.env.get_template("exports/arsenal_report.html")
    return template.render(export=context)


def render_arsenal_email_body(context: dict[str, Any]) -> str:
    kpi = context.get("kpi") or {}
    return (
        '<html><body style="font-family:system-ui,sans-serif;color:#1a1d21;">'
        f"<p>Отчёт <strong>АС Арсенал</strong> — {context['filter_label']}.</p>"
        f"<p>Сформирован: {context['generated_at']}<br>"
        f"Последняя загрузка: {context['import_info']}</p>"
        f"<p>Паспортов в выборке: <strong>{kpi.get('passport_count', 0)}</strong>, "
        f"среднее заполнение: <strong>{kpi.get('avg_fill_total', 0)}%</strong>.</p>"
        "<p>Полный отчёт во вложении (HTML).</p>"
        "</body></html>"
    )


def arsenal_export_filename(object_type: str = "") -> str:
    stamp = format_for_display(datetime.now(timezone.utc), "%Y%m%d-%H%M") or "export"
    slug = _slug_object_type(object_type)
    return f"wisenet-arsenal-{slug}-{stamp}.html"


def arsenal_email_subject(object_type: str = "") -> str:
    stamp = format_for_display(datetime.now(timezone.utc), "%d.%m.%Y %H:%M") or ""
    label = object_type if object_type else "Все типы"
    return f"АС Арсенал ({label}) — {stamp}"
