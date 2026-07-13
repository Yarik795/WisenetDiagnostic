from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Literal, Optional
from urllib.parse import parse_qs, urlencode, urlparse

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from pydantic import ValidationError

from ..config_store import ConfigStore
from ..data_sources import RunnerDeps, get_source_spec, load_source
from ..exclusions import excluded_ids_set, is_excluded
from ..display_time import format_for_display
from ..logging_config import get_log_file_path, get_logger
from ..models import RecorderCreate, RecorderUpdate
from ..monitoring import poll_single_recorder, run_ntp_fix_all
from ..cashflow_report import (
    SECTION_SPECS,
    find_latest_requests_source_file,
    import_requests_from_source,
    load_report_artifact,
    requests_file_path,
)
from ..poll_jobs import PollJob, PollJobManager
from ..report_jobs import ReportJob, ReportJobManager
from ..scheduler import MonitoringScheduler
from ..sunapi_extended import enable_recorder_ntp
from ..state_store import StateStore
from ..ui.dependencies import (
    get_monitoring_scheduler,
    get_poll_job_manager,
    get_report_job_manager,
    get_state_store,
    get_store,
)
from ..ui.grouping import (
    SortMode,
    effective_status,
    group_by_object,
    metrics_map_from_list,
    problem_count,
)
from ..ui.helpers import display_recorder_name
from ..ui.metrics_helpers import format_skew, sync_type_label
from ..ui.health_classifiers import CATEGORY_LABELS, HealthCategory
from ..ui.error_report import build_error_report_context
from ..ui.error_report_render import render_error_report_html
from ..ui.health_dashboard import health_dashboard_context
from ..device_kinds import filter_recorders_by_kind
from ..ui.kind_dashboard import kind_section_page_context
from ..ui.summary_dashboard import summary_page_context
from ..ui.payments import payments_page_context
from ..ui.payments_export import (
    build_payments_export_context,
    payments_email_subject_combined,
    payments_export_filename,
    render_payments_email_body_combined,
    render_payments_export_html,
)
from ..ui.source_imports import sources_page_context
from ..ui.arsenal_dashboard import (
    arsenal_detail_context,
    arsenal_page_context,
    arsenal_passport_context,
)
from ..ui.arsenal_export import (
    arsenal_email_subject,
    arsenal_export_filename,
    build_arsenal_export_context,
    render_arsenal_email_body,
    render_arsenal_export_html,
)
from ..ui.rvr_repeat_dashboard import rvr_repeat_page_context
from ..ui.rvr_repeat_export import (
    XLSX_MIME,
    build_rvr_repeat_xlsx,
    render_rvr_repeat_email_body,
    rvr_repeat_email_subject,
    rvr_repeat_export_filename,
)
from ..ui.time_dashboard import time_dashboard_context
from .templates_env import templates
from .validation import parse_recorder_form

router = APIRouter(tags=["web"])
check_logger = get_logger("check")


def _redirect(
    url: str,
    toast_type: str | None = None,
    message: str | None = None,
    *,
    request: Request | None = None,
) -> Response:
    redirect_url = url
    if toast_type and message:
        qs = urlencode({"toast": toast_type, "msg": message})
        redirect_url = f"{url}?{qs}"

    headers: dict[str, str] = {"HX-Redirect": redirect_url}
    if toast_type and message:
        headers["HX-Trigger"] = json.dumps(
            {"showToast": {"type": toast_type, "message": message}},
            ensure_ascii=True,
        )

    if request is not None and request.headers.get("HX-Request") == "true":
        return Response(status_code=200, headers=headers)

    response = RedirectResponse(url=redirect_url, status_code=303)
    for key, value in headers.items():
        response.headers[key] = value
    return response


def _object_names(store: ConfigStore) -> list[str]:
    return sorted({r.object_name for r in store.list_recorders()})


def _excluded_ids(store: ConfigStore) -> set[str]:
    return excluded_ids_set(store.load())


def _metrics_map(state: StateStore):
    return metrics_map_from_list(state.list_recorder_metrics())


def _inventory_kpi_ctx(
    store: ConfigStore,
    state: StateStore,
    *,
    kind: str | None = "tsv",
) -> dict:
    from ..ui.health_dashboard import fleet_overview_context

    config = store.load()
    recorders = filter_recorders_by_kind(store.list_recorders(), kind)  # type: ignore[arg-type]
    metrics = _metrics_map(state)
    settings = config.monitoring
    excluded = excluded_ids_set(config)
    ctx = fleet_overview_context(
        recorders,
        metrics,
        settings,
        excluded_ids=excluded,
        include_kind_columns=False,
    )
    ctx["inventory_problem_nvr_count"] = ctx["fleet_problem_nvr_count"]
    ctx["inventory_enabled_count"] = ctx["fleet_enabled_count"]
    ctx["inventory_category_counts"] = ctx["fleet_category_counts"]
    return ctx


def _referer_has_table_view(referer: str) -> bool:
    parsed = urlparse(referer or "")
    return parse_qs(parsed.query).get("view", [""])[0] == "table"


def _time_dashboard_ctx(
    store: ConfigStore,
    state: StateStore,
    *,
    compact: bool = False,
    search: str = "",
    problems_only: bool = True,
    show_all_table: bool = False,
    refresh_url: str = "/monitoring/partials/time-dashboard",
) -> dict:
    config = store.load()
    recorders = store.list_recorders()
    metrics = _metrics_map(state)
    ctx = time_dashboard_context(
        recorders,
        metrics,
        config.monitoring,
        ntp_server=config.monitoring.ntp_server or "",
        compact=compact,
        problems_only=problems_only,
        search=search,
        show_all_table=show_all_table,
        excluded_ids=excluded_ids_set(config),
    )
    ctx["time_refresh_url"] = refresh_url
    ctx["time_server_now"] = format_for_display(
        datetime.now(timezone.utc), "%Y-%m-%d %H:%M:%S"
    )
    ctx["time_show_actions"] = False
    return ctx


def _wants_time_dashboard_response(request: Request) -> bool:
    target = request.headers.get("HX-Target", "")
    referer = request.headers.get("HX-Current-URL", "")
    parsed = urlparse(referer or "")
    status_time = (
        ("/status" in parsed.path or "/monitoring" in parsed.path)
        and parse_qs(parsed.query).get("category", [""])[0] == "time"
    )
    return "#time-dashboard" in target or status_time or (
        "/time" in referer and "#health-dashboard" not in target
    )


def _health_dashboard_ctx(
    store: ConfigStore,
    state: StateStore,
    *,
    compact: bool = False,
    search: str = "",
    problems_only: bool = True,
    highlight_category: Optional[HealthCategory] = None,
    refresh_url: str = "/monitoring/partials/health-dashboard",
) -> dict:
    config = store.load()
    recorders = filter_recorders_by_kind(store.list_recorders(), "tsv")  # type: ignore[arg-type]
    metrics = _metrics_map(state)
    ctx = health_dashboard_context(
        recorders,
        metrics,
        config.monitoring,
        ntp_server=config.monitoring.ntp_server or "",
        compact=compact,
        problems_only=problems_only,
        search=search,
        highlight_category=highlight_category,
        excluded_ids=excluded_ids_set(config),
    )
    ctx["health_refresh_url"] = refresh_url
    ctx["health_server_now"] = format_for_display(
        datetime.now(timezone.utc), "%Y-%m-%d %H:%M:%S"
    )
    return ctx


def _health_dashboard_response(
    request: Request,
    store: ConfigStore,
    state: StateStore,
    *,
    toast_type: str | None = None,
    toast_message: str | None = None,
    compact: bool = False,
    search: str = "",
    problems_only: bool = True,
    highlight_category: Optional[HealthCategory] = None,
    refresh_url: str = "/monitoring/partials/health-dashboard",
    status_code: int = 200,
) -> HTMLResponse:
    ctx = _health_dashboard_ctx(
        store,
        state,
        compact=compact,
        search=search,
        problems_only=problems_only,
        highlight_category=highlight_category,
        refresh_url=refresh_url,
    )
    response = templates.TemplateResponse(
        request,
        "partials/health_dashboard_stack.html",
        ctx,
        status_code=status_code,
    )
    if toast_type and toast_message:
        return _attach_toast(response, toast_type, toast_message)
    return response


def _wants_health_dashboard_response(request: Request) -> bool:
    target = request.headers.get("HX-Target", "")
    referer = request.headers.get("HX-Current-URL", "")
    return (
        "#health-dashboard-stack" in target
        or "#health-dashboard" in target
        or "/status" in referer
        or "/monitoring" in referer
    )


def _health_params_from_referer(referer: str) -> dict:
    parsed = urlparse(referer or "")
    qs = parse_qs(parsed.query)
    search = qs.get("search", [""])[0]
    problems_only = qs.get("problems_only", ["true"])[0].lower() not in (
        "false",
        "0",
        "no",
    )
    category_raw = qs.get("category", [""])[0].strip()
    highlight_category: Optional[HealthCategory] = None
    if category_raw in CATEGORY_LABELS:
        highlight_category = category_raw  # type: ignore[assignment]
    compact = False
    if "/status" in parsed.path or (
        "/monitoring" in parsed.path
        and parse_qs(parsed.query).get("tab", [""])[0] == "health"
    ):
        enc_parts = {
            "search": search,
            "problems_only": "true" if problems_only else "false",
        }
        if highlight_category:
            enc_parts["category"] = highlight_category
        refresh_url = f"/monitoring/partials/health-dashboard?{urlencode(enc_parts)}"
    else:
        refresh_url = "/monitoring/partials/health-dashboard"
    return {
        "compact": compact,
        "search": search,
        "problems_only": problems_only,
        "highlight_category": highlight_category,
        "refresh_url": refresh_url,
    }


