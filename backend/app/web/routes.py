from __future__ import annotations

import json
import time
from typing import Literal, Optional
from urllib.parse import parse_qs, urlencode, urlparse

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from pydantic import ValidationError

from ..config_store import ConfigStore
from ..logging_config import get_log_file_path, get_logger
from ..models import RecorderCreate, RecorderUpdate
from ..monitoring import (
    poll_single_recorder,
    run_inventory_cycle,
    run_ntp_fix_all,
    run_poll_cycle,
)
from ..sunapi_extended import enable_recorder_ntp
from ..state_store import StateStore
from ..ui.dependencies import get_state_store, get_store
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
from ..ui.health_dashboard import health_dashboard_context
from ..ui.time_dashboard import time_dashboard_context
from .templates_env import templates
from .validation import parse_recorder_form

router = APIRouter(tags=["web"])
check_logger = get_logger("check")


def _redirect(url: str, toast_type: str | None = None, message: str | None = None) -> Response:
    if toast_type and message:
        qs = urlencode({"toast": toast_type, "msg": message})
        url = f"{url}?{qs}"
    response = RedirectResponse(url=url, status_code=303)
    response.headers["HX-Redirect"] = url
    return response


def _object_names(store: ConfigStore) -> list[str]:
    return sorted({r.object_name for r in store.list_recorders()})


def _metrics_map(state: StateStore):
    return metrics_map_from_list(state.list_recorder_metrics())


