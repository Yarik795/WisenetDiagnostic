from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from ..cashflow_report import (
    load_report_artifact,
    requests_file_info,
    requests_file_path,
)
from ..report_jobs import ReportJob, ReportJobManager
from ..state_store import SourceImportRow, StateStore


def format_file_size(size: int) -> str:
    if size < 1024:
        return f"{size} Б"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} КБ"
    return f"{size / (1024 * 1024):.1f} МБ"


def payments_page_context(
    state: StateStore,
    report_jobs: ReportJobManager,
) -> dict[str, Any]:
    file_info = requests_file_info()
    latest_import = state.get_latest_source_import("requests")
    report = load_report_artifact()
    if report:
        generated = parse_report_generated_at(report)
        if generated is not None:
            report = {**report, "generated_at": generated}
    active_job = report_jobs.get_active_job()
    return {
        "requests_path": requests_file_path(),
        "requests_file": file_info,
        "requests_file_size": format_file_size(file_info["size"]) if file_info else None,
        "latest_requests_import": latest_import,
        "report": report,
        "report_job": active_job,
        "job": active_job,
        "refresh_url": "/payments/partials/report",
        "refresh_target": "#payments-report-root",
        "refresh_select": "#payments-report-root",
        "format_file_size": format_file_size,
    }


def parse_report_generated_at(report: Optional[dict[str, Any]]) -> Optional[datetime]:
    if not report:
        return None
    raw = report.get("generated_at")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw))
    except ValueError:
        return None
