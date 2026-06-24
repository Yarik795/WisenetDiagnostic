from __future__ import annotations

import json
from typing import Any, Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse

from ..chat_store import ChatMessageRow, ChatStore
from ..config_store import ConfigStore
from ..display_time import format_for_display
from ..llm.orchestrator import ChatOrchestrator
from ..state_store import StateStore
from ..ui.dependencies import get_chat_store, get_state_store, get_store
from .templates_env import templates

router = APIRouter(tags=["ai-chat"])


def _message_view(msg: ChatMessageRow) -> dict[str, Any]:
    chart = None
    table = None
    if msg.chart_json:
        try:
            chart = json.loads(msg.chart_json)
        except json.JSONDecodeError:
            chart = None
    if msg.table_json:
        try:
            table = json.loads(msg.table_json)
        except json.JSONDecodeError:
            table = None
    return {
        "id": msg.id,
        "role": msg.role,
        "content": msg.content,
        "sql": msg.sql,
        "chart": chart,
        "table": table,
        "created_at": format_for_display(msg.created_at, "%d.%m.%Y %H:%M"),
        "pending": False,
    }


def _sse_error(text: str) -> str:
    payload = json.dumps({"text": text}, ensure_ascii=False)
    return f"event: error\ndata: {payload}\n\n"


@router.get("/ai-chat", response_class=HTMLResponse, response_model=None)
def ai_chat_page(
    request: Request,
    session_id: Optional[str] = None,
    chat_store: ChatStore = Depends(get_chat_store),
    store: ConfigStore = Depends(get_store),
) -> HTMLResponse | RedirectResponse:
    if session_id is None:
        latest = chat_store.get_latest_session()
        if latest:
            return RedirectResponse(
                url=f"/ai-chat?session_id={latest.id}",
                status_code=303,
            )
        session = chat_store.create_session()
        return RedirectResponse(
            url=f"/ai-chat?session_id={session.id}",
            status_code=303,
        )

    session = chat_store.get_session(session_id)
    if session is None:
        return RedirectResponse(url="/ai-chat", status_code=303)

    messages = chat_store.list_messages(session_id)
    llm_cfg = store.load().llm
    return templates.TemplateResponse(
        request,
        "ai_chat.html",
        {
            "active_nav": "ai_chat",
            "session_id": session_id,
            "sessions": chat_store.list_sessions_with_messages(),
            "messages": [_message_view(m) for m in messages],
            "llm_enabled": llm_cfg.enabled,
            "llm_configured": bool(llm_cfg.api_key),
        },
    )


@router.post("/ai-chat/session")
def ai_chat_new_session(
    chat_store: ChatStore = Depends(get_chat_store),
) -> RedirectResponse:
    session = chat_store.create_session()
    return RedirectResponse(url=f"/ai-chat?session_id={session.id}", status_code=303)


@router.post("/ai-chat/message", response_class=HTMLResponse)
def ai_chat_message(
    request: Request,
    session_id: str = Form(...),
    text: str = Form(...),
    chat_store: ChatStore = Depends(get_chat_store),
) -> HTMLResponse:
    text = text.strip()
    if not text:
        return HTMLResponse("", status_code=400)

    session = chat_store.get_session(session_id)
    if session is None:
        return HTMLResponse("Сессия не найдена", status_code=404)

    user_msg = chat_store.append_message(session_id, "user", text)

    return templates.TemplateResponse(
        request,
        "partials/ai_chat_turn.html",
        {
            "session_id": session_id,
            "user_message": _message_view(user_msg),
            "stream_url": (
                f"/ai-chat/stream?session_id={session_id}&message_id={user_msg.id}"
            ),
        },
    )


@router.get("/ai-chat/stream")
def ai_chat_stream(
    session_id: str,
    message_id: int,
    chat_store: ChatStore = Depends(get_chat_store),
    state: StateStore = Depends(get_state_store),
    store: ConfigStore = Depends(get_store),
) -> StreamingResponse:
    user_msg = chat_store.get_message(message_id)
    if user_msg is None or user_msg.session_id != session_id:
        return StreamingResponse(
            iter([_sse_error("Сообщение не найдено")]),
            media_type="text/event-stream",
        )
    if user_msg.role != "user":
        return StreamingResponse(
            iter([_sse_error("Ожидалось сообщение пользователя")]),
            media_type="text/event-stream",
        )
    if chat_store.has_assistant_reply_after(session_id, message_id):
        return StreamingResponse(
            iter([_sse_error("На это сообщение уже есть ответ")]),
            media_type="text/event-stream",
        )

    messages = chat_store.list_messages(session_id)
    history = [
        {"role": m.role, "content": m.content}
        for m in messages
        if m.id < message_id and m.role in ("user", "assistant")
    ]
    user_text = user_msg.content
    config = store.load()
    orchestrator = ChatOrchestrator(
        state_store=state,
        config_store=store,
        settings=config.llm,
    )

    def event_generator():
        final: dict[str, Any] = {}
        try:
            for event in orchestrator.run_stream(history, user_text):
                event_type = event["type"]
                data = event.get("data", {})
                if event_type == "done":
                    final = data if isinstance(data, dict) else {}
                payload = json.dumps(data, ensure_ascii=False, default=str)
                yield f"event: {event_type}\ndata: {payload}\n\n"

            if final:
                chart_json = (
                    json.dumps(final.get("chart"), ensure_ascii=False)
                    if final.get("chart")
                    else None
                )
                table_json = (
                    json.dumps(final.get("table"), ensure_ascii=False, default=str)
                    if final.get("table")
                    else None
                )
                chat_store.append_message(
                    session_id,
                    "assistant",
                    final.get("text", ""),
                    sql=final.get("sql"),
                    chart_json=chart_json,
                    table_json=table_json,
                )
                session = chat_store.get_session(session_id)
                if session and session.title == "Новый чат":
                    title = user_text[:60] + ("…" if len(user_text) > 60 else "")
                    chat_store.update_session_title(session_id, title)
        except Exception as exc:
            yield _sse_error(f"Ошибка: {exc}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
