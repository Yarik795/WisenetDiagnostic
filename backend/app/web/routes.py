from __future__ import annotations

import json
import time
from typing import Literal, Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from pydantic import ValidationError

from ..config_store import ConfigStore
from ..logging_config import get_log_file_path, get_logger
from ..models import RecorderCreate, RecorderUpdate
from ..monitoring import poll_single_recorder, run_inventory_cycle, run_poll_cycle
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
        },
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
        },
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
    status = effective_status(updated, metrics)
    template = (
        "partials/recorder_table_row.html"
        if "/recorders" in referer and "/objects" not in referer
        else "partials/recorder_row.html"
    )
    duration_ms = round((time.perf_counter() - start) * 1000)
    check_logger.info(
        "check finished",
        extra={
            "event": "check_done",
            "extra_recorder_id": recorder_id,
            "extra_status": outcome_status.value if outcome_status else None,
            "extra_effective_status": status,
            "extra_error": updated.last_error,
            "extra_duration_ms": duration_ms,
            "extra_template": template,
        },
    )

    response = templates.TemplateResponse(
        request,
        template,
        {"recorder": updated, "status": status, "metrics": metrics},
    )
    if outcome_status and outcome_status.value == "online":
        payload = {
            "showToast": {
                "type": "success",
                "message": f"{display_recorder_name(updated)}: доступен",
            }
        }
        response.headers["HX-Trigger"] = json.dumps(payload, ensure_ascii=True)
    elif outcome_status and outcome_status.value == "offline":
        payload = {
            "showToast": {
                "type": "error",
                "message": updated.last_error or "Недоступен",
            }
        }
        response.headers["HX-Trigger"] = json.dumps(payload, ensure_ascii=True)
    return response


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
    return _redirect("/objects", "success", "Опрос регистраторов запущен")


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
