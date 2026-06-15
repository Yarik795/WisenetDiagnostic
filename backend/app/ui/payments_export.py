from __future__ import annotations

import math
from typing import Any, Literal

from ..cashflow_report import SECTION_SPECS, format_amount_rub
from ..display_time import format_for_display
from ..web.templates_env import templates

PaymentsMetric = Literal["amount", "count"]

_KIND_LABELS = {
    "modern": "Модернизация",
    "rvr": "РВР",
}

_METRIC_LABELS = {
    "amount": "Сумма",
    "count": "Количество заявок",
}

_APPROVED_COLOR = "#34d399"
_DEFAULT_PARTY_COLOR = "#6b7280"


def _metric_for_section(metrics: dict[str, str] | None, section_key: str) -> PaymentsMetric:
    raw = (metrics or {}).get(section_key, "amount")
    return "count" if raw == "count" else "amount"


def _select_metric_view(
    series: dict[str, Any],
    metric: PaymentsMetric,
) -> dict[str, Any]:
    if metric == "count":
        matrix = series.get("count_matrix") or {}
        party_totals = series.get("count_totals") or {}
        approved_values = (series.get("approved") or {}).get("count") or []
    else:
        matrix = series.get("matrix") or {}
        party_totals = series.get("party_totals") or {}
        approved_values = (series.get("approved") or {}).get("amount") or []
    return {
        "months": list(series.get("months") or []),
        "parties": list(series.get("parties") or []),
        "matrix": matrix,
        "party_totals": party_totals,
        "approved": list(approved_values),
        "colors": dict(series.get("colors") or {}),
    }


def _format_metric_value(value: float, metric: PaymentsMetric) -> str:
    if metric == "count":
        n = int(round(value))
        mod10 = n % 10
        mod100 = n % 100
        word = "заявок"
        if mod100 < 11 or mod100 > 14:
            if mod10 == 1:
                word = "заявка"
            elif 2 <= mod10 <= 4:
                word = "заявки"
        return f"{n} {word}"
    return format_amount_rub(value)


def _party_color(colors: dict[str, str], party: str) -> str:
    return colors.get(party) or _DEFAULT_PARTY_COLOR


