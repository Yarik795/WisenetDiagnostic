"""Тесты импорта данных заявок ПП."""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime
from pathlib import Path

import pytest
from openpyxl import Workbook

from app.config_store import ConfigStore
from app.data_sources import (
    REQUESTS_SOURCE,
    RunnerDeps,
    copy_to_storage,
    load_source,
)
from app.pp_import import (
    COL_AMOUNT,
    COL_COMPLETED_AT,
    COL_REQUEST_NUMBER,
    PPRequestRow,
    build_col_index,
    import_pp_requests_xlsx,
    is_excluded_pp_status,
    parse_dt,
    parse_money,
)
from app.state_store import StateStore

PP_HEADERS = (
    "Заявка №",
    "Статус",
    "№ заявки ДРУГ",
    "Дата создания (UTC)",
    "Фактическая дата выполнения (UTC)",
    "ФИО заказчика",
    "Территориальный банк",
    "Вид работ",
    "Статус акта",
    "Сумма с НДС",
    "Гарантийная заявка",
    "Адрес",
    "Вид системы безопасности",
    "В лимите",
)


def _write_pp_xlsx(
    path: Path,
    rows: list[tuple],
    *,
    headers: tuple[str, ...] = PP_HEADERS,
) -> None:
    wb = Workbook()
    ws = wb.active
    ws.append(list(headers))
    for row in rows:
        ws.append(list(row))
    wb.save(path)


def test_parse_money_variants() -> None:
    assert parse_money(None) == 0.0
    assert parse_money("") == 0.0
    assert parse_money(47497125.32) == 47497125.32
    assert parse_money("47497125,32") == 47497125.32
    assert parse_money(" 1 234,5 ") == 1234.5


def test_parse_dt_variants() -> None:
    assert parse_dt(None) is None
    assert parse_dt("") is None
    dt = datetime(2025, 3, 21, 6, 24, 14)
    iso = parse_dt(dt)
    assert iso is not None
    assert iso.startswith("2025-03-21T06:24:14")
    assert parse_dt("21.03.2025  6:24:14") == iso
    assert parse_dt("22.06.2026 11:25") is not None
    assert parse_dt(date.today()) is not None


def test_build_col_index_requires_columns() -> None:
    with pytest.raises(ValueError, match="отсутствуют колонки"):
        build_col_index(["Заявка №", "Статус"])


def test_is_excluded_pp_status() -> None:
    assert is_excluded_pp_status("Отклонена")
    assert is_excluded_pp_status("Отозвана ДБ")
    assert is_excluded_pp_status("Отозвана ВК")
    assert not is_excluded_pp_status("Отправлена подрядчику")
    assert not is_excluded_pp_status("")


def test_import_pp_requests_skips_rejected_and_withdrawn(tmp_path: Path) -> None:
    xlsx = tmp_path / "requests.xlsx"
    _write_pp_xlsx(
        xlsx,
        [
            (
                "100",
                "Отправлена подрядчику",
                "SD1",
                None,
                date.today(),
                "Иванов",
                "ТБ",
                "РВР",
                "",
                100.0,
                "Нет",
                "А1",
                "СОТС",
                "",
            ),
            (
                "200",
                "Отклонена",
                "SD2",
                None,
                date.today(),
                "Петров",
                "ТБ",
                "РВР",
                "",
                200.0,
                "Нет",
                "А2",
                "СОТС",
                "",
            ),
            (
                "300",
                "Отозвана ДБ",
                "SD3",
                None,
                date.today(),
                "Сидоров",
                "ТБ",
                "РВР",
                "",
                300.0,
                "Нет",
                "А3",
                "СОТС",
                "",
            ),
        ],
    )

    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    count = import_pp_requests_xlsx(xlsx, state)
    assert count == 1
    assert state.count_pp_requests() == 1

    with sqlite3.connect(state.path) as conn:
        numbers = {
            row[0]
            for row in conn.execute("SELECT request_number FROM pp_requests").fetchall()
        }
    assert numbers == {"100"}


