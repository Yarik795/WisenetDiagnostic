from __future__ import annotations

from pathlib import Path

from ..cmdb_sync import DEFAULT_CMDB_PATH
from ..device_kinds import source_label
from ..state_store import SourceImportRow, StateStore


def sources_page_context(state: StateStore) -> dict:
    imports = state.list_source_imports(limit=50)
    latest_cmdb = state.get_latest_source_import("cmdb")
    cmdb_path = DEFAULT_CMDB_PATH
    return {
        "source_imports": imports,
        "latest_cmdb_import": latest_cmdb,
        "cmdb_path": cmdb_path,
        "cmdb_exists": cmdb_path.is_file(),
        "source_label": source_label,
    }


def format_import_filename(row: SourceImportRow) -> str:
    return row.filename or "—"
