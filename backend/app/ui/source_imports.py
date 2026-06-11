from __future__ import annotations

from typing import Any

from ..data_sources import SOURCES, SourceSpec, input_data_dir
from ..report_jobs import ReportJobManager
from ..state_store import SourceImportRow, StateStore


def sources_page_context(
    state: StateStore,
    report_jobs: ReportJobManager,
) -> dict[str, Any]:
    source_items = [
        _source_item_context(spec, state, report_jobs) for spec in SOURCES.values()
    ]
    imports = state.list_source_imports(limit=50)
    return {
        "input_data_path": input_data_dir(),
        "source_items": source_items,
        "source_imports": imports,
    }


def _source_item_context(
    spec: SourceSpec,
    state: StateStore,
    report_jobs: ReportJobManager,
) -> dict[str, Any]:
    latest = state.get_latest_source_import(spec.key)
    active_job = report_jobs.get_active_job(spec.key)
    return {
        "key": spec.key,
        "label": spec.label,
        "button_label": spec.button_label,
        "button_title": spec.button_title,
        "last_import": latest,
        "active_job": active_job,
    }


def format_import_filename(row: SourceImportRow) -> str:
    return row.filename or "—"