def _time_dashboard_ctx(
    store: ConfigStore,
    state: StateStore,
    *,
    compact: bool = False,
    search: str = "",
    problems_only: bool = True,
    show_all_table: bool = False,
    refresh_url: str = "/objects/partials/time-dashboard",
) -> dict:
    from datetime import datetime

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
    )
    ctx["time_refresh_url"] = refresh_url
    ctx["time_server_now"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ctx["time_show_actions"] = True
    return ctx


def _wants_time_dashboard_response(request: Request) -> bool:
    target = request.headers.get("HX-Target", "")
    referer = request.headers.get("HX-Current-URL", "")
    return "#time-dashboard" in target or (
        "/time" in referer and "#health-dashboard" not in target
    )


def _health_dashboard_ctx(
    store: ConfigStore,
    state: StateStore,
    *,
    compact: bool = False,
    search: str = "",
    problems_only: bool = True,
    category_filter: Optional[HealthCategory] = None,
    refresh_url: str = "/objects/partials/health-dashboard",
) -> dict:
    from datetime import datetime

    config = store.load()
    recorders = store.list_recorders()
    metrics = _metrics_map(state)
    ctx = health_dashboard_context(
        recorders,
        metrics,
        config.monitoring,
        ntp_server=config.monitoring.ntp_server or "",
        compact=compact,
        problems_only=problems_only,
        search=search,
        category_filter=category_filter,
    )
    ctx["health_refresh_url"] = refresh_url
    ctx["health_server_now"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    category_filter: Optional[HealthCategory] = None,
    refresh_url: str = "/objects/partials/health-dashboard",
    status_code: int = 200,
) -> HTMLResponse:
    ctx = _health_dashboard_ctx(
        store,
        state,
        compact=compact,
        search=search,
        problems_only=problems_only,
        category_filter=category_filter,
        refresh_url=refresh_url,
    )
    response = templates.TemplateResponse(
        request,
        "partials/health_dashboard.html",
        ctx,
        status_code=status_code,
    )
    if toast_type and toast_message:
        return _attach_toast(response, toast_type, toast_message)
    return response


def _wants_health_dashboard_response(request: Request) -> bool:
    target = request.headers.get("HX-Target", "")
    referer = request.headers.get("HX-Current-URL", "")
    return "#health-dashboard" in target or "/status" in referer


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
    category_filter: Optional[HealthCategory] = None
    if category_raw in CATEGORY_LABELS:
        category_filter = category_raw  # type: ignore[assignment]
    compact = "/recorders" in parsed.path and "/status" not in parsed.path
    if "/status" in parsed.path:
        enc_parts = {
            "search": search,
            "problems_only": "true" if problems_only else "false",
        }
        if category_filter:
            enc_parts["category"] = category_filter
        refresh_url = f"/status/partials/dashboard?{urlencode(enc_parts)}"
    elif compact:
        refresh_url = "/recorders/partials/health-dashboard"
    else:
        refresh_url = "/objects/partials/health-dashboard"
    return {
        "compact": compact,
        "search": search,
        "problems_only": problems_only,
        "category_filter": category_filter,
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
    compact = "/recorders" in parsed.path and "/time" not in parsed.path
    if "/time" in parsed.path:
        enc = urlencode(
            {
                "search": search,
                "problems_only": "true" if problems_only else "false",
            }
        )
        refresh_url = f"/time/partials/dashboard?{enc}"
        show_all = not problems_only
    elif compact:
        refresh_url = "/recorders/partials/time-dashboard"
        show_all = False
    else:
        refresh_url = "/objects/partials/time-dashboard"
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
    refresh_url: str = "/objects/partials/time-dashboard",
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
    if "/recorders" in referer and "/objects" not in referer:
        return "partials/recorder_table_row.html"
    if "/channels" in referer:
        return "partials/recorder_metrics_panel.html"
    return "partials/recorder_row.html"


def _recorder_partial_context(
    recorder,
    metrics,
    *,
    template: str,
    metrics_map: dict | None = None,
) -> dict:
    status = effective_status(recorder, metrics)
    ctx: dict = {"recorder": recorder, "status": status, "metrics": metrics}
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
    return RedirectResponse(url="/objects", status_code=302)


@router.get("/health", include_in_schema=False)
def health() -> dict[str, str]:
    return {"status": "ok", "log_file": str(get_log_file_path())}


@router.get("/objects", response_class=HTMLResponse)
def objects_page(
    request: Request,
    sort: SortMode = "status",
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    recorders = store.list_recorders()
    metrics = _metrics_map(state)
    groups = group_by_object(recorders, "", sort, metrics)
    toast = _toast_from_query(request)
    return templates.TemplateResponse(
        request,
        "objects.html",
        {
            "active_nav": "objects",
            "groups": groups,
            "recorders": recorders,
            "metrics_map": metrics,
            "sort": sort,
            "toast": toast,
            **_health_dashboard_ctx(store, state),
        },
    )


@router.get("/objects/partials/health-dashboard", response_class=HTMLResponse)
def objects_health_dashboard_partial(
    request: Request,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    return _health_dashboard_response(
        request,
        store,
        state,
        refresh_url="/objects/partials/health-dashboard",
    )


@router.get("/objects/partials/time-dashboard", response_class=HTMLResponse)
def objects_time_dashboard_partial(
    request: Request,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    return _time_dashboard_response(
        request,
        store,
        state,
        refresh_url="/objects/partials/time-dashboard",
    )


@router.get("/objects/partials/groups", response_class=HTMLResponse)
def objects_groups_partial(
    request: Request,
    search: str = "",
    sort: SortMode = "status",
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    recorders = store.list_recorders()
    metrics = _metrics_map(state)
    groups = group_by_object(recorders, search, sort, metrics)
    return templates.TemplateResponse(
        request,
        "partials/object_groups.html",
        {"groups": groups, "recorders": recorders, "metrics_map": metrics},
    )


@router.get("/recorders", response_class=HTMLResponse)
def recorders_page(
    request: Request,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    recorders = sorted(
        store.list_recorders(),
        key=lambda r: (r.object_name.lower(), r.host),
    )
    return templates.TemplateResponse(
        request,
        "recorders.html",
        {
            "active_nav": "recorders",
            "recorders": recorders,
            "metrics_map": _metrics_map(state),
            "toast": _toast_from_query(request),
            **_health_dashboard_ctx(
                store,
                state,
                compact=True,
                refresh_url="/recorders/partials/health-dashboard",
            ),
        },
    )


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


@router.get("/time", response_class=HTMLResponse)
def time_page(
    request: Request,
    search: str = "",
    problems_only: str = "true",
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    only_problems = problems_only.lower() not in ("false", "0", "no")
    qs = urlencode({"search": search, "problems_only": "true" if only_problems else "false"})
    return templates.TemplateResponse(
        request,
        "time.html",
        {
            "active_nav": "time",
            "time_search": search,
            "time_problems_only": only_problems,
            "toast": _toast_from_query(request),
            **_time_dashboard_ctx(
                store,
                state,
                search=search,
                problems_only=only_problems,
                show_all_table=not only_problems,
                refresh_url=f"/time/partials/dashboard?{qs}",
            ),
        },
    )


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


@router.get("/status", response_class=HTMLResponse)
def status_page(
    request: Request,
    search: str = "",
    problems_only: str = "true",
    category: str = "",
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    only_problems = problems_only.lower() not in ("false", "0", "no")
    category_filter: Optional[HealthCategory] = None
    if category.strip() in CATEGORY_LABELS:
        category_filter = category.strip()  # type: ignore[assignment]
    enc = {
        "search": search,
        "problems_only": "true" if only_problems else "false",
    }
    if category_filter:
        enc["category"] = category_filter
    qs = urlencode(enc)
    return templates.TemplateResponse(
        request,
        "status.html",
        {
            "active_nav": "status",
            "health_search": search,
            "health_problems_only": only_problems,
            "health_category_filter": category_filter,
            "health_category_options": list(CATEGORY_LABELS.items()),
            "toast": _toast_from_query(request),
            **_health_dashboard_ctx(
                store,
                state,
                search=search,
                problems_only=only_problems,
                category_filter=category_filter,
                refresh_url=f"/status/partials/dashboard?{qs}",
            ),
        },
    )


@router.get("/status/partials/dashboard", response_class=HTMLResponse)
def status_dashboard_partial(
    request: Request,
    search: str = "",
    problems_only: str = "true",
    category: str = "",
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> HTMLResponse:
    only_problems = problems_only.lower() not in ("false", "0", "no")
    category_filter: Optional[HealthCategory] = None
    if category.strip() in CATEGORY_LABELS:
        category_filter = category.strip()  # type: ignore[assignment]
    enc = {
        "search": search,
        "problems_only": "true" if only_problems else "false",
    }
    if category_filter:
        enc["category"] = category_filter
    return _health_dashboard_response(
        request,
        store,
        state,
        search=search,
        problems_only=only_problems,
        category_filter=category_filter,
        refresh_url=f"/status/partials/dashboard?{urlencode(enc)}",
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
    enabled: str = Form("true"),
    store: ConfigStore = Depends(get_store),
) -> Response:
    data, errors = parse_recorder_form(
        object_name, name, host, port, use_https, enabled
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
            enabled=data.enabled,
        )
    except ValidationError as e:
        return _form_validation_error(request, None, store, e)

    store.create_recorder(body)
    return _redirect("/objects", "success", "Регистратор добавлен")


@router.post("/recorders/{recorder_id}", response_class=HTMLResponse)
async def recorder_update(
    request: Request,
    recorder_id: str,
    object_name: str = Form(""),
    name: str = Form(""),
    host: str = Form(""),
    port: str = Form("80"),
    use_https: str = Form("false"),
    enabled: str = Form("true"),
    store: ConfigStore = Depends(get_store),
) -> Response:
    recorder = store.get_recorder(recorder_id)
    if not recorder:
        return HTMLResponse("Не найден", status_code=404)

    data, errors = parse_recorder_form(
        object_name, name, host, port, use_https, enabled
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
            enabled=data.enabled,
        )
    except ValidationError as e:
        return _form_validation_error(request, recorder, store, e)

    store.update_recorder(recorder_id, body)
    return _redirect("/objects", "success", "Регистратор сохранён")


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
    if "/recorders" in referer and "/objects" not in referer:
        return _redirect("/recorders", "success", "Регистратор удалён")
    return _redirect("/objects", "success", "Регистратор удалён")


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
            "extra_enabled": recorder.enabled,
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
        _recorder_partial_context(updated, metrics, template=template),
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

    if not recorder.enabled:
        return HTMLResponse("Регистратор отключён", status_code=400)

    config = store.load()
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
            _recorder_partial_context(recorder, metrics, template=template),
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
        _recorder_partial_context(updated, metrics, template=template),
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


@router.get("/channels", response_class=HTMLResponse)
def channels_page(
    request: Request,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
    health: str = "",
    recorder_id: str = "",
) -> HTMLResponse:
    recorders = store.list_recorders()
    metrics = _metrics_map(state)
    channels = state.list_channels(
        recorder_id=recorder_id or None,
        health=health or None,
    )
    return templates.TemplateResponse(
        request,
        "channels.html",
        {
            "active_nav": "channels",
            "channels": channels,
            "recorders": recorders,
            "recorders_by_id": _recorders_by_id(store),
            "metrics_map": metrics,
            "filter_health": health,
            "filter_recorder": recorder_id,
            "toast": _toast_from_query(request),
        },
    )


@router.get("/history", response_class=HTMLResponse)
def history_page(
    request: Request,
    state: StateStore = Depends(get_state_store),
    store: ConfigStore = Depends(get_store),
    entity_type: str = "",
    entity_id: str = "",
) -> HTMLResponse:
    history = state.list_history(
        entity_type=entity_type or None,
        entity_id=entity_id or None,
        limit=300,
    )
    return templates.TemplateResponse(
        request,
        "history.html",
        {
            "active_nav": "history",
            "history": history,
            "recorders": store.list_recorders(),
            "filter_entity_type": entity_type,
            "filter_entity_id": entity_id,
        },
    )


@router.post("/monitoring/poll-all", response_class=HTMLResponse)
async def monitoring_poll_all(
    request: Request,
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> Response:
    await run_poll_cycle(store, state, include_inventory=False)
    referer = request.headers.get("HX-Current-URL", "")
    if "/status" in referer:
        return _redirect("/status", "success", "Опрос регистраторов завершён")
    if "/time" in referer:
        return _redirect("/time", "success", "Опрос регистраторов завершён")
    if "/recorders" in referer and "/objects" not in referer:
        return _redirect("/recorders", "success", "Опрос регистраторов завершён")
    return _redirect("/objects", "success", "Опрос регистраторов завершён")


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
    store: ConfigStore = Depends(get_store),
    state: StateStore = Depends(get_state_store),
) -> Response:
    await run_inventory_cycle(store, state)
    return _redirect("/channels", "success", "Инвентаризация каналов завершена")


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
    if "/channels" in referer:
        return _redirect("/channels", "success", "Каналы обновлены")
    return _redirect("/objects", "success", "Каналы обновлены")
