"""Тесты единой загрузки исходных данных."""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from openpyxl import Workbook

from app.config_store import ConfigStore
from app.data_sources import (
    CMDB_SOURCE,
    REQUESTS_SOURCE,
    RunnerDeps,
    copy_to_storage,
    files_identical,
    find_latest_source_file,
    load_source,
)
from app.state_store import StateStore


def _touch_xlsx(path: Path) -> None:
    wb = Workbook()
    wb.active.append(["col"])
    wb.save(path)


def test_find_latest_source_file_picks_newest(tmp_path: Path) -> None:
    older = tmp_path / "cmdb-old.xlsx"
    newer = tmp_path / "export-cmdb-2026.xlsx"
    _touch_xlsx(older)
    time.sleep(0.05)
    _touch_xlsx(newer)

    found = find_latest_source_file(CMDB_SOURCE, tmp_path)
    assert found == newer


def test_find_latest_source_file_requests_marker(tmp_path: Path) -> None:
    wrong = tmp_path / "other.xlsx"
    right = tmp_path / "Выгрузка Заявки ПП.xlsx"
    _touch_xlsx(wrong)
    _touch_xlsx(right)

    found = find_latest_source_file(REQUESTS_SOURCE, tmp_path)
    assert found == right


def test_files_identical_detects_same_content(tmp_path: Path) -> None:
    a = tmp_path / "a.xlsx"
    b = tmp_path / "b.xlsx"
    _touch_xlsx(a)
    _touch_xlsx(b)
    assert files_identical(a, b)


def test_load_source_no_input_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.data_sources.INPUT_DATA_DIR", tmp_path / "missing")
    store = ConfigStore(path=tmp_path / "config.json")
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    deps = RunnerDeps(store=store, state=state)

    result = load_source("cmdb", deps)
    assert not result.ok
    assert "inputData" in result.message


def test_load_source_no_changes_requests(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_dir = tmp_path / "inputData"
    input_dir.mkdir()
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    monkeypatch.setattr("app.data_sources.INPUT_DATA_DIR", input_dir)
    monkeypatch.setattr("app.data_sources.UPLOADS_DIR", uploads)

    source = input_dir / "Заявки-1.xlsx"
    _touch_xlsx(source)
    copy_to_storage(REQUESTS_SOURCE, source)

    from app.cashflow_report import save_report_artifact

    monkeypatch.setattr(
        "app.cashflow_report.REPORTS_DIR",
        tmp_path / "reports",
    )
    (tmp_path / "reports").mkdir()
    save_report_artifact({"generated_at": "2026-01-01T00:00:00+00:00", "row_count": 1})

    store = ConfigStore(path=tmp_path / "config.json")
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()

    from app.state_store import PPRequestRow
    from app.pp_import import parse_dt

    with state.replace_pp_requests() as session:
        session.write_batch(
            [
                PPRequestRow(
                    request_number="seed",
                    status="ok",
                    drug_number="SD1",
                    created_at=None,
                    completed_at=parse_dt("2026-01-01"),
                    customer_fio="Test",
                    tb="TB",
                    work_type="РВР",
                    act_status="",
                    amount_vat=0.0,
                    warranty="Нет",
                    address="",
                    security_system_type="СОТС",
                    in_limit="",
                    raw_json="{}",
                    source_row=2,
                )
            ]
        )

    deps = RunnerDeps(store=store, state=state)

    result = load_source("requests", deps)
    assert result.ok
    assert result.message == "Новых данных нет"
    assert not result.changed
