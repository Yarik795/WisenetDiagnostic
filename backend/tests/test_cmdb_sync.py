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
    FUNCTIONAL_TYPE_AUX,
    FUNCTIONAL_TYPE_CAMERA,
    MANUFACTURER_BIO,
    MANUFACTURER_SKUD,
    CmdbDeviceRow,
    FUNCTIONAL_TYPE_VIDEO,
    build_col_index,
    classify_cmdb_row,
    find_header_row,
    is_cmdb_importable_row,
    merge_devices_from_cmdb,
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


def _cmdb_row(
    host: str,
    object_name: str,
    *,
    name: str | None = None,
    mac: str | None = None,
    functional_type: str = FUNCTIONAL_TYPE_VIDEO,
    manufacturer: str = "Hanwha",
    device_kind: str | None = "tsv",
    source_row: int = 5,
) -> CmdbDeviceRow:
    return CmdbDeviceRow(
        host=host,
        object_name=object_name,
        name=name,
        mac=mac,
        functional_type=functional_type,
        manufacturer=manufacturer,
        device_kind=device_kind,  # type: ignore[arg-type]
        source_row=source_row,
    )


def test_find_header_row_skips_description_rows() -> None:
    grid = _grid_with_data()
    assert find_header_row(grid) == 1


def test_classify_cmdb_row() -> None:
    assert classify_cmdb_row(FUNCTIONAL_TYPE_VIDEO, "Hanwha") == "tsv"
    assert classify_cmdb_row("", MANUFACTURER_SKUD) == "skud"
    assert classify_cmdb_row("", MANUFACTURER_BIO) == "bio"
    assert classify_cmdb_row("Камера", "Hanwha") is None
    assert is_cmdb_importable_row(FUNCTIONAL_TYPE_CAMERA, "Hanwha")
    assert is_cmdb_importable_row(FUNCTIONAL_TYPE_AUX, "Hanwha")
    assert not is_cmdb_importable_row("Камера", "Hanwha")


