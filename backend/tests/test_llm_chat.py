from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.chat_store import ChatStore
from app.config_store import ConfigStore
from app.llm.orchestrator import ChatOrchestrator
from app.llm.sql_guard import is_safe_select, run_readonly
from app.llm.tools import build_echarts_option
from app.models import AppConfig, LLMSettings
from app.state_store import StateStore
from app.ui.dependencies import get_chat_store, get_state_store, get_store


def test_is_safe_select_accepts_select():
    assert is_safe_select("SELECT 1")
    assert is_safe_select("WITH t AS (SELECT 1 AS x) SELECT * FROM t")


def test_is_safe_select_rejects_write():
    assert not is_safe_select("DELETE FROM channels")
    assert not is_safe_select("SELECT 1; DROP TABLE channels")


def test_run_readonly(tmp_path):
    db = tmp_path / "test.db"
    import sqlite3

    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE t (id INTEGER, name TEXT)")
    conn.execute("INSERT INTO t VALUES (1, 'a')")
    conn.commit()
    conn.close()

    cols, rows, count, truncated = run_readonly(db, "SELECT id, name FROM t", max_rows=10)
    assert cols == ["id", "name"]
    assert rows == [{"id": 1, "name": "a"}]
    assert count == 1
    assert not truncated


def test_build_echarts_bar():
    table = {
        "columns": ["status", "cnt"],
        "rows": [
            {"status": "ok", "cnt": 10},
            {"status": "error", "cnt": 2},
        ],
    }
    option = build_echarts_option(
        {"chart_type": "bar", "x": "status", "y": ["cnt"], "title": "Test"},
        table,
    )
    assert option["series"][0]["type"] == "bar"
    assert option["xAxis"]["data"] == ["ok", "error"]


def test_build_echarts_rejects_unknown_columns():
    table = {"columns": ["status", "cnt"], "rows": [{"status": "ok", "cnt": 1}]}
    option = build_echarts_option(
        {"chart_type": "bar", "x": "missing", "y": ["cnt"], "title": "T"},
        table,
    )
    assert option == {}


def test_build_echarts_rejects_all_null_y():
    table = {"columns": ["status", "cnt"], "rows": [{"status": "ok", "cnt": 0}]}
    option = build_echarts_option(
        {"chart_type": "bar", "x": "status", "y": ["cnt"], "title": "T"},
        table,
    )
    assert option == {}


def test_build_echarts_adds_datazoom_for_many_categories():
    rows = [{"label": f"c{i}", "val": i} for i in range(20)]
    table = {"columns": ["label", "val"], "rows": rows}
    option = build_echarts_option(
        {"chart_type": "bar", "x": "label", "y": ["val"], "title": "Many"},
        table,
    )
    assert "dataZoom" in option


def test_build_echarts_pie_aggregates_slices():
    rows = [{"kind": f"k{i}", "n": i} for i in range(15)]
    table = {"columns": ["kind", "n"], "rows": rows}
    option = build_echarts_option(
        {"chart_type": "pie", "x": "kind", "y": ["n"], "title": "Pie"},
        table,
    )
    names = [d["name"] for d in option["series"][0]["data"]]
    assert "Прочие" in names
    assert len(names) == 10


def test_orchestrator_iteration_limit_chart_message():
    orch = ChatOrchestrator(settings=LLMSettings(enabled=True, api_key="x", max_iterations=1))
    with patch.object(orch.llm, "chat") as mock_chat:
        msg = MagicMock()
        msg.tool_calls = [MagicMock()]
        msg.tool_calls[0].function.name = "run_sql"
        msg.tool_calls[0].function.arguments = '{"query": "SELECT 1"}'
        msg.tool_calls[0].id = "c1"
        msg.model_dump.return_value = {"role": "assistant", "tool_calls": []}
        mock_chat.return_value.choices = [MagicMock(message=msg)]
        with patch.object(orch, "_execute_tool", return_value=("ok", {"columns": ["x"], "rows": []}, None, "SELECT 1")):
            result = orch.run([], "Построй график bar по данным")
    assert "make_chart" in result.text


@pytest.fixture
def chat_client(tmp_path: Path):
    from fastapi.testclient import TestClient

    from app.main import app

    config_path = tmp_path / "config.json"
    store = ConfigStore(path=config_path)
    store.save(AppConfig(llm=LLMSettings(enabled=True, api_key="test-key")))
    db_path = tmp_path / "monitoring.db"
    state = StateStore(path=db_path)
    state.init_db()
    chat = ChatStore(path=db_path)
    chat.init_db()

    app.dependency_overrides[get_store] = lambda: store
    app.dependency_overrides[get_state_store] = lambda: state
    app.dependency_overrides[get_chat_store] = lambda: chat
    yield TestClient(app), chat
    app.dependency_overrides.clear()


def test_ai_chat_redirects_to_session(chat_client):
    client, chat = chat_client
    session = chat.create_session()
    chat.append_message(session.id, "user", "hi")
    chat.append_message(session.id, "assistant", "hello")

    r = client.get("/ai-chat", follow_redirects=False)
    assert r.status_code == 303
    assert f"session_id={session.id}" in r.headers["location"]


def test_ai_chat_stream_requires_message_id(chat_client):
    client, chat = chat_client
    session = chat.create_session()
    user = chat.append_message(session.id, "user", "test")

    def fake_stream(history, user_text):
        yield {"type": "done", "data": {"text": "ok"}}

    with patch.object(ChatOrchestrator, "run_stream", side_effect=lambda h, t: fake_stream(h, t)):
        r = client.get(f"/ai-chat/stream?session_id={session.id}&message_id={user.id}")
    assert r.status_code == 200
    body = "".join(r.iter_text())
    assert "event:" in body
    assert "done" in body


def test_ai_chat_stream_rejects_answered_message(chat_client):
    client, chat = chat_client
    session = chat.create_session()
    user = chat.append_message(session.id, "user", "test")
    chat.append_message(session.id, "assistant", "done")

    r = client.get(f"/ai-chat/stream?session_id={session.id}&message_id={user.id}")
    body = "".join(r.iter_text())
    assert "error" in body
    assert "уже есть ответ" in body


def test_chat_store_list_sessions_with_messages(chat_client):
    _, chat = chat_client
    empty = chat.create_session()
    full = chat.create_session()
    chat.append_message(full.id, "user", "q")
    sessions = chat.list_sessions_with_messages()
    ids = {s.id for s in sessions}
    assert full.id in ids
    assert empty.id not in ids


def test_chat_store_delete_empty_sessions(chat_client):
    _, chat = chat_client
    empty = chat.create_session()
    full = chat.create_session()
    chat.append_message(full.id, "user", "q")
    removed = chat.delete_empty_sessions()
    assert removed >= 1
    assert chat.get_session(empty.id) is None
    assert chat.get_session(full.id) is not None
