"""HTML-экспорт и email отчёта «Инвентарь регистраторов»."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..config_store import ConfigStore
from ..display_time import format_for_display
from ..state_store import StateStore
from ..web.templates_env import templates
from .recorder_inventory import recorder_inventory_page_context


def build_recorder_inventory_export_context(
    store: ConfigStore,
    state: StateStore,
    *,
    search: str = "",
) -> dict[str, Any]:
    page_ctx = recorder_inventory_page_context(store, state, search=search)
    generated_at = format_for_display(datetime.now(timezone.utc), "%d.%m.%Y %H:%M") or "—"
    filter_label = f"Поиск: {search}" if search.strip() else "Все регистраторы"
    return {
        "title": "Инвентарь регистраторов",
        "filter_label": filter_label,
        "generated_at": generated_at,
        "kpi": page_ctx.get("recorder_inventory_kpi") or {},
        "rows": page_ctx.get("recorder_inventory_rows") or [],
    }


def render_recorder_inventory_email_body(context: dict[str, Any]) -> str:
    kpi = context.get("kpi") or {}
    return (
        '<html><body style="font-family:system-ui,sans-serif;color:#1a1d21;">'
        f"<p>Отчёт <strong>Инвентарь регистраторов</strong> — {context['filter_label']}.</p>"
        f"<p>Сформирован: {context['generated_at']}</p>"
        f"<p>Регистраторов: <strong>{kpi.get('total', 0)}</strong>, "
        f"с моделью: <strong>{kpi.get('with_model', 0)}</strong>, "
        f"с MAC: <strong>{kpi.get('with_mac', 0)}</strong>, "
        f"с серийным номером: <strong>{kpi.get('with_serial', 0)}</strong>.</p>"
        "<p>Полный отчёт во вложении (HTML).</p>"
        "</body></html>"
    )


def recorder_inventory_email_subject(search: str = "") -> str:
    stamp = format_for_display(datetime.now(timezone.utc), "%d.%m.%Y %H:%M") or ""
    label = f"поиск: {search}" if search.strip() else "все регистраторы"
    return f"Инвентарь регистраторов ({label}) — {stamp}"


def render_recorder_inventory_export_html(context: dict[str, Any]) -> str:
    template = templates.env.get_template("exports/recorder_inventory_report.html")
    return template.render(export=context)


def recorder_inventory_export_filename() -> str:
    stamp = format_for_display(datetime.now(timezone.utc), "%Y%m%d-%H%M") or "export"
    return f"wisenet-recorders-inventory-{stamp}.html"
