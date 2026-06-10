from __future__ import annotations

from pathlib import Path

from ..cashflow_report import requests_file_info, requests_file_path
from ..cmdb_sync import DEFAULT_CMDB_PATH
from ..device_kinds import source_label
from ..state_store import SourceImportRow, StateStore
from .payments import format_file_size


def sources_page_context(state: StateStore) -> dict:
    imports = state.list_source_imports(limit=50)
    latest_cmdb = state.get_latest_source_import("cmdb")
    latest_requests = state.get_latest_source_import("requests")
    cmdb_path = DEFAULT_CMDB_PATH
    requests_info = requests_file_info()
    return {
        "source_imports": imports,
        "latest_cmdb_import": latest_cmdb,
        "latest_requests_import": latest_requests,
        "cmdb_path": cmdb_path,
        "cmdb_exists": cmdb_path.is_file(),
        "requests_path": requests_file_path(),
        "requests_exists": requests_info is not None,
        "requests_file_size": format_file_size(requests_info["size"])
        if requests_info
        else None,
        "source_label": source_label,
    }


def format_import_filename(row: SourceImportRow) -> str:
    return row.filename or "—"
