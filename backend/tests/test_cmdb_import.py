"""Тесты импорта CMDB в SQLite."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from openpyxl import Workbook

from app.cmdb_import import import_cmdb_xlsx
from app.state_store import StateStore

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
from cmdb_reader import (  # noqa: E402
    FUNCTIONAL_TYPE_AUX,
    FUNCTIONAL_TYPE_CAMERA,
    FUNCTIONAL_TYPE_VIDEO,
)


def _grid_with_data(*data_rows: list) -> list[list]:
    return [
        ["описание", "полей"],
        [
            "Внешний ID",
            "Тип",
            "IP",
            "MAC",
            "Название",
            "Адрес",
            "Название площадки",
            "Примечание",
            "Сегмент сети",
            "Домен",
            "Логин пользователя",
            "Имя ОСи",
            "Имя билда",
            "Дата установки ОСи",
            "Серийный номер",
            "Производитель устройства",
            "Модель устройства",
            "Список кодов обновления Windows",
            "Маска подсети",
            "Установленное ПО",
            "Открытые порты",
            "Тип порта",
            "Владелец экземпляра",
            "Функциональный тип",
        ],
        *data_rows,
    ]


def _write_cmdb_xlsx(path: Path, grid: list[list]) -> None:
    wb = Workbook()
    ws = wb.active
    for row in grid:
        ws.append(row)
    wb.save(path)


@pytest.fixture
def state(tmp_path: Path) -> StateStore:
    db = StateStore(path=tmp_path / "monitoring.db")
    db.init_db()
    return db


def test_import_cmdb_replaces_records(state: StateStore, tmp_path: Path) -> None:
    grid = _grid_with_data(
        [
            "1",
            "Оборудование ТСО",
            "10.1.1.1",
            "AA:BB:CC:DD:EE:01",
            "",
            "Объект 1",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "Hanwha",
            "HRX-1620",
            "",
            "",
            "",
            "",
            "",
            "",
            FUNCTIONAL_TYPE_VIDEO,
        ],
        [
            "2",
            "Оборудование ТСО",
            "10.1.1.2",
            "",
            "",
            "Объект 2",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "Hanwha",
            "QNO-6010R",
            "",
            "",
            "",
            "",
            "",
            "",
            FUNCTIONAL_TYPE_CAMERA,
        ],
    )
    path = tmp_path / "cmdb.xlsx"
    _write_cmdb_xlsx(path, grid)

    count = import_cmdb_xlsx(path, state)
    assert count == 2
    assert state.count_cmdb_records() == 2

    with state._connect() as conn:
        row = conn.execute(
            "SELECT device_kind, model_name FROM cmdb_records WHERE host = ?",
            ("10.1.1.1",),
        ).fetchone()
    assert row["device_kind"] == "tsv"
    assert row["model_name"] == "HRX-1620"

    with state._connect() as conn:
        row = conn.execute(
            "SELECT device_kind, functional_type FROM cmdb_records WHERE host = ?",
            ("10.1.1.2",),
        ).fetchone()
    assert row["device_kind"] is None
    assert row["functional_type"] == FUNCTIONAL_TYPE_CAMERA


def test_import_cmdb_full_replace(state: StateStore, tmp_path: Path) -> None:
    path = tmp_path / "cmdb.xlsx"
    grid1 = _grid_with_data(
        [
            "1",
            "Оборудование ТСО",
            "10.1.1.1",
            "",
            "",
            "Объект",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "Hanwha",
            "NVR",
            "",
            "",
            "",
            "",
            "",
            "",
            FUNCTIONAL_TYPE_VIDEO,
        ],
    )
    _write_cmdb_xlsx(path, grid1)
    import_cmdb_xlsx(path, state)
    assert state.count_cmdb_records() == 1

    grid2 = _grid_with_data(
        [
            "2",
            "Оборудование ТСО",
            "10.2.2.2",
            "",
            "",
            "Другой",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "Generic",
            "UPS",
            "",
            "",
            "",
            "",
            "",
            "",
            FUNCTIONAL_TYPE_AUX,
        ],
    )
    _write_cmdb_xlsx(path, grid2)
    import_cmdb_xlsx(path, state)
    assert state.count_cmdb_records() == 1

    with state._connect() as conn:
        row = conn.execute(
            "SELECT host, functional_type FROM cmdb_records"
        ).fetchone()
    assert row["host"] == "10.2.2.2"
    assert row["functional_type"] == FUNCTIONAL_TYPE_AUX