def _time_params_from_referer(referer: str) -> dict:
    parsed = urlparse(referer or "")
    qs = parse_qs(parsed.query)
    search = qs.get("search", [""])[0]
    problems_only = qs.get("problems_only", ["true"])[0].lower() not in (
        "false",
        "0",
        "no",
    )
    compact = False
    if "/time" in parsed.path or (
        ("/status" in parsed.path or "/monitoring" in parsed.path)
        and parse_qs(parsed.query).get("category", [""])[0] == "time"
    ):
        enc = urlencode(
            {
                "search": search,
                "problems_only": "true" if problems_only else "false",
            }
        )
        if "/status" in parsed.path or "/monitoring" in parsed.path:
            enc_status = {
                "search": search,
                "problems_only": "true" if problems_only else "false",
                "category": "time",
            }
            refresh_url = f"/monitoring/partials/health-dashboard?{urlencode(enc_status)}"
        else:
            refresh_url = f"/time/partials/dashboard?{enc}"
        show_all = not problems_only
    else:
        refresh_url = "/monitoring/partials/time-dashboard"
        show_all = False
    return {
        "compact": compact,
        "search": search,
        "problems_only": problems_only,
        "show_all_table": show_all,
        "refresh_url": refresh_url,
    }


def _time_dashboard_response(
    request: Request,
    store: ConfigStore,
    state: StateStore,
    *,
    toast_type: str | None = None,
    toast_message: str | None = None,
    compact: bool = False,
    search: str = "",
    problems_only: bool = True,
    show_all_table: bool = False,
    refresh_url: str = "/monitoring/partials/time-dashboard",
    status_code: int = 200,
) -> HTMLResponse:
    ctx = _time_dashboard_ctx(
        store,
        state,
        compact=compact,
        search=search,
        problems_only=problems_only,
        show_all_table=show_all_table,
        refresh_url=refresh_url,
    )
    response = templates.TemplateResponse(
        request,
        "partials/time_dashboard.html",
        ctx,
        status_code=status_code,
    )
    if toast_type and toast_message:
        return _attach_toast(response, toast_type, toast_message)
    return response


def _recorder_partial_template(referer: str) -> str:
    parsed = urlparse(referer or "")
    if _referer_has_table_view(referer) or (
        "/recorders" in parsed.path and "/monitoring" not in parsed.path
    ):
        return "partials/recorder_table_row.html"
    return "partials/recorder_row.html"


def _recorder_partial_context(
    recorder,
    metrics,
    *,
    template: str,
    metrics_map: dict | None = None,
    excluded_ids: set[str] | None = None,
) -> dict:
    excluded = excluded_ids or set()
    status = effective_status(recorder, metrics, excluded_ids=excluded)
    ctx: dict = {
        "recorder": recorder,
        "status": status,
        "metrics": metrics,
        "excluded_ids": excluded,
        "is_excluded": recorder.id in excluded,
    }
    if template == "partials/recorder_table_row.html":
        ctx["metrics_map"] = metrics_map or {recorder.id: metrics}
    return ctx


def _attach_toast(response: HTMLResponse, toast_type: str, message: str) -> HTMLResponse:
    payload = {"showToast": {"type": toast_type, "message": message}}
    response.headers["HX-Trigger"] = json.dumps(payload, ensure_ascii=True)
    return response


def _recorders_by_id(store: ConfigStore) -> dict[str, object]:
    return {r.id: r for r in store.list_recorders()}


@router.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/summary", status_code=302)


@router.get("/summary", response_class=HTMLResponse)
def summary_page(
    request: Request,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
    poll_jobs: PollJobManager = Depends(get_poll_job_manager),
    scheduler: MonitoringScheduler = Depends(get_monitoring_scheduler),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "summary.html",
        {
            "active_nav": "summary",
            "toast": _toast_from_query(request),
            **summary_page_context(store, state),
            **_poll_ui_ctx(
                poll_jobs,
                store,
                scheduler,
                refresh_url="/summary",
                refresh_target=".page-content",
                refresh_select=".page-content",
            ),
        },
    )


def _placeholder_page(
    request: Request,
    *,
    active_nav: str,
    section_title: str,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "placeholder_section.html",
        {
            "active_nav": active_nav,
            "section_title": section_title,
            "toast": _toast_from_query(request),
        },
    )


@router.get("/budget", response_class=HTMLResponse)
def budget_page(request: Request) -> HTMLResponse:
    return _placeholder_page(request, active_nav="budget", section_title="Бюджет")


@router.get("/arsenal", response_class=HTMLResponse)
def arsenal_page(
    request: Request,
    object_type: str = "",
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "arsenal.html",
        {
            "active_nav": "arsenal",
            "toast": _toast_from_query(request),
            **arsenal_page_context(state, object_type=object_type),
        },
    )


@router.get("/arsenal/partials/dashboard", response_class=HTMLResponse)
def arsenal_dashboard_partial(
    request: Request,
    object_type: str = "",
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "partials/arsenal_dashboard.html",
        arsenal_page_context(state, object_type=object_type),
    )


@router.get("/arsenal/partials/detail", response_class=HTMLResponse)
def arsenal_detail_partial(
    request: Request,
    dimension: str = "",
    value: str = "",
    system_type: str = "",
    status: str = "",
    object_type: str = "",
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "partials/arsenal_detail.html",
        arsenal_detail_context(
            state,
            dimension=dimension,
            value=value,
            system_type=system_type,
            status=status,
            object_type=object_type,
        ),
    )


@router.get("/arsenal/passport/{passport_number}", response_class=HTMLResponse)
def arsenal_passport_partial(
    request: Request,
    passport_number: str,
    object_type: str = "",
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "partials/arsenal_passport_card.html",
        arsenal_passport_context(
            state,
            passport_number,
            object_type=object_type,
        ),
    )


def _arsenal_export_html_response(
    request: Request,
    state: StateStore,
    *,
    object_type: str = "",
) -> Response:
    page_ctx = arsenal_page_context(state, object_type=object_type)
    if not page_ctx.get("arsenal_has_data"):
        return _redirect(
            "/arsenal",
            "error",
            "Нет данных Арсенал для экспорта",
            request=request,
        )
    export_ctx = build_arsenal_export_context(page_ctx)
    filename = arsenal_export_filename(object_type)
    html = render_arsenal_export_html(export_ctx)
    response = HTMLResponse(content=html)
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@router.get("/arsenal/export.html", include_in_schema=False)
def arsenal_export_html(
    request: Request,
    object_type: str = "",
    state: StateStore = Depends(get_state_store),
) -> Response:
    return _arsenal_export_html_response(
        request, state, object_type=object_type
    )


