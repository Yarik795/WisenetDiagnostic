"""Тесты синхронизации config из CMDB (без реального xlsx)."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
BACKEND = ROOT / "backend"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(BACKEND))

from app.models import CheckStatus, Recorder  # noqa: E402
from cmdb_reader import (  # noqa: E402
    CmdbRecorderRow,
    FUNCTIONAL_TYPE_VIDEO,
    build_col_index,
    find_header_row,
    merge_recorders_from_cmdb,
    parse_cmdb_grid,
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


def test_find_header_row_skips_description_rows() -> None:
    grid = _grid_with_data()
    assert find_header_row(grid) == 1


def test_parse_cmdb_filters_videoregistratory() -> None:
    grid = _grid_with_data(
        [
            "538000001",
            "Оборудование ТСО",
            "10.0.0.1",
            "",
            "",
            "г. Москва",
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
            "538000002",
            "Оборудование ТСО",
            "10.0.0.2",
            "",
            "",
            "г. СПб",
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
            "X",
            "",
            "",
            "",
            "",
            "",
            "",
            "Камера",
        ],
    )
    result = parse_cmdb_grid(grid)
    assert len(result.rows) == 1
    assert result.rows[0].host == "10.0.0.1"
    assert result.rows[0].object_name == "г. Москва"
    assert result.rows[0].name == "HRX-1620"
    assert result.skipped_wrong_type == 1


def test_build_col_index_normalizes_spaces() -> None:
    header = ["  IP  ", "Функциональный  тип", "Адрес", "Модель устройства"]
    idx = build_col_index(header)
    assert idx["IP"] == 0
    assert idx["Функциональный тип"] == 1


def test_merge_preserves_id_and_last_by_host() -> None:
    existing = [
        Recorder(
            id="nvr-keep-me",
            object_name="old",
            name="old-name",
            host="10.1.1.1",
            last_status=CheckStatus.ONLINE,
            last_check_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            last_error=None,
        ),
        Recorder(
            id="nvr-remove",
            object_name="gone",
            host="10.9.9.9",
        ),
    ]
    cmdb_rows = [
        CmdbRecorderRow(
            host="10.1.1.1",
            object_name="новый адрес",
            name="HRX-1620",
            source_row=5,
        ),
        CmdbRecorderRow(
            host="10.2.2.2",
            object_name="новый объект",
            name=None,
            source_row=6,
        ),
    ]
    merged, stats, errors = merge_recorders_from_cmdb(cmdb_rows, existing)
    assert not errors
    assert stats.preserved == 1
    assert stats.added == 1
    assert stats.removed == 1

    by_host = {r.host: r for r in merged}
    assert by_host["10.1.1.1"].id == "nvr-keep-me"
    assert by_host["10.1.1.1"].last_status == CheckStatus.ONLINE
    assert by_host["10.1.1.1"].object_name == "новый адрес"
    assert by_host["10.1.1.1"].name == "HRX-1620"
    assert by_host["10.2.2.2"].id != "nvr-keep-me"
    assert "10.9.9.9" not in by_host


def test_merge_duplicate_ip_in_cmdb_second_gets_new_id() -> None:
    existing = [
        Recorder(id="nvr-first", object_name="o", host="10.0.0.5"),
    ]
    rows = [
        CmdbRecorderRow(host="10.0.0.5", object_name="a1", name="M1", source_row=2),
        CmdbRecorderRow(host="10.0.0.5", object_name="a2", name="M2", source_row=3),
    ]
    merged, stats, errors = merge_recorders_from_cmdb(rows, existing)
    assert not errors
    assert stats.preserved == 1
    assert stats.added == 1
    ids = [r.id for r in merged]
    assert ids[0] == "nvr-first"
    assert ids[1] != "nvr-first"


def test_merge_fail_on_empty_object_name() -> None:
    existing: list[Recorder] = []
    rows = [
        CmdbRecorderRow(host="10.0.0.1", object_name="", name="X", source_row=4),
    ]
    merged, stats, errors = merge_recorders_from_cmdb(rows, existing)
    assert merged == []
    assert len(errors) == 1
    assert errors[0].source_row == 4


def test_sync_preserves_exclusions(tmp_path: Path) -> None:
    from app.cmdb_sync import sync_from_cmdb
    from app.config_store import ConfigStore
    from app.models import AppConfig, ExclusionSettings

    store = ConfigStore(path=tmp_path / "config.json")
    store.save(
        AppConfig(
            recorders=[
                Recorder(
                    id="nvr-keep",
                    object_name="Old",
                    host="10.1.1.1",
                    port=80,
                )
            ],
            exclusions=ExclusionSettings(recorder_ids=["nvr-keep"]),
        )
    )

    xlsx = tmp_path / "cmdb.xlsx"
    xlsx.write_bytes(b"")
    from unittest.mock import patch
    from cmdb_reader import CmdbParseResult

    rows = [
        CmdbRecorderRow(
            host="10.1.1.1",
            object_name="New name",
            name="NVR",
            source_row=5,
        )
    ]
    parsed = CmdbParseResult(
        rows=rows,
        skipped_empty_ip=0,
        skipped_wrong_type=0,
        total_data_rows=1,
    )

    with patch("app.cmdb_sync.read_cmdb_xlsx", return_value=parsed):
        result = sync_from_cmdb(store, cmdb_path=xlsx, dry_run=True)

    assert result.ok
    config = store.load()
    assert "nvr-keep" in config.exclusions.recorder_ids