def test_import_pp_requests_xlsx_parses_rows(tmp_path: Path) -> None:
    xlsx = tmp_path / "requests.xlsx"
    _write_pp_xlsx(
        xlsx,
        [
            (
                "14049579",
                "Отправлена подрядчику",
                "SD240833781",
                "22.06.2026 11:25",
                None,
                "Олег Юрьевич К",
                "Московский банк (3800)",
                "РВР",
                "",
                47497125.32,
                "Нет",
                "г Москва, ул Череповецкая, 20",
                "СОТС",
                "",
            ),
            (
                "14049536",
                "Отправлена подрядчику",
                "SD240803586",
                datetime(2026, 6, 22, 11, 16),
                date.today(),
                "Наталия Анатольевна Ж",
                "Московский банк (3800)",
                "РВР",
                "Проект",
                "1234,56",
                "Нет",
                "г Москва",
                "ТСВ",
                "Московский банк",
            ),
        ],
    )

    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()

    count = import_pp_requests_xlsx(xlsx, state)
    assert count == 2
    assert state.count_pp_requests() == 2

    with sqlite3.connect(state.path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM pp_requests WHERE request_number = ?",
            ("14049579",),
        ).fetchone()
    assert row is not None
    assert row["drug_number"] == "SD240833781"
    assert row["amount_vat"] == pytest.approx(47497125.32)
    assert row["completed_at"] is None
    assert row["security_system_type"] == "СОТС"
    raw = json.loads(row["raw_json"])
    assert raw["Заявка №"] == "14049579"
    assert raw["Адрес"] == "г Москва, ул Череповецкая, 20"


def test_import_pp_requests_duplicate_replaces_last(tmp_path: Path) -> None:
    xlsx = tmp_path / "dup.xlsx"
    _write_pp_xlsx(
        xlsx,
        [
            (
                "100",
                "Статус 1",
                "SD1",
                None,
                date.today(),
                "Иванов",
                "ТБ",
                "РВР",
                "",
                100.0,
                "Нет",
                "А1",
                "СОТС",
                "",
            ),
            (
                "100",
                "Статус 2",
                "SD2",
                None,
                date.today(),
                "Петров",
                "ТБ",
                "РВР",
                "",
                200.0,
                "Нет",
                "А2",
                "ТСВ",
                "",
            ),
        ],
    )

    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    count = import_pp_requests_xlsx(xlsx, state)
    assert count == 2
    assert state.count_pp_requests() == 1

    with sqlite3.connect(state.path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT status, amount_vat FROM pp_requests WHERE request_number = ?",
            ("100",),
        ).fetchone()
    assert row["status"] == "Статус 2"
    assert row["amount_vat"] == pytest.approx(200.0)


def test_import_pp_requests_missing_column(tmp_path: Path) -> None:
    xlsx = tmp_path / "bad.xlsx"
    _write_pp_xlsx(
        xlsx,
        [("1", "2")],
        headers=("Заявка №", "Статус"),
    )

    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()

    with pytest.raises(ValueError, match="отсутствуют колонки"):
        import_pp_requests_xlsx(xlsx, state)


def test_pp_requests_sql_aggregate_without_excel(tmp_path: Path) -> None:
    xlsx = tmp_path / "requests.xlsx"
    _write_pp_xlsx(
        xlsx,
        [
            (
                "1",
                "Статус",
                "SD1",
                None,
                date.today(),
                "A",
                "Московский банк (3800)",
                "РВР",
                "",
                1000.0,
                "Нет",
                "addr",
                "СОТС",
                "",
            ),
            (
                "2",
                "Статус",
                "SD2",
                None,
                date.today(),
                "B",
                "Московский банк (3800)",
                "Модернизация",
                "",
                500.0,
                "Нет",
                "addr",
                "ТСВ",
                "",
            ),
        ],
    )

    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    import_pp_requests_xlsx(xlsx, state)

    with sqlite3.connect(state.path) as conn:
        rows = conn.execute(
            """
            SELECT work_type, COUNT(*) AS cnt, SUM(amount_vat) AS total
            FROM pp_requests
            GROUP BY work_type
            ORDER BY work_type
            """
        ).fetchall()

    assert len(rows) == 2
    assert rows[0][0] == "Модернизация"
    assert rows[0][1] == 1
    assert rows[0][2] == pytest.approx(500.0)