def render_payments_bar_svg(
    series: dict[str, Any],
    metric: PaymentsMetric,
    *,
    width: int = 640,
    height: int = 260,
) -> str:
    view = _select_metric_view(series, metric)
    months = view["months"]
    parties = view["parties"]
    matrix = view["matrix"]
    approved = view["approved"]
    colors = view["colors"]

    if not months:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="Нет данных">'
            f'<rect width="{width}" height="{height}" fill="#f8f9fa"/>'
            f'<text x="{width // 2}" y="{height // 2}" text-anchor="middle" '
            f'font-size="14" fill="#5c6370">Нет данных</text></svg>'
        )

    pad_left = 48
    pad_right = 16
    pad_top = 24
    pad_bottom = 56
    chart_w = width - pad_left - pad_right
    chart_h = height - pad_top - pad_bottom
    bar_gap = 12
    bar_w = chart_w / max(len(months), 1) - bar_gap

    totals: list[float] = []
    for idx, _month in enumerate(months):
        total = sum(float((matrix.get(party) or [0])[idx] or 0) for party in parties)
        if idx < len(approved):
            total += float(approved[idx] or 0)
        totals.append(total)
    max_total = max(totals) if totals else 1.0
    if max_total <= 0:
        max_total = 1.0

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="График по месяцам">',
        f'<rect width="{width}" height="{height}" fill="#f8f9fa"/>',
    ]

    grid_lines = 4
    for i in range(grid_lines + 1):
        y = pad_top + chart_h * i / grid_lines
        parts.append(
            f'<line x1="{pad_left}" y1="{y:.1f}" x2="{width - pad_right}" y2="{y:.1f}" '
            f'stroke="#d8dce3" stroke-width="1"/>'
        )
        val = max_total * (1 - i / grid_lines)
        parts.append(
            f'<text x="{pad_left - 6}" y="{y + 4:.1f}" text-anchor="end" '
            f'font-size="10" fill="#5c6370">{_format_metric_value(val, metric)}</text>'
        )

    for idx, month in enumerate(months):
        x = pad_left + idx * (chart_w / max(len(months), 1)) + bar_gap / 2
        y_bottom = pad_top + chart_h
        stack_bottom = y_bottom
        segments: list[tuple[str, float, str]] = []
        for party in parties:
            val = float((matrix.get(party) or [0])[idx] or 0)
            if val > 0:
                segments.append((party, val, _party_color(colors, party)))
        if idx < len(approved):
            appr_val = float(approved[idx] or 0)
            if appr_val > 0:
                segments.append(
                    ("Согласовано", appr_val, colors.get("Согласовано", _APPROVED_COLOR))
                )
        for _name, val, color in segments:
            seg_h = chart_h * val / max_total
            y_top = stack_bottom - seg_h
            parts.append(
                f'<rect x="{x:.1f}" y="{y_top:.1f}" width="{bar_w:.1f}" '
                f'height="{max(seg_h, 0.5):.1f}" fill="{color}" rx="2"/>'
            )
            stack_bottom = y_top
        parts.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{height - 12}" text-anchor="middle" '
            f'font-size="10" fill="#5c6370" transform="rotate(-25 {x + bar_w / 2:.1f} {height - 12})">'
            f"{month}</text>"
        )

    legend_x = pad_left
    legend_y = 10
    for name, color in [(p, _party_color(colors, p)) for p in parties]:
        if legend_x > width - 80:
            legend_x = pad_left
            legend_y += 14
        parts.append(
            f'<rect x="{legend_x}" y="{legend_y - 8}" width="10" height="10" fill="{color}"/>'
            f'<text x="{legend_x + 14}" y="{legend_y}" font-size="10" fill="#1a1d21">{name}</text>'
        )
        legend_x += 14 + len(name) * 6 + 16
    if any(v > 0 for v in approved):
        parts.append(
            f'<rect x="{legend_x}" y="{legend_y - 8}" width="10" height="10" '
            f'fill="{colors.get("Согласовано", _APPROVED_COLOR)}"/>'
            f'<text x="{legend_x + 14}" y="{legend_y}" font-size="10" fill="#1a1d21">Согласовано</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


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


def render_payments_donut_svg(
    series: dict[str, Any],
    metric: PaymentsMetric,
    *,
    width: int = 320,
    height: int = 260,
) -> str:
    view = _select_metric_view(series, metric)
    parties = view["parties"]
    party_totals = view["party_totals"]
    colors = view["colors"]
    entries = [
        (party, float(party_totals.get(party) or 0))
        for party in parties
        if float(party_totals.get(party) or 0) > 0
    ]

    if not entries:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="Нет данных">'
            f'<rect width="{width}" height="{height}" fill="#f8f9fa"/>'
            f'<text x="{width // 2}" y="{height // 2}" text-anchor="middle" '
            f'font-size="14" fill="#5c6370">Нет данных</text></svg>'
        )

    cx = width * 0.38
    cy = height * 0.5
    outer_r = min(width, height) * 0.32
    inner_r = outer_r * 0.62
    total = sum(val for _, val in entries)
    start = -math.pi / 2

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Распределение по сторонам">',
        f'<rect width="{width}" height="{height}" fill="#f8f9fa"/>',
    ]
    for party, val in entries:
        angle = 2 * math.pi * val / total
        end = start + angle
        path = _donut_arc_path(cx, cy, outer_r, inner_r, start, end)
        parts.append(f'<path d="{path}" fill="{_party_color(colors, party)}"/>')
        start = end

    parts.append(
        f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" font-size="11" fill="#1a1d21">'
        f"Итого</text>"
        f'<text x="{cx:.1f}" y="{cy + 14:.1f}" text-anchor="middle" font-size="10" fill="#5c6370">'
        f"{_format_metric_value(total, metric)}</text>"
    )

    legend_y = 24
    for party, val in entries:
        pct = 100.0 * val / total if total else 0
        parts.append(
            f'<rect x="{width * 0.62:.0f}" y="{legend_y - 9}" width="10" height="10" '
            f'fill="{_party_color(colors, party)}"/>'
            f'<text x="{width * 0.62 + 14:.0f}" y="{legend_y}" font-size="10" fill="#1a1d21">'
            f"{party}: {_format_metric_value(val, metric)} ({pct:.1f}%)</text>"
        )
        legend_y += 16

    parts.append("</svg>")
    return "".join(parts)


