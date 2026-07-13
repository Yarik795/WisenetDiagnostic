"""Тесты UI-контекста отчёта «Анализ повторных РВР»."""

from __future__ import annotations

from app.ui.rvr_repeat_dashboard import (
    build_kind_cells,
    build_rvr_matrix_rows,
    kind_cell_status,
    row_aggregate_status,
)


def test_kind_cell_status_absolute() -> None:
    assert kind_cell_status(0) == "na"
    assert kind_cell_status(1) == "neutral"
    assert kind_cell_status(2) == "warn"
    assert kind_cell_status(3) == "error"
    assert kind_cell_status(10) == "error"


def test_kind_cell_status_boost() -> None:
    assert kind_cell_status(2, boost=True) == "error"
    assert kind_cell_status(3, boost=True) == "error"
    assert kind_cell_status(1, boost=True) == "neutral"


def test_row_aggregate_status() -> None:
    assert row_aggregate_status(0) == "ok"
    assert row_aggregate_status(1) == "ok"
    assert row_aggregate_status(2) == "warn"
    assert row_aggregate_status(6) == "warn"
    assert row_aggregate_status(7) == "error"


def test_build_kind_cells_relative_boost() -> None:
    by_kind = {
        "САПС": [{"num": "1", "date": "01.01.2026", "desc": "a"}] * 2,
        "СКУД": [{"num": "2", "date": "02.01.2026", "desc": "b"}] * 4,
    }
    cells = build_kind_cells(by_kind, ["САПС", "СКУД", "ТСВ"])
    by_name = {c["kind"]: c for c in cells}

    assert by_name["САПС"]["count"] == 2
    assert by_name["САПС"]["status"] == "warn"
    assert by_name["СКУД"]["count"] == 4
    assert by_name["СКУД"]["status"] == "error"
    assert by_name["ТСВ"]["count"] == 0
    assert by_name["ТСВ"]["status"] == "na"


def test_build_rvr_matrix_rows_preserves_entries() -> None:
    groups = [
        {
            "address": "ул. Тестовая, 1",
            "object_type": "АДЗ",
            "repeat_count": 2,
            "by_kind": {
                "СОТС": [
                    {"num": "100", "date": "01.06.2026", "desc": "проблема 1"},
                    {"num": "101", "date": "02.06.2026", "desc": "проблема 2"},
                ],
            },
            "analysis": None,
        },
    ]
    rows = build_rvr_matrix_rows(groups, ["СОТС", "ТСВ"])
    assert len(rows) == 1
    row = rows[0]
    assert row["address"] == "ул. Тестовая, 1"
    assert row["repeat_count"] == 2
    assert row["aggregate_status"] == "warn"
    assert row["row_id"].startswith("rvr-")

    sots = next(c for c in row["cells"] if c["kind"] == "СОТС")
    assert len(sots["entries"]) == 2
    assert sots["entries"][0]["num"] == "100"