@router.post("/arsenal/report/email", include_in_schema=False)
def arsenal_report_email(
    request: Request,
    object_type: str = "",
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> Response:
    from ..email_sender import send_report_email
    from ..report_delivery import validate_email_config

    page_ctx = arsenal_page_context(state, object_type=object_type)
    if not page_ctx.get("arsenal_has_data"):
        return JSONResponse(
            {"ok": False, "message": "Нет данных Арсенал для отправки"},
            status_code=400,
        )

    config = store.load()
    email_cfg = config.email_report
    config_errors = validate_email_config(email_cfg)
    if config_errors:
        return JSONResponse(
            {
                "ok": False,
                "message": "Настройте email_report в config.json: "
                + "; ".join(config_errors),
            },
            status_code=400,
        )

    export_ctx = build_arsenal_export_context(page_ctx)
    attachment_html = render_arsenal_export_html(export_ctx)
    filename = arsenal_export_filename(object_type)
    body_html = render_arsenal_email_body(export_ctx)
    subject = arsenal_email_subject(object_type)

    try:
        send_report_email(
            email_cfg,
            body_html=body_html,
            attachments=[(filename, attachment_html)],
            subject=subject,
        )
    except Exception as exc:
        short = str(exc)[:200] + ("…" if len(str(exc)) > 200 else "")
        return JSONResponse(
            {"ok": False, "message": f"Ошибка отправки: {short}"},
            status_code=500,
        )

    recipients = ", ".join(email_cfg.to_emails)
    return JSONResponse({"ok": True, "message": f"Отчёт отправлен на {recipients}"})


@router.get("/rvr-repeat", response_class=HTMLResponse)
def rvr_repeat_page(
    request: Request,
    date_from: str = Query("", alias="from"),
    date_to: str = Query("", alias="to"),
    threshold: int = 2,
    object_type: str = "",
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "rvr_repeat.html",
        {
            "active_nav": "rvr_repeat",
            "toast": _toast_from_query(request),
            **rvr_repeat_page_context(
                state,
                date_from=date_from or None,
                date_to=date_to or None,
                threshold=threshold,
                object_type=object_type or None,
            ),
        },
    )


@router.get("/rvr-repeat/partials/report", response_class=HTMLResponse)
def rvr_repeat_report_partial(
    request: Request,
    date_from: str = Query("", alias="from"),
    date_to: str = Query("", alias="to"),
    threshold: int = 2,
    object_type: str = "",
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "partials/rvr_repeat_report.html",
        rvr_repeat_page_context(
            state,
            date_from=date_from or None,
            date_to=date_to or None,
            threshold=threshold,
            object_type=object_type or None,
        ),
    )


def _rvr_repeat_query_params(request: Request) -> dict[str, str | int]:
    qp = request.query_params
    return {
        "date_from": qp.get("from") or qp.get("date_from") or "",
        "date_to": qp.get("to") or qp.get("date_to") or "",
        "threshold": int(qp.get("threshold") or 2),
        "object_type": qp.get("object_type") or "",
    }


def _rvr_repeat_export_response(
    request: Request,
    state: StateStore,
) -> Response:
    params = _rvr_repeat_query_params(request)
    page_ctx = rvr_repeat_page_context(
        state,
        date_from=params["date_from"] or None,
        date_to=params["date_to"] or None,
        threshold=int(params["threshold"]),
        object_type=str(params.get("object_type") or "") or None,
    )
    report = page_ctx.get("rvr_report")
    if not report or not report.get("has_data"):
        return _redirect(
            "/rvr-repeat",
            "error",
            "Нет данных для экспорта за выбранный период",
            request=request,
        )
    xlsx_bytes = build_rvr_repeat_xlsx(report)
    filename = rvr_repeat_export_filename(report)
    return Response(
        content=xlsx_bytes,
        media_type=XLSX_MIME,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/rvr-repeat/export.xlsx", include_in_schema=False)
def rvr_repeat_export_xlsx(
    request: Request,
    state: StateStore = Depends(get_state_store),
) -> Response:
    return _rvr_repeat_export_response(request, state)


@router.post("/rvr-repeat/report/email", include_in_schema=False)
def rvr_repeat_report_email(
    request: Request,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> Response:
    from ..email_sender import send_report_email
    from ..report_delivery import validate_email_config

    params = _rvr_repeat_query_params(request)
    page_ctx = rvr_repeat_page_context(
        state,
        date_from=params["date_from"] or None,
        date_to=params["date_to"] or None,
        threshold=int(params["threshold"]),
        object_type=str(params.get("object_type") or "") or None,
    )
    report = page_ctx.get("rvr_report")
    if not report or not report.get("has_data"):
        return JSONResponse(
            {"ok": False, "message": "Нет данных для отправки за выбранный период"},
            status_code=400,
        )

    config = store.load()
    email_cfg = config.email_report
    config_errors = validate_email_config(email_cfg)
    if config_errors:
        return JSONResponse(
            {
                "ok": False,
                "message": "Настройте email_report в config.json: "
                + "; ".join(config_errors),
            },
            status_code=400,
        )

    xlsx_bytes = build_rvr_repeat_xlsx(report)
    filename = rvr_repeat_export_filename(report)
    body_html = render_rvr_repeat_email_body(report)
    subject = rvr_repeat_email_subject(report)

    try:
        send_report_email(
            email_cfg,
            body_html=body_html,
            binary_attachments=[(filename, xlsx_bytes, XLSX_MIME)],
            subject=subject,
        )
    except Exception as exc:
        short = str(exc)[:200] + ("…" if len(str(exc)) > 200 else "")
        return JSONResponse(
            {"ok": False, "message": f"Ошибка отправки: {short}"},
            status_code=500,
        )

    recipients = ", ".join(email_cfg.to_emails)
    return JSONResponse({"ok": True, "message": f"Отчёт отправлен на {recipients}"})


@router.get("/smartview", response_class=HTMLResponse)
def smartview_page(request: Request) -> HTMLResponse:
    return _placeholder_page(
        request, active_nav="smartview", section_title="Smartview"
    )


@router.get("/sources", response_class=HTMLResponse)
def sources_page(
    request: Request,
    state: StateStore = Depends(get_state_store),
    report_jobs: ReportJobManager = Depends(get_report_job_manager),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "sources.html",
        {
            "active_nav": "sources",
            "toast": _toast_from_query(request),
            **sources_page_context(state, report_jobs),
        },
    )


def _source_job_panel_response(
    request: Request,
    job: ReportJob,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "partials/source_job_panel.html",
        {
            "job": job,
            "refresh_url": f"/sources/partials/{job.source_key}",
            "refresh_target": f"#source-row-{job.source_key}",
        },
    )


def _start_source_load_job(
    key: str,
    store: ConfigStore,
    state: StateStore,
    report_jobs: ReportJobManager,
) -> ReportJob:
    get_source_spec(key)
    deps = RunnerDeps(store=store, state=state)

    def runner(on_progress):
        result = load_source(key, deps, on_progress=on_progress)
        if not result.ok:
            raise RuntimeError(result.message)
        return result.message

    return report_jobs.start(
        runner,
        source_key=key,
        refresh_url=f"/sources/partials/{key}",
        refresh_target=f"#source-row-{key}",
    )


@router.get("/sources/partials/{key}", response_class=HTMLResponse)
def sources_row_partial(
    request: Request,
    key: str,
    state: StateStore = Depends(get_state_store),
    report_jobs: ReportJobManager = Depends(get_report_job_manager),
) -> HTMLResponse:
    spec = get_source_spec(key)
    ctx = {
        "key": spec.key,
        "label": spec.label,
        "button_label": spec.button_label,
        "button_title": spec.button_title,
        "last_import": state.get_latest_source_import(spec.key),
        "active_job": report_jobs.get_active_job(spec.key),
    }
    return templates.TemplateResponse(
        request,
        "partials/source_row.html",
        ctx,
    )


@router.post("/sources/{key}/load", response_class=HTMLResponse)
async def sources_load(
    request: Request,
    key: str,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
    report_jobs: ReportJobManager = Depends(get_report_job_manager),
) -> HTMLResponse:
    job = _start_source_load_job(key, store, state, report_jobs)
    return _source_job_panel_response(request, job)


@router.get("/sources/jobs/{job_id}", response_class=HTMLResponse)
def sources_job_status(
    request: Request,
    job_id: str,
    report_jobs: ReportJobManager = Depends(get_report_job_manager),
) -> HTMLResponse:
    job = report_jobs.get_job(job_id)
    if job is None:
        return HTMLResponse("Задача не найдена", status_code=404)
    return _source_job_panel_response(request, job)


def _payments_job_panel_response(
    request: Request,
    job: ReportJob,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "partials/payments_job_panel.html",
        {
            "job": job,
            "refresh_url": "/payments/partials/report",
            "refresh_target": "#payments-report-root",
            "refresh_select": "#payments-report-root",
        },
    )


def _load_requests_from_input_data(
    state: StateStore,
    report_jobs: ReportJobManager,
) -> tuple[bool, str, ReportJob | None]:
    try:
        source = find_latest_requests_source_file()
        dest, size = import_requests_from_source(source)
    except FileNotFoundError as exc:
        state.record_source_import(
            "requests",
            filename=None,
            record_count=0,
            status="error",
            message=str(exc),
        )
        return False, str(exc), None
    except Exception as exc:
        state.record_source_import(
            "requests",
            filename=None,
            record_count=0,
            status="error",
            message=str(exc),
        )
        return False, f"Ошибка загрузки файла: {exc}", None

    state.record_source_import(
        "requests",
        filename=source.name,
        record_count=0,
        status="ok",
        message=(
            f"Загружен {source.name} ({size // 1024} КБ), "
            "запущена генерация отчёта"
        ),
    )
    job = report_jobs.start_report(
        dest,
        refresh_url="/payments/partials/report",
        refresh_target="#payments-report-root",
        refresh_select="#payments-report-root",
        naumen_cost_map=state.naumen_cost_by_sberdrug(),
    )
    return True, f"Загружен {source.name}, формируется отчёт", job


@router.get("/payments", response_class=HTMLResponse)
def payments_page(
    request: Request,
    state: StateStore = Depends(get_state_store),
    report_jobs: ReportJobManager = Depends(get_report_job_manager),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "payments.html",
        {
            "active_nav": "payments",
            "toast": _toast_from_query(request),
            **payments_page_context(state, report_jobs),
        },
    )


@router.get("/payments/partials/report", response_class=HTMLResponse)
def payments_report_partial(
    request: Request,
    state: StateStore = Depends(get_state_store),
    report_jobs: ReportJobManager = Depends(get_report_job_manager),
) -> HTMLResponse:
    ctx = payments_page_context(state, report_jobs)
    return templates.TemplateResponse(
        request,
        "partials/payments_report.html",
        ctx,
    )


@router.get("/payments/jobs/{job_id}", response_class=HTMLResponse)
def payments_job_status(
    request: Request,
    job_id: str,
    report_jobs: ReportJobManager = Depends(get_report_job_manager),
) -> HTMLResponse:
    job = report_jobs.get_job(job_id)
    if job is None:
        return HTMLResponse("Задача не найдена", status_code=404)
    return _payments_job_panel_response(request, job)


@router.post("/payments/upload", response_class=HTMLResponse)
async def payments_upload(
    request: Request,
    state: StateStore = Depends(get_state_store),
    report_jobs: ReportJobManager = Depends(get_report_job_manager),
) -> Response:
    ok, message, _job = _load_requests_from_input_data(state, report_jobs)
    if not ok:
        return _redirect("/payments", "error", message, request=request)
    return _redirect("/payments", "success", message, request=request)


@router.post("/payments/refresh", response_class=HTMLResponse)
async def payments_refresh(
    request: Request,
    state: StateStore = Depends(get_state_store),
    report_jobs: ReportJobManager = Depends(get_report_job_manager),
) -> Response:
    dest = requests_file_path()
    if not dest.is_file():
        if request.headers.get("HX-Request") == "true":
            response = HTMLResponse(
                '<p class="banner-error">Сначала загрузите заявки с ПП (кнопка «Загрузить»)</p>',
                status_code=400,
            )
            response.headers["HX-Trigger"] = json.dumps(
                {
                    "showToast": {
                        "type": "error",
                        "message": "Сначала загрузите заявки с ПП",
                    }
                },
                ensure_ascii=False,
            )
            return response
        return _redirect(
            "/payments",
            "error",
            "Сначала загрузите заявки с ПП",
            request=request,
        )

    job = report_jobs.start_report(
        dest,
        refresh_url="/payments/partials/report",
        refresh_target="#payments-report-root",
        refresh_select="#payments-report-root",
        naumen_cost_map=state.naumen_cost_by_sberdrug(),
    )
    return _payments_job_panel_response(request, job)


def _parse_payments_view_params(request: Request) -> tuple[str, dict[str, str]]:
    kind = request.query_params.get("kind", "modern")
    if kind not in ("modern", "rvr"):
        kind = "modern"
    metrics: dict[str, str] = {}
    for key, _title in SECTION_SPECS:
        raw = request.query_params.get(f"m_{key}")
        if raw in ("amount", "count"):
            metrics[key] = raw
    return kind, metrics


def _payments_export_html_response(
    request: Request,
    *,
    kind: str,
    metrics: dict[str, str],
) -> Response:
    report = load_report_artifact()
    if not report:
        if request.headers.get("HX-Request") == "true":
            return HTMLResponse("Отчёт не сформирован", status_code=404)
        return _redirect("/payments", "error", "Сначала сформируйте отчёт", request=request)
    try:
        context = build_payments_export_context(report, kind, metrics)
    except ValueError as exc:
        return _redirect("/payments", "error", str(exc), request=request)
    filename = payments_export_filename(kind)
    html = render_payments_export_html(context)
    response = HTMLResponse(content=html)
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@router.get("/payments/export.html", include_in_schema=False)
def payments_export_html(request: Request) -> Response:
    kind, metrics = _parse_payments_view_params(request)
    return _payments_export_html_response(request, kind=kind, metrics=metrics)


@router.post("/payments/report/email", include_in_schema=False)
def payments_report_email(
    request: Request,
    store: ConfigStore = Depends(get_store),
) -> Response:
    from ..email_sender import send_report_email
    from ..report_delivery import validate_email_config

    _kind, metrics = _parse_payments_view_params(request)
    report = load_report_artifact()
    if not report:
        return JSONResponse(
            {"ok": False, "message": "Сначала сформируйте отчёт"},
            status_code=400,
        )
    config = store.load()
    email_cfg = config.email_report
    config_errors = validate_email_config(email_cfg)
    if config_errors:
        return JSONResponse(
            {
                "ok": False,
                "message": "Настройте email_report в config.json: " + "; ".join(config_errors),
            },
            status_code=400,
        )
    metrics_rvr = {key: "count" for key, _ in SECTION_SPECS}
    try:
        modern_context = build_payments_export_context(report, "modern", metrics)
        rvr_context = build_payments_export_context(report, "rvr", metrics_rvr)
    except ValueError as exc:
        return JSONResponse({"ok": False, "message": str(exc)}, status_code=400)

    attachments = [
        (payments_export_filename("modern"), render_payments_export_html(modern_context)),
        (payments_export_filename("rvr"), render_payments_export_html(rvr_context)),
    ]
    body_html = render_payments_email_body_combined(modern_context, rvr_context)
    subject = payments_email_subject_combined()
    try:
        send_report_email(
            email_cfg,
            body_html=body_html,
            attachments=attachments,
            subject=subject,
        )
    except Exception as exc:
        short = str(exc)[:200] + ("…" if len(str(exc)) > 200 else "")
        return JSONResponse(
            {"ok": False, "message": f"Ошибка отправки: {short}"},
            status_code=500,
        )
    recipients = ", ".join(email_cfg.to_emails)
    return JSONResponse({"ok": True, "message": f"Отчёт отправлен на {recipients}"})


@router.get("/health", include_in_schema=False)
def health() -> dict[str, str]:
    return {"status": "ok", "log_file": str(get_log_file_path())}


def _monitoring_page_ctx(
    store: ConfigStore,
    state: StateStore,
    *,
    sort: SortMode = "status",
    view: str = "",
    tab: str = "",
    search: str = "",
    problems_only: bool = True,
    category: str = "",
) -> dict:
    inventory_view = "table" if view.strip().lower() == "table" else "groups"
    monitoring_tab = "health" if tab.strip().lower() == "health" else "inventory"
    recorders = filter_recorders_by_kind(store.list_recorders(), "tsv")  # type: ignore[arg-type]
    metrics = _metrics_map(state)
    excluded = _excluded_ids(store)
    if inventory_view == "table":
        recorders_display = sorted(
            recorders,
            key=lambda r: (r.object_name.lower(), r.host),
        )
        groups = []
    else:
        recorders_display = recorders
        groups = group_by_object(
            recorders, "", sort, metrics, excluded_ids=excluded
        )
    ctx: dict = {
        "active_nav": "monitoring",
        "inventory_view": inventory_view,
        "monitoring_tab": monitoring_tab,
        "groups": groups,
        "recorders": recorders_display,
        "metrics_map": metrics,
        "excluded_ids": excluded,
        "sort": sort,
        "visible_device_kinds": ("tsv",),
        **_inventory_kpi_ctx(store, state, kind="tsv"),
    }
    if monitoring_tab == "health":
        category_filter: Optional[HealthCategory] = None
        if category.strip() in CATEGORY_LABELS:
            category_filter = category.strip()  # type: ignore[assignment]
        enc = {
            "search": search,
            "problems_only": "true" if problems_only else "false",
        }
        if category_filter:
            enc["category"] = category_filter
        qs = urlencode(enc)
        dash_url = f"/monitoring/partials/health-dashboard?{qs}"
        ctx.update(
            {
                "health_search": search,
                "health_problems_only": problems_only,
                "health_category_filter": category_filter,
                "health_category_options": list(CATEGORY_LABELS.items()),
                **_health_dashboard_ctx(
                    store,
                    state,
                    search=search,
                    problems_only=problems_only,
                    highlight_category=category_filter,
                    refresh_url=dash_url,
                ),
            }
        )
    return ctx


@router.get("/monitoring", response_class=HTMLResponse)
def monitoring_page(
    request: Request,
    sort: SortMode = "status",
    view: str = "",
    tab: str = "",
    search: str = "",
    problems_only: str = "true",
    category: str = "",
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
    poll_jobs: PollJobManager = Depends(get_poll_job_manager),
    scheduler: MonitoringScheduler = Depends(get_monitoring_scheduler),
) -> HTMLResponse:
    only_problems = problems_only.lower() not in ("false", "0", "no")
    ctx = _monitoring_page_ctx(
        store,
        state,
        sort=sort,
        view=view,
        tab=tab,
        search=search,
        problems_only=only_problems,
        category=category,
    )
    toast = _toast_from_query(request)
    if ctx["monitoring_tab"] == "health":
        enc = {
            "search": search,
            "problems_only": "true" if only_problems else "false",
        }
        if category.strip() in CATEGORY_LABELS:
            enc["category"] = category.strip()
        qs = urlencode(enc)
        poll_refresh_url = f"/monitoring/partials/health-dashboard?{qs}"
        poll_refresh_target = "#health-dashboard-stack"
    elif ctx["inventory_view"] == "table":
        poll_refresh_url = "/monitoring/partials/table"
        poll_refresh_target = "#inventory-table-root"
    else:
        poll_refresh_url = "/monitoring/partials/groups"
        poll_refresh_target = "#object-groups"
    ctx.update(
        {
            "toast": toast,
            **_poll_ui_ctx(
                poll_jobs,
                store,
                scheduler,
                refresh_url=poll_refresh_url,
                refresh_target=poll_refresh_target,
            ),
        }
    )
    return templates.TemplateResponse(request, "monitoring.html", ctx)


@router.get("/objects", include_in_schema=False)
def objects_page_redirect(
    sort: SortMode = "status",
    view: str = "",
    tab: str = "",
) -> RedirectResponse:
    params: dict[str, str] = {}
    if view:
        params["view"] = view
    if sort != "status":
        params["sort"] = sort
    if tab:
        params["tab"] = tab
    qs = f"?{urlencode(params)}" if params else ""
    return RedirectResponse(url=f"/monitoring{qs}", status_code=302)


@router.post("/objects/sync-cmdb", response_class=HTMLResponse)
def objects_sync_cmdb(
    request: Request,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> Response:
    deps = RunnerDeps(store=store, state=state)
    result = load_source("cmdb", deps)
    if result.ok:
        return _redirect("/objects", "success", result.message, request=request)
    return _redirect("/objects", "error", result.message, request=request)


@router.post("/objects/report/email", response_class=HTMLResponse)
def objects_report_email(
    request: Request,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> Response:
    return monitoring_report_email(request, store, state)


def _send_report_email_response(
    request: Request,
    store: ConfigStore,
    state: StateStore,
    *,
    redirect_path: str,
) -> Response:
    from ..report_delivery import ReportDeliveryService

    service = ReportDeliveryService(config_store=store, state_store=state)
    result = service.send_report_now(trigger="manual")
    if result.ok:
        return _redirect(redirect_path, "success", result.message, request=request)
    return _redirect(redirect_path, "error", result.message, request=request)


@router.post("/summary/report/email", response_class=HTMLResponse)
def summary_report_email(
    request: Request,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> Response:
    return _send_report_email_response(
        request, store, state, redirect_path="/summary"
    )


@router.post("/monitoring/report/email", response_class=HTMLResponse)
def monitoring_report_email(
    request: Request,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> Response:
    return _send_report_email_response(
        request, store, state, redirect_path="/monitoring"
    )


@router.get("/objects/partials/health-dashboard", include_in_schema=False)
def objects_health_dashboard_partial_redirect() -> RedirectResponse:
    return RedirectResponse(url="/monitoring/partials/health-dashboard", status_code=302)


@router.get("/monitoring/partials/health-dashboard", response_class=HTMLResponse)
def monitoring_health_dashboard_partial(
    request: Request,
    search: str = "",
    problems_only: str = "true",
    category: str = "",
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    only_problems = problems_only.lower() not in ("false", "0", "no")
    highlight_category: Optional[HealthCategory] = None
    if category.strip() in CATEGORY_LABELS:
        highlight_category = category.strip()  # type: ignore[assignment]
    enc = {
        "search": search,
        "problems_only": "true" if only_problems else "false",
    }
    if highlight_category:
        enc["category"] = highlight_category
    qs = urlencode(enc)
    return _health_dashboard_response(
        request,
        store,
        state,
        search=search,
        problems_only=only_problems,
        highlight_category=highlight_category,
        refresh_url=f"/monitoring/partials/health-dashboard?{qs}",
    )


@router.get("/objects/partials/time-dashboard", include_in_schema=False)
def objects_time_dashboard_partial_redirect() -> RedirectResponse:
    return RedirectResponse(url="/monitoring/partials/time-dashboard", status_code=302)


@router.get("/monitoring/partials/time-dashboard", response_class=HTMLResponse)
def monitoring_time_dashboard_partial(
    request: Request,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    return _time_dashboard_response(
        request,
        store,
        state,
        refresh_url="/monitoring/partials/time-dashboard",
    )


@router.get("/objects/partials/table", include_in_schema=False)
def objects_table_partial_redirect() -> RedirectResponse:
    return RedirectResponse(url="/monitoring/partials/table", status_code=302)


@router.get("/monitoring/partials/table", response_class=HTMLResponse)
def monitoring_table_partial(
    request: Request,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    recorders = sorted(
        filter_recorders_by_kind(store.list_recorders(), "tsv"),  # type: ignore[arg-type]
        key=lambda r: (r.object_name.lower(), r.host),
    )
    excluded = _excluded_ids(store)
    return templates.TemplateResponse(
        request,
        "partials/objects_table.html",
        {
            "recorders": recorders,
            "metrics_map": _metrics_map(state),
            "excluded_ids": excluded,
        },
    )


@router.get("/objects/partials/groups", include_in_schema=False)
def objects_groups_partial_redirect() -> RedirectResponse:
    return RedirectResponse(url="/monitoring/partials/groups", status_code=302)


@router.get("/monitoring/partials/groups", response_class=HTMLResponse)
def monitoring_groups_partial(
    request: Request,
    search: str = "",
    sort: SortMode = "status",
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    recorders = filter_recorders_by_kind(store.list_recorders(), "tsv")  # type: ignore[arg-type]
    metrics = _metrics_map(state)
    excluded = _excluded_ids(store)
    groups = group_by_object(
        recorders, search, sort, metrics, excluded_ids=excluded
    )
    ctx = {
        "groups": groups,
        "recorders": recorders,
        "metrics_map": metrics,
        "excluded_ids": excluded,
        "inventory_view": "groups",
        "visible_device_kinds": ("tsv",),
        **_inventory_kpi_ctx(store, state, kind="tsv"),
    }
    return templates.TemplateResponse(
        request,
        "partials/objects_groups_refresh.html",
        ctx,
    )


def _kind_section_response(
    request: Request,
    kind: str,
    *,
    sort: SortMode = "status",
    store: ConfigStore,
    state: StateStore,
    poll_jobs: PollJobManager,
    scheduler: MonitoringScheduler,
) -> HTMLResponse:
    active_nav = kind
    groups_partial_url = f"/{kind}/partials/groups"
    ctx = kind_section_page_context(store, state, kind, sort=sort)  # type: ignore[arg-type]
    ctx.update(
        {
            "active_nav": active_nav,
            "groups_partial_url": groups_partial_url,
            "toast": _toast_from_query(request),
            **_poll_ui_ctx(
                poll_jobs,
                store,
                scheduler,
                refresh_url=f"/{kind}",
                refresh_target=".page-content",
                refresh_select=".page-content",
            ),
        }
    )
    return templates.TemplateResponse(request, "kind_section.html", ctx)


@router.get("/skud", response_class=HTMLResponse)
def skud_page(
    request: Request,
    sort: SortMode = "status",
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
    poll_jobs: PollJobManager = Depends(get_poll_job_manager),
    scheduler: MonitoringScheduler = Depends(get_monitoring_scheduler),
) -> HTMLResponse:
    return _kind_section_response(
        request,
        "skud",
        sort=sort,
        store=store,
        state=state,
        poll_jobs=poll_jobs,
        scheduler=scheduler,
    )


@router.get("/bio", response_class=HTMLResponse)
def bio_page(
    request: Request,
    sort: SortMode = "status",
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
    poll_jobs: PollJobManager = Depends(get_poll_job_manager),
    scheduler: MonitoringScheduler = Depends(get_monitoring_scheduler),
) -> HTMLResponse:
    return _kind_section_response(
        request,
        "bio",
        sort=sort,
        store=store,
        state=state,
        poll_jobs=poll_jobs,
        scheduler=scheduler,
    )


def _kind_groups_partial(
    request: Request,
    kind: str,
    *,
    search: str = "",
    sort: SortMode = "status",
    store: ConfigStore,
    state: StateStore,
) -> HTMLResponse:
    recorders = filter_recorders_by_kind(store.list_recorders(), kind)  # type: ignore[arg-type]
    metrics = _metrics_map(state)
    excluded = _excluded_ids(store)
    groups = group_by_object(
        recorders, search, sort, metrics, excluded_ids=excluded
    )
    return templates.TemplateResponse(
        request,
        "partials/kind_object_groups.html",
        {
            "groups": groups,
            "metrics_map": metrics,
            "excluded_ids": excluded,
        },
    )


@router.get("/skud/partials/groups", response_class=HTMLResponse)
def skud_groups_partial(
    request: Request,
    search: str = "",
    sort: SortMode = "status",
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    return _kind_groups_partial(
        request, "skud", search=search, sort=sort, store=store, state=state
    )


@router.get("/bio/partials/groups", response_class=HTMLResponse)
def bio_groups_partial(
    request: Request,
    search: str = "",
    sort: SortMode = "status",
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    return _kind_groups_partial(
        request, "bio", search=search, sort=sort, store=store, state=state
    )


def _export_errors_html_response(
    store: ConfigStore,
    state: StateStore,
) -> HTMLResponse:
    config = store.load()
    recorders = store.list_recorders()
    metrics = _metrics_map(state)
    report = build_error_report_context(
        recorders,
        metrics,
        config.monitoring,
        credentials=config.credentials,
        ntp_server=config.monitoring.ntp_server or "",
        device_auth="userinfo",
        problem_since_map=state.category_problem_since_map(),
        recorder_problem_since_map=state.recorder_problem_since_map(),
        excluded_ids=excluded_ids_set(config),
    )
    filename = (
        "wisenet-tso-errors-"
        f"{format_for_display(datetime.now(timezone.utc), '%Y%m%d-%H%M')}.html"
    )
    html = render_error_report_html(report)
    response = HTMLResponse(content=html)
    response.headers["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )
    return response


@router.get("/objects/export/errors.html", include_in_schema=False)
def objects_export_errors_redirect() -> RedirectResponse:
    return RedirectResponse(url="/summary/export/errors.html", status_code=302)


@router.get("/monitoring/export/errors.html", include_in_schema=False)
def monitoring_export_errors_redirect() -> RedirectResponse:
    return RedirectResponse(url="/summary/export/errors.html", status_code=302)


@router.get("/summary/export/errors.html", response_class=HTMLResponse)
def summary_export_errors_html(
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    return _export_errors_html_response(store, state)


@router.get("/recorders", include_in_schema=False)
def recorders_page() -> RedirectResponse:
    return RedirectResponse(url="/monitoring?view=table", status_code=302)


@router.get("/recorders/partials/health-dashboard", response_class=HTMLResponse)
def recorders_health_dashboard_partial(
    request: Request,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    return _health_dashboard_response(
        request,
        store,
        state,
        compact=True,
        refresh_url="/recorders/partials/health-dashboard",
    )


@router.get("/recorders/partials/time-dashboard", response_class=HTMLResponse)
def recorders_time_dashboard_partial(
    request: Request,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    return _time_dashboard_response(
        request,
        store,
        state,
        compact=True,
        refresh_url="/recorders/partials/time-dashboard",
    )


@router.get("/time", include_in_schema=False)
def time_page(
    search: str = "",
    problems_only: str = "true",
) -> RedirectResponse:
    only_problems = problems_only.lower() not in ("false", "0", "no")
    qs = urlencode(
        {
            "search": search,
            "problems_only": "true" if only_problems else "false",
            "category": "time",
        }
    )
    return RedirectResponse(url=f"/monitoring?tab=health&{qs}", status_code=302)


@router.get("/time/partials/dashboard", response_class=HTMLResponse)
def time_dashboard_partial(
    request: Request,
    search: str = "",
    problems_only: str = "true",
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    only_problems = problems_only.lower() not in ("false", "0", "no")
    qs = urlencode({"search": search, "problems_only": "true" if only_problems else "false"})
    return _time_dashboard_response(
        request,
        store,
        state,
        search=search,
        problems_only=only_problems,
        show_all_table=not only_problems,
        refresh_url=f"/time/partials/dashboard?{qs}",
    )


@router.get("/status", include_in_schema=False)
def status_page(
    search: str = "",
    problems_only: str = "true",
    category: str = "",
) -> RedirectResponse:
    only_problems = problems_only.lower() not in ("false", "0", "no")
    enc = {
        "tab": "health",
        "search": search,
        "problems_only": "true" if only_problems else "false",
    }
    if category.strip():
        enc["category"] = category.strip()
    return RedirectResponse(url=f"/monitoring?{urlencode(enc)}", status_code=302)


@router.get("/status/partials/dashboard", include_in_schema=False)
def status_dashboard_partial_redirect(
    search: str = "",
    problems_only: str = "true",
    category: str = "",
) -> RedirectResponse:
    only_problems = problems_only.lower() not in ("false", "0", "no")
    enc = {
        "search": search,
        "problems_only": "true" if only_problems else "false",
    }
    if category.strip():
        enc["category"] = category.strip()
    return RedirectResponse(
        url=f"/monitoring/partials/health-dashboard?{urlencode(enc)}",
        status_code=302,
    )


@router.get("/settings", response_class=HTMLResponse)
def settings_page(
    request: Request,
    store: ConfigStore = Depends(get_store),
) -> HTMLResponse:
    creds = store.get_credentials()
    saved = request.query_params.get("saved")
    toast = {"type": "success", "message": "Настройки сохранены"} if saved else None
    return templates.TemplateResponse(
        request,
        "settings.html",
        {
            "active_nav": "settings",
            "credentials": creds,
            "errors": None,
            "toast": toast,
        },
    )


@router.post("/settings", response_class=HTMLResponse)
def settings_save(
    request: Request,
    username: str = Form(""),
    password: str = Form(""),
    store: ConfigStore = Depends(get_store),
) -> Response:
    errors: dict[str, str] = {}
    if not username.strip():
        errors["username"] = "Укажите логин"
    if not password:
        errors["password"] = "Укажите пароль"
    if errors:
        if request.headers.get("HX-Request"):
            return templates.TemplateResponse(
                request,
                "settings.html",
                {
                    "active_nav": "settings",
                    "credentials": store.get_credentials(),
                    "errors": errors,
                    "toast": None,
                },
                status_code=400,
            )
        return templates.TemplateResponse(
            request,
            "settings.html",
            {
                "active_nav": "settings",
                "credentials": store.get_credentials(),
                "errors": errors,
                "toast": None,
            },
            status_code=400,
        )
    store.update_credentials(username.strip(), password)
    return RedirectResponse(url="/settings?saved=1", status_code=303)


@router.get("/settings/exclusions", response_class=HTMLResponse)
def settings_exclusions_page(
    request: Request,
    store: ConfigStore = Depends(get_store),
) -> HTMLResponse:
    config = store.load()
    excluded = excluded_ids_set(config)
    recorders = sorted(
        config.recorders,
        key=lambda r: (r.object_name.lower(), display_recorder_name(r).lower()),
    )
    return templates.TemplateResponse(
        request,
        "settings_exclusions.html",
        {
            "active_nav": "settings",
            "recorders": recorders,
            "excluded_ids": excluded,
            "toast": _toast_from_query(request),
        },
    )


@router.post("/settings/exclusions", response_class=HTMLResponse)
def settings_exclusions_save(
    request: Request,
    store: ConfigStore = Depends(get_store),
    recorder_ids: list[str] = Form(default=[]),
) -> Response:
    store.set_exclusions(recorder_ids)
    return _redirect(
        "/settings/exclusions",
        "success",
        "Список исключений сохранён",
        request=request,
    )


@router.get("/recorders/new", response_class=HTMLResponse)
def recorder_new_form(
    request: Request,
    store: ConfigStore = Depends(get_store),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "partials/recorder_form.html",
        {
            "recorder": None,
            "object_names": _object_names(store),
            "form": None,
            "errors": None,
        },
    )


@router.get("/recorders/{recorder_id}/edit", response_class=HTMLResponse)
def recorder_edit_form(
    request: Request,
    recorder_id: str,
    store: ConfigStore = Depends(get_store),
) -> HTMLResponse:
    recorder = store.get_recorder(recorder_id)
    if not recorder:
        return HTMLResponse("Регистратор не найден", status_code=404)
    return templates.TemplateResponse(
        request,
        "partials/recorder_form.html",
        {
            "recorder": recorder,
            "object_names": _object_names(store),
            "form": None,
            "errors": None,
        },
    )


@router.post("/recorders", response_class=HTMLResponse)
async def recorder_create(
    request: Request,
    object_name: str = Form(""),
    name: str = Form(""),
    host: str = Form(""),
    port: str = Form("80"),
    use_https: str = Form("false"),
    mac: str = Form(""),
    device_kind: str = Form("tsv"),
    store: ConfigStore = Depends(get_store),
) -> Response:
    data, errors = parse_recorder_form(
        object_name, name, host, port, use_https, mac, device_kind
    )
    if errors or data is None:
        return templates.TemplateResponse(
            request,
            "partials/recorder_form.html",
            {
                "recorder": None,
                "object_names": _object_names(store),
                "form": data,
                "errors": errors,
            },
            status_code=400,
        )
    try:
        body = RecorderCreate(
            object_name=data.object_name,
            name=data.name or None,
            host=data.host,
            port=data.port,
            use_https=data.use_https,
            mac=data.mac or None,
            device_kind=data.device_kind,  # type: ignore[arg-type]
        )
    except ValidationError as e:
        return _form_validation_error(request, None, store, e)

    store.create_recorder(body)
    return _redirect("/monitoring", "success", "Устройство ТСВ добавлено", request=request)


@router.post("/recorders/{recorder_id}", response_class=HTMLResponse)
async def recorder_update(
    request: Request,
    recorder_id: str,
    object_name: str = Form(""),
    name: str = Form(""),
    host: str = Form(""),
    port: str = Form("80"),
    use_https: str = Form("false"),
    mac: str = Form(""),
    device_kind: str = Form("tsv"),
    store: ConfigStore = Depends(get_store),
) -> Response:
    recorder = store.get_recorder(recorder_id)
    if not recorder:
        return HTMLResponse("Не найден", status_code=404)

    data, errors = parse_recorder_form(
        object_name, name, host, port, use_https, mac, device_kind
    )
    if errors or data is None:
        return templates.TemplateResponse(
            request,
            "partials/recorder_form.html",
            {
                "recorder": recorder,
                "object_names": _object_names(store),
                "form": data,
                "errors": errors,
            },
            status_code=400,
        )
    try:
        body = RecorderUpdate(
            object_name=data.object_name,
            name=data.name or None,
            host=data.host,
            port=data.port,
            use_https=data.use_https,
            mac=data.mac or None,
            device_kind=data.device_kind,  # type: ignore[arg-type]
        )
    except ValidationError as e:
        return _form_validation_error(request, recorder, store, e)

    store.update_recorder(recorder_id, body)
    return _redirect("/monitoring", "success", "Устройство ТСВ сохранено", request=request)


@router.post("/recorders/{recorder_id}/delete", response_class=HTMLResponse)
def recorder_delete(
    request: Request,
    recorder_id: str,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> Response:
    if not store.delete_recorder(recorder_id):
        return HTMLResponse("Не найден", status_code=404)
    state.delete_recorder_data(recorder_id)
    referer = request.headers.get("HX-Current-URL", "")
    if "/recorders" in referer and "/monitoring" not in referer:
        return _redirect("/recorders", "success", "Устройство ТСВ удалено", request=request)
    return _redirect("/monitoring", "success", "Устройство ТСВ удалено", request=request)


@router.post("/recorders/{recorder_id}/exclude", response_class=HTMLResponse)
def recorder_exclude(
    request: Request,
    recorder_id: str,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    if not store.add_exclusion(recorder_id):
        return HTMLResponse("Не найден", status_code=404)
    recorder = store.get_recorder(recorder_id)
    if not recorder:
        return HTMLResponse("Не найден", status_code=404)
    referer = request.headers.get("HX-Current-URL", "")
    template = _recorder_partial_template(referer)
    metrics = state.get_recorder_metrics(recorder_id)
    response = templates.TemplateResponse(
        request,
        template,
        _recorder_partial_context(
            recorder,
            metrics,
            template=template,
            excluded_ids=_excluded_ids(store),
        ),
    )
    return _attach_toast(
        response, "success", f"{display_recorder_name(recorder)} исключён из мониторинга"
    )


@router.post("/recorders/{recorder_id}/unexclude", response_class=HTMLResponse)
def recorder_unexclude(
    request: Request,
    recorder_id: str,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    store.remove_exclusion(recorder_id)
    recorder = store.get_recorder(recorder_id)
    if not recorder:
        return HTMLResponse("Не найден", status_code=404)
    referer = request.headers.get("HX-Current-URL", "")
    template = _recorder_partial_template(referer)
    metrics = state.get_recorder_metrics(recorder_id)
    response = templates.TemplateResponse(
        request,
        template,
        _recorder_partial_context(
            recorder,
            metrics,
            template=template,
            excluded_ids=_excluded_ids(store),
        ),
    )
    return _attach_toast(
        response, "success", f"{display_recorder_name(recorder)} снова в мониторинге"
    )


@router.post("/recorders/{recorder_id}/check", response_class=HTMLResponse)
async def recorder_check(
    request: Request,
    recorder_id: str,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    start = time.perf_counter()
    referer = request.headers.get("HX-Current-URL", "")
    is_htmx = request.headers.get("HX-Request") == "true"

    check_logger.info(
        "check requested",
        extra={
            "event": "check_start",
            "extra_recorder_id": recorder_id,
            "extra_htmx": is_htmx,
            "extra_htmx_url": referer or None,
        },
    )

    recorder = store.get_recorder(recorder_id)
    if not recorder:
        check_logger.warning(
            "recorder not found",
            extra={"event": "check_not_found", "extra_recorder_id": recorder_id},
        )
        return HTMLResponse("Не найден", status_code=404)

    config = store.load()
    if is_excluded(recorder_id, config):
        return HTMLResponse(
            "Регистратор исключён из мониторинга", status_code=400
        )

    credentials = store.get_credentials()
    has_credentials = bool(credentials.username and credentials.password)
    check_logger.info(
        "check running",
        extra={
            "event": "check_running",
            "extra_recorder_id": recorder.id,
            "extra_object_name": recorder.object_name,
            "extra_host": recorder.host,
            "extra_port": recorder.port,
            "extra_excluded": is_excluded(recorder.id, config),
            "extra_has_credentials": has_credentials,
        },
    )

    await poll_single_recorder(store, state, recorder, include_inventory=True)
    updated = store.get_recorder(recorder_id)
    if not updated:
        return HTMLResponse("Не найден", status_code=404)
    outcome_status = updated.last_status
    metrics = state.get_recorder_metrics(recorder_id)
    template = _recorder_partial_template(referer)
    duration_ms = round((time.perf_counter() - start) * 1000)
    check_logger.info(
        "check finished",
        extra={
            "event": "check_done",
            "extra_recorder_id": recorder_id,
            "extra_status": outcome_status.value if outcome_status else None,
            "extra_effective_status": effective_status(updated, metrics),
            "extra_error": updated.last_error,
            "extra_duration_ms": duration_ms,
            "extra_template": template,
        },
    )

    response = templates.TemplateResponse(
        request,
        template,
        _recorder_partial_context(
            updated,
            metrics,
            template=template,
            excluded_ids=_excluded_ids(store),
        ),
    )
    if outcome_status and outcome_status.value == "online":
        return _attach_toast(
            response,
            "success",
            f"{display_recorder_name(updated)}: доступен",
        )
    if outcome_status and outcome_status.value == "offline":
        return _attach_toast(
            response,
            "error",
            updated.last_error or "Недоступен",
        )
    return response


@router.post("/recorders/{recorder_id}/ntp/enable", response_class=HTMLResponse)
async def recorder_enable_ntp(
    request: Request,
    recorder_id: str,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    referer = request.headers.get("HX-Current-URL", "")
    template = _recorder_partial_template(referer)

    recorder = store.get_recorder(recorder_id)
    if not recorder:
        return HTMLResponse("Не найден", status_code=404)

    config = store.load()
    if is_excluded(recorder_id, config):
        return HTMLResponse("Регистратор исключён из мониторинга", status_code=400)

    credentials = config.credentials
    ntp_server = (config.monitoring.ntp_server or "").strip()
    metrics = state.get_recorder_metrics(recorder_id)
    use_time_dashboard = _wants_time_dashboard_response(request)
    time_params = _time_params_from_referer(referer) if use_time_dashboard else {}

    def _error_response(message: str, status_code: int = 400) -> HTMLResponse:
        if use_time_dashboard:
            return _time_dashboard_response(
                request,
                store,
                state,
                toast_type="error",
                toast_message=message,
                status_code=status_code,
                **time_params,
            )
        response = templates.TemplateResponse(
            request,
            template,
            _recorder_partial_context(
                recorder,
                metrics,
                template=template,
                excluded_ids=_excluded_ids(store),
            ),
            status_code=status_code,
        )
        return _attach_toast(response, "error", message)

    if not ntp_server:
        return _error_response(
            "Укажите NTP-сервер в config.json: monitoring.ntp_server"
        )

    if not credentials.username or not credentials.password:
        return _error_response("Не заданы учётные данные API в настройках")

    posix_tz = (config.monitoring.ntp_posix_timezone or "").strip()
    result = await enable_recorder_ntp(
        recorder,
        credentials,
        ntp_server,
        posix_timezone=posix_tz,
    )
    if not result.success:
        return _error_response(result.error or "Не удалось обновить NTP")

    await poll_single_recorder(store, state, recorder, include_inventory=False)
    updated = store.get_recorder(recorder_id) or recorder
    metrics = state.get_recorder_metrics(recorder_id)
    sync_label = sync_type_label(metrics.sync_type if metrics else "NTP")
    ntp_status = metrics.ntp_status if metrics and metrics.ntp_status else "—"
    skew_note = ""
    if metrics and metrics.time_skew_seconds is not None:
        skew_note = f", расхождение {format_skew(metrics.time_skew_seconds)}"

    toast_msg = (
        f"{display_recorder_name(updated)}: NTP обновлён ({ntp_server}). "
        f"Режим: {sync_label}, статус NTP: {ntp_status}{skew_note}"
    )
    if use_time_dashboard:
        return _time_dashboard_response(
            request,
            store,
            state,
            toast_type="success",
            toast_message=toast_msg,
            **time_params,
        )

    response = templates.TemplateResponse(
        request,
        template,
        _recorder_partial_context(
            updated,
            metrics,
            template=template,
            excluded_ids=_excluded_ids(store),
        ),
    )
    return _attach_toast(response, "success", toast_msg)


def _form_validation_error(
    request: Request,
    recorder,
    store: ConfigStore,
    error: ValidationError,
) -> HTMLResponse:
    errors = {
        ".".join(str(x) for x in e["loc"]): e["msg"] for e in error.errors()
    }
    return templates.TemplateResponse(
        request,
        "partials/recorder_form.html",
        {
            "recorder": recorder,
            "object_names": _object_names(store),
            "form": None,
            "errors": errors,
        },
        status_code=400,
    )


def _toast_from_query(request: Request) -> Optional[dict[str, str]]:
    t = request.query_params.get("toast")
    msg = request.query_params.get("msg")
    if t in ("success", "error") and msg:
        return {"type": t, "message": msg}
    return None


def _poll_schedule_hint(store: ConfigStore, *, auto_paused: bool = False) -> str:
    m = store.load().monitoring
    schedule = (
        f"каждые {m.poll_interval_minutes} мин; "
        f"полный — каждые {m.full_poll_interval_minutes} мин; "
        f"инвентаризация (детальный архив по каналам) — раз в 24 ч"
    )
    if auto_paused:
        return f"Автоопрос приостановлен. Расписание без изменений: {schedule}"
    return f"Автоопрос: {schedule}"


def _poll_ui_ctx(
    poll_jobs: PollJobManager,
    store: ConfigStore,
    scheduler: MonitoringScheduler,
    *,
    refresh_url: str,
    refresh_target: str,
    refresh_select: str = "",
    inventory: bool = False,
) -> dict:
    active_job = poll_jobs.get_active_job()
    auto_paused = scheduler.is_auto_paused()
    ctx: dict = {
        "schedule_hint": _poll_schedule_hint(store, auto_paused=auto_paused),
        "refresh_url": refresh_url,
        "refresh_target": refresh_target,
        "refresh_select": refresh_select,
        "poll_page_inventory": inventory,
        "poll_job": active_job,
        "job": active_job,
        "auto_poll_paused": auto_paused,
        "auto_poll_active": not auto_paused,
    }
    if inventory:
        ctx.update(
            {
                "poll_post_url": "/monitoring/inventory-all",
                "poll_button_label": "Инвентаризация всех",
                "poll_button_title": "Перечитывает список камер на всех NVR",
            }
        )
    else:
        ctx.update(
            {
                "poll_post_url": "/monitoring/poll-all",
                "poll_button_label": "Опросить все устройства",
                "poll_button_title": (
                    "Обновляет статус NVR, диски, время и состояние каналов; "
                    "инвентаризация — детальный архив по каждому каналу"
                ),
            }
        )
    return ctx


def _poll_page_actions_response(
    request: Request,
    poll_jobs: PollJobManager,
    store: ConfigStore,
    scheduler: MonitoringScheduler,
    *,
    refresh_url: str,
    refresh_target: str,
    refresh_select: str = "",
    inventory: bool = False,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "partials/poll_page_actions.html",
        _poll_ui_ctx(
            poll_jobs,
            store,
            scheduler,
            refresh_url=refresh_url,
            refresh_target=refresh_target,
            refresh_select=refresh_select,
            inventory=inventory,
        ),
    )


def _poll_job_panel_response(
    request: Request,
    job: PollJob,
    store: ConfigStore,
    scheduler: MonitoringScheduler,
    *,
    refresh_url: str,
    refresh_target: str,
    refresh_select: str = "",
) -> HTMLResponse:
    auto_paused = scheduler.is_auto_paused()
    return templates.TemplateResponse(
        request,
        "partials/poll_job_panel.html",
        {
            "job": job,
            "schedule_hint": _poll_schedule_hint(store, auto_paused=auto_paused),
            "refresh_url": refresh_url,
            "refresh_target": refresh_target,
            "refresh_select": refresh_select,
            "auto_poll_paused": auto_paused,
            "auto_poll_active": not auto_paused,
            "poll_button_label": "Опросить все устройства",
        },
    )


@router.get("/monitoring/poll-ui", response_class=HTMLResponse)
def monitoring_poll_ui(
    request: Request,
    refresh_url: str = "/monitoring/partials/health-dashboard",
    refresh_target: str = "#health-dashboard-stack",
    refresh_select: str = "",
    inventory: str = "",
    store: ConfigStore = Depends(get_store),
    poll_jobs: PollJobManager = Depends(get_poll_job_manager),
    scheduler: MonitoringScheduler = Depends(get_monitoring_scheduler),
) -> HTMLResponse:
    return _poll_page_actions_response(
        request,
        poll_jobs,
        store,
        scheduler,
        refresh_url=refresh_url,
        refresh_target=refresh_target,
        refresh_select=refresh_select,
        inventory=inventory.lower() in ("true", "1", "yes", "on"),
    )


@router.post("/monitoring/poll-all", response_class=HTMLResponse)
async def monitoring_poll_all(
    request: Request,
    refresh_url: str = Form(default="/monitoring/partials/health-dashboard"),
    refresh_target: str = Form(default="#health-dashboard-stack"),
    refresh_select: str = Form(default=""),
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
    poll_jobs: PollJobManager = Depends(get_poll_job_manager),
    scheduler: MonitoringScheduler = Depends(get_monitoring_scheduler),
) -> HTMLResponse:
    job = poll_jobs.start_manual_poll(
        store,
        state,
        include_inventory=False,
        refresh_url=refresh_url or None,
    )
    return _poll_job_panel_response(
        request,
        job,
        store,
        scheduler,
        refresh_url=refresh_url,
        refresh_target=refresh_target,
        refresh_select=refresh_select,
    )


@router.post("/monitoring/poll/cancel", response_class=HTMLResponse)
async def monitoring_poll_cancel(
    request: Request,
    refresh_url: str = Form(default="/monitoring/partials/health-dashboard"),
    refresh_target: str = Form(default="#health-dashboard-stack"),
    refresh_select: str = Form(default=""),
    inventory: str = Form(default=""),
    store: ConfigStore = Depends(get_store),
    poll_jobs: PollJobManager = Depends(get_poll_job_manager),
    scheduler: MonitoringScheduler = Depends(get_monitoring_scheduler),
) -> HTMLResponse:
    cancelled = await poll_jobs.cancel_active_poll()
    response = _poll_page_actions_response(
        request,
        poll_jobs,
        store,
        scheduler,
        refresh_url=refresh_url,
        refresh_target=refresh_target,
        refresh_select=refresh_select,
        inventory=inventory.lower() in ("true", "1", "yes", "on"),
    )
    if cancelled:
        response.headers["HX-Trigger"] = json.dumps(
            {
                "showToast": {
                    "type": "success",
                    "message": "Текущий опрос остановлен",
                }
            },
            ensure_ascii=True,
        )
    return response


@router.post("/monitoring/auto-poll/stop", response_class=HTMLResponse)
def monitoring_auto_poll_stop(
    request: Request,
    refresh_url: str = Form(default="/monitoring/partials/health-dashboard"),
    refresh_target: str = Form(default="#health-dashboard-stack"),
    refresh_select: str = Form(default=""),
    inventory: str = Form(default=""),
    store: ConfigStore = Depends(get_store),
    poll_jobs: PollJobManager = Depends(get_poll_job_manager),
    scheduler: MonitoringScheduler = Depends(get_monitoring_scheduler),
) -> HTMLResponse:
    scheduler.pause_auto()
    response = _poll_page_actions_response(
        request,
        poll_jobs,
        store,
        scheduler,
        refresh_url=refresh_url,
        refresh_target=refresh_target,
        refresh_select=refresh_select,
        inventory=inventory.lower() in ("true", "1", "yes", "on"),
    )
    response.headers["HX-Trigger"] = json.dumps(
        {
            "showToast": {
                "type": "success",
                "message": "Автоматический опрос приостановлен",
            }
        },
        ensure_ascii=True,
    )
    return response


@router.post("/monitoring/auto-poll/resume", response_class=HTMLResponse)
def monitoring_auto_poll_resume(
    request: Request,
    refresh_url: str = Form(default="/monitoring/partials/health-dashboard"),
    refresh_target: str = Form(default="#health-dashboard-stack"),
    refresh_select: str = Form(default=""),
    inventory: str = Form(default=""),
    store: ConfigStore = Depends(get_store),
    poll_jobs: PollJobManager = Depends(get_poll_job_manager),
    scheduler: MonitoringScheduler = Depends(get_monitoring_scheduler),
) -> HTMLResponse:
    scheduler.resume_auto()
    response = _poll_page_actions_response(
        request,
        poll_jobs,
        store,
        scheduler,
        refresh_url=refresh_url,
        refresh_target=refresh_target,
        refresh_select=refresh_select,
        inventory=inventory.lower() in ("true", "1", "yes", "on"),
    )
    response.headers["HX-Trigger"] = json.dumps(
        {
            "showToast": {
                "type": "success",
                "message": "Автоматический опрос возобновлён",
            }
        },
        ensure_ascii=True,
    )
    return response


@router.get("/monitoring/jobs/{job_id}", response_class=HTMLResponse)
def monitoring_job_status(
    request: Request,
    job_id: str,
    store: ConfigStore = Depends(get_store),
    poll_jobs: PollJobManager = Depends(get_poll_job_manager),
    scheduler: MonitoringScheduler = Depends(get_monitoring_scheduler),
) -> HTMLResponse:
    job = poll_jobs.get_job(job_id)
    if not job:
        return HTMLResponse("Задача не найдена", status_code=404)
    refresh_url = request.query_params.get(
        "refresh_url", job.refresh_url or "/monitoring/partials/health-dashboard"
    )
    refresh_target = request.query_params.get("refresh_target", "#health-dashboard-stack")
    refresh_select = request.query_params.get("refresh_select", "")
    return _poll_job_panel_response(
        request,
        job,
        store,
        scheduler,
        refresh_url=refresh_url,
        refresh_target=refresh_target,
        refresh_select=refresh_select,
    )


@router.post("/monitoring/ntp-fix-all", response_class=HTMLResponse)
async def monitoring_ntp_fix_all(
    request: Request,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    referer = request.headers.get("HX-Current-URL", "")
    use_health = _wants_health_dashboard_response(request)
    dash_params = (
        _health_params_from_referer(referer)
        if use_health
        else _time_params_from_referer(referer)
    )

    fix_result = await run_ntp_fix_all(store, state)
    dash_response = (
        _health_dashboard_response if use_health else _time_dashboard_response
    )
    if fix_result.errors and fix_result.total == 0 and fix_result.success == 0:
        return dash_response(
            request,
            store,
            state,
            toast_type="error",
            toast_message=fix_result.errors[0],
            status_code=400,
            **dash_params,
        )

    if fix_result.total == 0:
        msg = "Нет регистраторов, требующих исправления NTP"
        toast_type = "success"
    elif fix_result.failed == 0:
        msg = f"NTP обновлён на {fix_result.success} из {fix_result.total} регистраторов"
        toast_type = "success"
    else:
        msg = (
            f"Успешно: {fix_result.success}, ошибок: {fix_result.failed} "
            f"из {fix_result.total}"
        )
        toast_type = "error" if fix_result.success == 0 else "success"

    if fix_result.errors and fix_result.failed:
        detail = "; ".join(fix_result.errors[:3])
        if len(fix_result.errors) > 3:
            detail += f" … (+{len(fix_result.errors) - 3})"
        msg = f"{msg}. {detail}"

    return dash_response(
        request,
        store,
        state,
        toast_type=toast_type,
        toast_message=msg,
        **dash_params,
    )


@router.post("/monitoring/inventory-all", response_class=HTMLResponse)
async def monitoring_inventory_all(
    request: Request,
    refresh_url: str = Form(default="/monitoring"),
    refresh_target: str = Form(default=".page-content"),
    refresh_select: str = Form(default=".page-content"),
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
    poll_jobs: PollJobManager = Depends(get_poll_job_manager),
    scheduler: MonitoringScheduler = Depends(get_monitoring_scheduler),
) -> HTMLResponse:
    job = poll_jobs.start_manual_poll(
        store,
        state,
        include_inventory=True,
        refresh_url=refresh_url or None,
    )
    return _poll_job_panel_response(
        request,
        job,
        store,
        scheduler,
        refresh_url=refresh_url,
        refresh_target=refresh_target,
        refresh_select=refresh_select,
    )


@router.post("/recorders/{recorder_id}/inventory", response_class=HTMLResponse)
async def recorder_inventory(
    request: Request,
    recorder_id: str,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> Response:
    recorder = store.get_recorder(recorder_id)
    if not recorder:
        return HTMLResponse("Не найден", status_code=404)
    await poll_single_recorder(store, state, recorder, include_inventory=True)
    referer = request.headers.get("HX-Current-URL", "")
    return _redirect("/monitoring", "success", "Каналы обновлены", request=request)