def build_payments_export_context(
    report: dict[str, Any],
    kind: str,
    metrics: dict[str, str] | None = None,
) -> dict[str, Any]:
    reports = report.get("reports") or {}
    kind_report = reports.get(kind)
    if not isinstance(kind_report, dict):
        raise ValueError(f"Неизвестный вид отчёта: {kind}")

    generated_raw = report.get("generated_at")
    generated_at = "—"
    if generated_raw:
        try:
            from datetime import datetime

            generated_at = (
                format_for_display(datetime.fromisoformat(str(generated_raw)), "%d.%m.%Y %H:%M")
                or str(generated_raw)
            )
        except ValueError:
            generated_at = str(generated_raw)

    sections_out: list[dict[str, Any]] = []
    for key, default_title in SECTION_SPECS:
        section = next(
            (s for s in (kind_report.get("sections") or []) if s.get("key") == key),
            None,
        )
        if not isinstance(section, dict):
            continue
        metric = _metric_for_section(metrics, key)
        series = section.get("series") or {}
        party_totals = _select_metric_view(series, metric)["party_totals"]
        party_totals_fmt = [
            {
                "party": party,
                "value": _format_metric_value(float(party_totals.get(party) or 0), metric),
            }
            for party in (series.get("parties") or [])
            if float(party_totals.get(party) or 0) > 0
        ]
        sections_out.append(
            {
                "key": key,
                "title": section.get("title") or default_title,
                "kpi": section.get("kpi") or {},
                "bar_svg": render_payments_bar_svg(series, metric),
                "donut_svg": render_payments_donut_svg(series, metric),
                "party_totals_fmt": party_totals_fmt,
                "rows": section.get("rows") or [],
                "metric": metric,
                "metric_label": _METRIC_LABELS[metric],
            }
        )

    return {
        "title": kind_report.get("title") or _KIND_LABELS.get(kind, kind),
        "kind": kind,
        "kind_label": _KIND_LABELS.get(kind, kind),
        "generated_at": generated_at,
        "source_file": report.get("source_file") or "—",
        "sections": sections_out,
    }


def render_payments_export_html(context: dict[str, Any]) -> str:
    template = templates.env.get_template("exports/payments_report.html")
    return template.render(export=context)


def payments_export_filename(kind: str) -> str:
    from datetime import datetime, timezone

    stamp = format_for_display(datetime.now(timezone.utc), "%Y%m%d-%H%M") or "export"
    return f"wisenet-payments-{kind}-{stamp}.html"


def payments_email_subject(kind: str) -> str:
    from datetime import datetime, timezone

    stamp = format_for_display(datetime.now(timezone.utc), "%d.%m.%Y %H:%M") or ""
    label = _KIND_LABELS.get(kind, kind)
    return f"Статус оплаты ({label}) — {stamp}"


def render_payments_email_body(context: dict[str, Any]) -> str:
    total_requests = sum(int((s.get("kpi") or {}).get("total_count") or 0) for s in context["sections"])
    return (
        "<html><body style=\"font-family:system-ui,sans-serif;color:#1a1d21;\">"
        f"<p>Отчёт «Статус оплаты» — <strong>{context['kind_label']}</strong>.</p>"
        f"<p>Сформирован: {context['generated_at']}<br>"
        f"Исходный файл: {context['source_file']}</p>"
        f"<p>Заявок в работе (суммарно по разделам): <strong>{total_requests}</strong></p>"
        "<p>Полный отчёт во вложении (HTML).</p>"
        "</body></html>"
    )
