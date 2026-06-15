"""Тесты импорта данных Naumen."""

from __future__ import annotations

from pathlib import Path

import pytest
from openpyxl import Workbook

from app.config_store import ConfigStore
from app.data_sources import (
    NAUMEN_SOURCE,
    RunnerDeps,
    copy_to_storage,
    find_latest_source_file,
    load_source,
)
from app.naumen_import import (
    COL_COST,
    COL_DESCRIPTION,
    COL_EXTERNAL_ID,
    COL_NUMBER,
    COL_SBERDRUG,
    NaumenRow,
    build_col_index,
    import_naumen_xlsx,
    parse_cost,
)
from app.state_store import StateStore

NAUMEN_HEADERS = (
    COL_EXTERNAL_ID,
    COL_NUMBER,
    COL_COST,
    COL_SBERDRUG,
    COL_DESCRIPTION,
)


def _write_naumen_xlsx(
    path: Path,
    rows: list[tuple],
    *,
    headers: tuple[str, ...] = NAUMEN_HEADERS,
) -> None:
    wb = Workbook()
    ws = wb.active
    ws.append(list(headers))
    for row in rows:
        ws.append(list(row))
    wb.save(path)


def test_parse_cost_variants() -> None:
    assert parse_cost(None) == 0.0
    assert parse_cost("") == 0.0
    assert parse_cost(0) == 0.0
    assert parse_cost("29837,61") == 29837.61
    assert parse_cost(" 1 234,5 ") == 1234.5


def test_build_col_index_requires_columns() -> None:
    with pytest.raises(ValueError, match="отсутствуют колонки"):
        build_col_index(["Номер", "Описание"])


def test_import_naumen_xlsx_parses_rows(tmp_path: Path) -> None:
    xlsx = tmp_path / "naumen_all.xlsx"
    _write_naumen_xlsx(
        xlsx,
        [
            ("000011006370", "156029", "29837,61", "SD198350794", "Описание заявки"),
            ("000011015245", "168666", "", "SD198579378", "Без стоимости"),
        ],
    )

    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()

    count = import_naumen_xlsx(xlsx, state)
    assert count == 2
    assert state.count_naumen_records() == 2


def test_find_latest_source_file_naumen_marker(tmp_path: Path) -> None:
    wrong = tmp_path / "other.xlsx"
    right = tmp_path / "naumen_all.xlsx"
    _write_naumen_xlsx(wrong, [])
    _write_naumen_xlsx(right, [])

    found = find_latest_source_file(NAUMEN_SOURCE, tmp_path)
    assert found == right


def test_load_source_naumen_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_dir = tmp_path / "inputData"
    uploads = tmp_path / "uploads"
    input_dir.mkdir()
    uploads.mkdir()
    monkeypatch.setattr("app.data_sources.INPUT_DATA_DIR", input_dir)
    monkeypatch.setattr("app.data_sources.UPLOADS_DIR", uploads)

    source = input_dir / "naumen_all.xlsx"
    _write_naumen_xlsx(
        source,
        [("000011006370", "156029", 0, "SD198350794", "Тест")],
    )

    store = ConfigStore(path=tmp_path / "config.json")
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    deps = RunnerDeps(store=store, state=state)

    result = load_source("naumen", deps)
    assert result.ok
    assert result.record_count == 1
    assert "1 строк" in result.message
    assert state.count_naumen_records() == 1


def test_load_source_naumen_skip_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_dir = tmp_path / "inputData"
    uploads = tmp_path / "uploads"
    input_dir.mkdir()
    uploads.mkdir()
    monkeypatch.setattr("app.data_sources.INPUT_DATA_DIR", input_dir)
    monkeypatch.setattr("app.data_sources.UPLOADS_DIR", uploads)

    source = input_dir / "naumen_all.xlsx"
    _write_naumen_xlsx(
        source,
        [("000011006370", "156029", 0, "SD198350794", "Тест")],
    )
    copy_to_storage(NAUMEN_SOURCE, source)

    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    with state.replace_naumen_records() as session:
        session.write_batch(
            [
                NaumenRow(
                    external_id="000011006370",
                    number="156029",
                    cost=0.0,
                    sberdrug_number="SD198350794",
                    description="Тест",
                    source_row=2,
                )
            ]
        )

    store = ConfigStore(path=tmp_path / "config.json")
    deps = RunnerDeps(store=store, state=state)

    result = load_source("naumen", deps)
    assert result.ok
    assert result.message == "Новых данных нет"
    assert not result.changed


def test_import_naumen_xlsx_missing_column(tmp_path: Path) -> None:
    xlsx = tmp_path / "bad.xlsx"
    _write_naumen_xlsx(
        xlsx,
        [("1", "2", "3", "4", "5")],
        headers=(COL_NUMBER, COL_DESCRIPTION, "A", "B", "C"),
    )

    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()

    with pytest.raises(ValueError, match="отсутствуют колонки"):
        import_naumen_xlsx(xlsx, state)


def test_naumen_cost_by_sberdrug_first_nonzero(tmp_path: Path) -> None:
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    with state.replace_naumen_records() as session:
        session.write_batch(
            [
                NaumenRow(
                    external_id="1",
                    number="100",
                    cost=0.0,
                    sberdrug_number="SD111",
                    description="zero",
                    source_row=2,
                ),
                NaumenRow(
                    external_id="2",
                    number="101",
                    cost=500.5,
                    sberdrug_number="SD111",
                    description="nonzero",
                    source_row=3,
                ),
                NaumenRow(
                    external_id="3",
                    number="102",
                    cost=999.0,
                    sberdrug_number="SD222",
                    description="other",
                    source_row=4,
                ),
            ]
        )

    cost_map = state.naumen_cost_by_sberdrug()
    assert cost_map == {"SD111": 500.5, "SD222": 999.0}
