"""HTML-экспорт отчёта «Устройства на объекте»."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..config_store import ConfigStore
from ..display_time import format_for_display
from ..state_store import StateStore
from ..web.templates_env import templates
from .site_inventory import site_devices_page_context


def build_site_devices_export_context(
    store: ConfigStore,
    state: StateStore,
    *,
    search: str = "",
) -> dict[str, Any]:
    page_ctx = site_devices_page_context(store, state, search=search)
    generated_at = format_for_display(datetime.now(timezone.utc), "%d.%m.%Y %H:%M") or "—"
    filter_label = f"Поиск: {search}" if search.strip() else "Все объекты"
    return {
        "title": "Устройства на объекте",
        "filter_label": filter_label,
        "generated_at": generated_at,
        "kpi": page_ctx.get("site_devices_kpi") or {},
        "groups": page_ctx.get("site_devices_groups") or [],
    }


def render_site_devices_export_html(context: dict[str, Any]) -> str:
    template = templates.env.get_template("exports/site_devices_report.html")
    return template.render(export=context)


def site_devices_export_filename() -> str:
    stamp = format_for_display(datetime.now(timezone.utc), "%Y%m%d-%H%M") or "export"
    return f"wisenet-site-devices-{stamp}.html"
