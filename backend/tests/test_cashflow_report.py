from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from app.cashflow_report import (
    REPORT_ARTIFACT,
    build_cashflow_report,
    find_latest_requests_source_file,
    import_requests_from_source,
    load_report_artifact,
    read_excel,
    requests_file_path,
)


def _sample_row(**overrides):
    base = {
        "Вид работ": "Модернизация",
        "Статус": "На согласовании",
        "Статус акта": "Проект",
        "ФИО заказчика": "Зайцев Иван",
        "Фактическая дата выполнения (UTC)": date.today(),
        "Территориальный банк": "38 Московский банк",
        "Сумма с НДС": "10 000,50",
        "Заявка №": "1234567",
        "В лимите": "Московский банк",
    }
    base.update(overrides)
    return base


@pytest.fixture
def sample_xlsx(tmp_path: Path) -> Path:
    path = tmp_path / "sample.xlsx"
    rows = [
        _sample_row(),
        _sample_row(
            ФИО="Петров Андрей С.",
            **{"ФИО заказчика": "Петров Андрей С.", "Территориальный банк": "99 ЦА"},
        ),
        _sample_row(**{"Вид работ": "РВР", "Статус": "На согласовании"}),
    ]
    pd.DataFrame(rows).to_excel(path, index=False, engine="openpyxl")
    return path


def test_build_cashflow_report_success(sample_xlsx: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    artifact = tmp_path / "cashflow_report.json"
    monkeypatch.setattr("app.cashflow_report.REPORT_ARTIFACT", artifact)

    payload = build_cashflow_report(sample_xlsx)

    assert payload["row_count"] == 3
    assert "modern" in payload["reports"]
    assert "rvr" in payload["reports"]
    assert len(payload["reports"]["modern"]["sections"]) == 4
    assert artifact.is_file()
    loaded = load_report_artifact()
    assert loaded is not None
    assert loaded["row_count"] == 3


def test_read_excel_missing_columns(tmp_path: Path):
    path = tmp_path / "bad.xlsx"
    pd.DataFrame({"Статус": ["x"]}).to_excel(path, index=False, engine="openpyxl")
    df = read_excel(path)
    with pytest.raises(ValueError, match="обязательные столбцы"):
        from app.cashflow_report import _validate_columns

        _validate_columns(df)


def test_build_cashflow_report_empty_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    path = tmp_path / "empty.xlsx"
    pd.DataFrame(columns=list(_sample_row().keys())).to_excel(path, index=False, engine="openpyxl")
    artifact = tmp_path / "cashflow_report.json"
    monkeypatch.setattr("app.cashflow_report.REPORT_ARTIFACT", artifact)

    with pytest.raises(ValueError, match="не содержит строк"):
        build_cashflow_report(path)


def test_requests_file_path_points_to_uploads():
    path = requests_file_path()
    assert path.name == "requests.xlsx"
    assert "uploads" in path.as_posix()


def test_find_latest_requests_source_file(tmp_path: Path):
    older = tmp_path / "Заявки_старые.xlsx"
    newer = tmp_path / "выгрузка_Заявки_2026.xlsx"
    other = tmp_path / "отчет.xlsx"
    pd.DataFrame({"a": [1]}).to_excel(older, index=False, engine="openpyxl")
    pd.DataFrame({"a": [2]}).to_excel(newer, index=False, engine="openpyxl")
    pd.DataFrame({"a": [3]}).to_excel(other, index=False, engine="openpyxl")
    newer.touch()
    import os
    import time

    os.utime(older, (time.time() - 3600, time.time() - 3600))

    found = find_latest_requests_source_file(tmp_path)
    assert found == newer


def test_find_latest_requests_source_file_missing_dir(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="не найдена"):
        find_latest_requests_source_file(tmp_path / "missing")


def test_import_requests_from_source(sample_xlsx: Path, tmp_path: Path):
    dest = tmp_path / "requests.xlsx"
    copied, size = import_requests_from_source(sample_xlsx, dest)
    assert copied == dest
    assert size > 0
    assert dest.is_file()