def test_parse_cmdb_filters_videoregistratory() -> None:
    grid = _grid_with_data(
        [
            "538000001",
            "Оборудование ТСО",
            "10.0.0.1",
            "E8:FF:1E:30:15:3F",
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
    assert result.rows[0].device_kind == "tsv"
    assert result.rows[0].mac == "E8:FF:1E:30:15:3F"
    assert result.skipped_unclassified == 1
    assert result.counts_by_kind["tsv"] == 1


def test_parse_cmdb_camera_and_aux() -> None:
    grid = _grid_with_data(
        [
            "538000010",
            "Оборудование ТСО",
            "10.0.0.10",
            "AA:BB:CC:DD:EE:FF",
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
            "QNO-6010R",
            "",
            "",
            "",
            "",
            "",
            "",
            FUNCTIONAL_TYPE_CAMERA,
        ],
        [
            "538000011",
            "Оборудование ТСО",
            "10.0.0.11",
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
            "Generic",
            "UPS-100",
            "",
            "",
            "",
            "",
            "",
            "",
            FUNCTIONAL_TYPE_AUX,
        ],
    )
    result = parse_cmdb_grid(grid)
    assert len(result.rows) == 2
    by_host = {r.host: r for r in result.rows}
    assert by_host["10.0.0.10"].device_kind is None
    assert by_host["10.0.0.10"].functional_type == FUNCTIONAL_TYPE_CAMERA
    assert by_host["10.0.0.11"].device_kind is None
    assert by_host["10.0.0.11"].functional_type == FUNCTIONAL_TYPE_AUX
    assert result.counts_by_kind["camera"] == 1
    assert result.counts_by_kind["aux"] == 1


def test_merge_ignores_db_only_rows() -> None:
    existing: list[Recorder] = []
    rows = [
        _cmdb_row("10.0.0.1", "obj", name="NVR"),
        _cmdb_row(
            "10.0.0.2",
            "cam obj",
            name="Cam",
            functional_type=FUNCTIONAL_TYPE_CAMERA,
            device_kind=None,
        ),
    ]
    merged, stats, errors = merge_devices_from_cmdb(rows, existing)
    assert not errors
    assert len(merged) == 1
    assert merged[0].host == "10.0.0.1"
    assert stats.added == 1


def test_parse_cmdb_skud_and_bio() -> None:
    grid = _grid_with_data(
        [
            "538000001",
            "Оборудование ТСО",
            "100.111.46.66",
            "E8:FF:1E:30:15:3F",
            "",
            "г. Москва, ул. Федосьино",
            "",
            "СКУД",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            MANUFACTURER_SKUD,
            "NG NET",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        [
            "538000001",
            "Оборудование ТСО",
            "100.111.47.19",
            "0C:63:FC:0A:E8:E2",
            "",
            "г. Москва, ул. Череповецкая",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            MANUFACTURER_BIO,
            "Pocket Face FS6",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
    )
    result = parse_cmdb_grid(grid)
    assert len(result.rows) == 2
    by_host = {r.host: r for r in result.rows}
    assert by_host["100.111.46.66"].device_kind == "skud"
    assert by_host["100.111.46.66"].name == "NG NET"
    assert by_host["100.111.47.19"].device_kind == "bio"
    assert by_host["100.111.47.19"].mac == "0C:63:FC:0A:E8:E2"
    assert result.counts_by_kind["skud"] == 1
    assert result.counts_by_kind["bio"] == 1


def test_build_col_index_normalizes_spaces() -> None:
    header = [
        "  IP  ",
        "Адрес",
        "Модель  устройства",
        "Производитель устройства",
        "MAC",
        "Функциональный  тип",
    ]
    idx = build_col_index(header)
    assert idx["IP"] == 0
    assert idx["Функциональный тип"] == 5


def test_build_col_index_accepts_latin_homoglyph_address() -> None:
    header = [
        "IP",
        "Адреc",
        "Модель уcтройcтва",
        "Производитель устройства",
        "MAC",
        "Функциональный тип",
    ]
    idx = build_col_index(header)
    assert idx["Адрес"] == 1
    assert idx["Модель устройства"] == 2


def test_parse_cmdb_with_homoglyph_functional_type() -> None:
    video_type_homoglyph = "Видеорегистраторы".replace("с", "c")
    grid = _grid_with_data(
        [
            "538000001",
            "Оборудование ТСО",
            "10.0.0.3",
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
            video_type_homoglyph,
        ],
    )
    result = parse_cmdb_grid(grid)
    assert len(result.rows) == 1
    assert result.rows[0].host == "10.0.0.3"


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
        _cmdb_row("10.1.1.1", "новый адрес", name="HRX-1620", source_row=5),
        _cmdb_row("10.2.2.2", "новый объект", source_row=6),
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


def test_merge_duplicate_ip_same_kind_second_gets_new_id() -> None:
    existing = [
        Recorder(id="nvr-first", object_name="o", host="10.0.0.5"),
    ]
    rows = [
        _cmdb_row("10.0.0.5", "a1", name="M1", source_row=2),
        _cmdb_row("10.0.0.5", "a2", name="M2", source_row=3),
    ]
    merged, stats, errors = merge_recorders_from_cmdb(rows, existing)
    assert not errors
    assert stats.preserved == 1
    assert stats.added == 1
    ids = [r.id for r in merged]
    assert ids[0] == "nvr-first"
    assert ids[1] != "nvr-first"


def test_merge_same_ip_different_kinds() -> None:
    existing: list[Recorder] = []
    rows = [
        _cmdb_row(
            "10.0.0.5",
            "addr",
            name="NVR",
            functional_type=FUNCTIONAL_TYPE_VIDEO,
            manufacturer="Hanwha",
            device_kind="tsv",
        ),
        _cmdb_row(
            "10.0.0.5",
            "addr",
            name="NG NET",
            functional_type="",
            manufacturer=MANUFACTURER_SKUD,
            device_kind="skud",
        ),
    ]
    merged, stats, errors = merge_devices_from_cmdb(rows, existing)
    assert not errors
    assert len(merged) == 2
    kinds = {r.device_kind for r in merged}
    assert kinds == {"tsv", "skud"}


def test_merge_preserves_sots_devices() -> None:
    existing = [
        Recorder(
            id="sots-1",
            object_name="Obj",
            host="10.8.8.8",
            device_kind="sots",
        ),
        Recorder(
            id="nvr-remove",
            object_name="gone",
            host="10.9.9.9",
        ),
    ]
    rows = [_cmdb_row("10.1.1.1", "new", name="NVR")]
    merged, stats, errors = merge_devices_from_cmdb(rows, existing)
    assert not errors
    ids = {r.id for r in merged}
    assert "sots-1" in ids
    assert "nvr-remove" not in ids
    assert stats.removed == 1


def test_merge_fail_on_empty_object_name() -> None:
    existing: list[Recorder] = []
    rows = [_cmdb_row("10.0.0.1", "", name="X", source_row=4)]
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

    rows = [_cmdb_row("10.1.1.1", "New name", name="NVR", source_row=5)]
    parsed = CmdbParseResult(
        rows=rows,
        skipped_empty_ip=0,
        skipped_unclassified=0,
        total_data_rows=1,
        counts_by_kind={"tsv": 1, "skud": 0, "bio": 0},
    )

    with patch("app.cmdb_sync.read_cmdb_xlsx", return_value=parsed):
        result = sync_from_cmdb(store, cmdb_path=xlsx, dry_run=True)

    assert result.ok
    config = store.load()
    assert "nvr-keep" in config.exclusions.recorder_ids


def test_sync_preserves_email_report(tmp_path: Path) -> None:
    from unittest.mock import patch

    from app.cmdb_sync import sync_from_cmdb
    from app.config_store import ConfigStore
    from app.models import AppConfig, EmailReportSettings
    from cmdb_reader import CmdbParseResult

    store = ConfigStore(path=tmp_path / "config.json")
    email_settings = EmailReportSettings(
        enabled=True,
        smtp_host="smtp.example.com",
        smtp_port=587,
        from_email="sender@example.com",
        to_emails=["a@example.com", "b@example.com"],
        subject="Custom subject",
        send_time="14:45",
    )
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
            email_report=email_settings,
        )
    )

    xlsx = tmp_path / "cmdb.xlsx"
    xlsx.write_bytes(b"")
    parsed = CmdbParseResult(
        rows=[_cmdb_row("10.1.1.1", "New name", name="NVR", source_row=5)],
        skipped_empty_ip=0,
        skipped_unclassified=0,
        total_data_rows=1,
        counts_by_kind={"tsv": 1, "skud": 0, "bio": 0},
    )

    with patch("app.cmdb_sync.read_cmdb_xlsx", return_value=parsed):
        result = sync_from_cmdb(store, cmdb_path=xlsx)

    assert result.ok
    config = store.load()
    assert config.email_report == email_settings


def test_sync_skips_write_when_no_changes(tmp_path: Path) -> None:
    from unittest.mock import patch

    from app.cmdb_sync import sync_from_cmdb
    from app.config_store import ConfigStore
    from app.models import AppConfig
    from cmdb_reader import CmdbParseResult

    config_path = tmp_path / "config.json"
    store = ConfigStore(path=config_path)
    recorder = Recorder(id="nvr-keep", object_name="Obj", host="10.1.1.1", name="NVR")
    store.save(AppConfig(recorders=[recorder]))
    mtime_before = config_path.stat().st_mtime

    xlsx = tmp_path / "cmdb.xlsx"
    xlsx.write_bytes(b"")
    parsed = CmdbParseResult(
        rows=[_cmdb_row("10.1.1.1", "Obj", name="NVR", source_row=5)],
        skipped_empty_ip=0,
        skipped_unclassified=0,
        total_data_rows=1,
        counts_by_kind={"tsv": 1, "skud": 0, "bio": 0},
    )

    with patch("app.cmdb_sync.read_cmdb_xlsx", return_value=parsed):
        result = sync_from_cmdb(store, cmdb_path=xlsx)

    assert result.ok
    assert "Изменений нет" in result.message
    assert config_path.stat().st_mtime == mtime_before
    assert list(tmp_path.glob("config.json.bak.*")) == []
