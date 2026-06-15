from __future__ import annotations

import pytest

from app.llm.sql_guard import is_safe_select, run_readonly
from app.llm.tools import build_echarts_option


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
        "rows": [
            {"status": "ok", "cnt": 10},
            {"status": "error", "cnt": 2},
        ]
    }
    option = build_echarts_option(
        {"chart_type": "bar", "x": "status", "y": ["cnt"], "title": "Test"},
        table,
    )
    assert option["series"][0]["type"] == "bar"
    assert option["xAxis"]["data"] == ["ok", "error"]