def test_load_source_requests_skip_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_dir = tmp_path / "inputData"
    uploads = tmp_path / "uploads"
    input_dir.mkdir()
    uploads.mkdir()
    monkeypatch.setattr("app.data_sources.INPUT_DATA_DIR", input_dir)
    monkeypatch.setattr("app.data_sources.UPLOADS_DIR", uploads)

    source = input_dir / "Заявки-1.xlsx"
    _write_pp_xlsx(
        source,
        [
            (
                "14049579",
                "Отправлена подрядчику",
                "SD240833781",
                "22.06.2026 11:25",
                date.today(),
                "Олег Юрьевич К",
                "Московский банк (3800)",
                "Модернизация",
                "Проект",
                100.0,
                "Нет",
                "addr",
                "СОТС",
                "",
            ),
        ],
    )
    copy_to_storage(REQUESTS_SOURCE, source)

    from app.cashflow_report import save_report_artifact

    monkeypatch.setattr(
        "app.cashflow_report.REPORTS_DIR",
        tmp_path / "reports",
    )
    (tmp_path / "reports").mkdir()
    save_report_artifact({"generated_at": "2026-01-01T00:00:00+00:00", "row_count": 1})

    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    with state.replace_pp_requests() as session:
        session.write_batch(
            [
                PPRequestRow(
                    request_number="14049579",
                    status="Отправлена подрядчику",
                    drug_number="SD240833781",
                    created_at=None,
                    completed_at=parse_dt(date.today()),
                    customer_fio="Олег Юрьевич К",
                    tb="Московский банк (3800)",
                    work_type="Модернизация",
                    act_status="Проект",
                    amount_vat=100.0,
                    warranty="Нет",
                    address="addr",
                    security_system_type="СОТС",
                    in_limit="",
                    raw_json="{}",
                    source_row=2,
                )
            ]
        )

    store = ConfigStore(path=tmp_path / "config.json")
    deps = RunnerDeps(store=store, state=state)

    result = load_source("requests", deps)
    assert result.ok
    assert result.message == "Новых данных нет"
    assert not result.changed


def test_load_source_requests_imports_to_db(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_dir = tmp_path / "inputData"
    uploads = tmp_path / "uploads"
    reports = tmp_path / "reports"
    input_dir.mkdir()
    uploads.mkdir()
    reports.mkdir()
    monkeypatch.setattr("app.data_sources.INPUT_DATA_DIR", input_dir)
    monkeypatch.setattr("app.data_sources.UPLOADS_DIR", uploads)
    monkeypatch.setattr("app.cashflow_report.REPORTS_DIR", reports)

    source = input_dir / "Выгрузка Заявки ПП.xlsx"
    _write_pp_xlsx(
        source,
        [
            (
                "14049579",
                "На согласовании",
                "SD240833781",
                "22.06.2026 11:25",
                date.today(),
                "Зайцев Иван",
                "38 Московский банк",
                "Модернизация",
                "Проект",
                10000.5,
                "Нет",
                "г Москва",
                "СОТС",
                "Московский банк",
            ),
        ],
    )

    store = ConfigStore(path=tmp_path / "config.json")
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    deps = RunnerDeps(store=store, state=state)

    result = load_source("requests", deps)
    assert result.ok
    assert state.count_pp_requests() == 1
    assert "1 строк" in result.message

    with sqlite3.connect(state.path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT raw_json FROM pp_requests WHERE request_number = ?",
            ("14049579",),
        ).fetchone()
    raw = json.loads(row["raw_json"])
    assert COL_REQUEST_NUMBER in raw
    assert COL_AMOUNT in raw
    assert COL_COMPLETED_AT in raw
