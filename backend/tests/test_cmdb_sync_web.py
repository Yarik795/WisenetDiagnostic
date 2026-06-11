"""Тесты веб-синхронизации CMDB и sync_from_cmdb."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook

from app.cmdb_sync import sync_from_cmdb
from app.config_store import ConfigStore
from app.main import app
from app.models import RecorderCreate
from app.ui.dependencies import get_state_store, get_store

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
from cmdb_reader import FUNCTIONAL_TYPE_VIDEO  # noqa: E402


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
def client(tmp_path: Path) -> TestClient:
    config_path = tmp_path / "config.json"
    store = ConfigStore(path=config_path)
    db_path = tmp_path / "monitoring.db"

    from app.state_store import StateStore

    state = StateStore(path=db_path)
    state.init_db()

    def override_store() -> ConfigStore:
        return store

    def override_state() -> StateStore:
        return state

    app.dependency_overrides[get_store] = override_store
    app.dependency_overrides[get_state_store] = override_state
    yield TestClient(app)
    app.dependency_overrides.clear()


def _setup_input_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    input_dir = tmp_path / "inputData"
    input_dir.mkdir()
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    monkeypatch.setattr("app.data_sources.INPUT_DATA_DIR", input_dir)
    monkeypatch.setattr("app.data_sources.UPLOADS_DIR", uploads)
    return input_dir


def test_sources_page_has_load_buttons(client: TestClient) -> None:
    r = client.get("/sources")
    assert r.status_code == 200
    assert "Обновить CMDB" in r.text
    assert "Обновить заявки с ПП" in r.text
    assert 'hx-post="/sources/cmdb/load"' in r.text
    assert 'hx-post="/sources/requests/load"' in r.text
    assert "Данные не загружены" in r.text


def test_sync_cmdb_missing_file(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _setup_input_data(tmp_path, monkeypatch)
    r = client.post(
        "/objects/sync-cmdb",
        follow_redirects=False,
        headers={"HX-Request": "true"},
    )
    assert r.status_code == 200
    assert "toast=error" in r.headers["hx-redirect"]
    assert "showToast" in r.headers.get("hx-trigger", "")


def test_sync_cmdb_missing_file_without_htmx(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _setup_input_data(tmp_path, monkeypatch)
    r = client.post("/objects/sync-cmdb", follow_redirects=False)
    assert r.status_code == 303
    loc = r.headers["location"]
    assert "toast=error" in loc
    assert "msg=" in loc


def test_sync_cmdb_success(
    client: TestClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_dir = _setup_input_data(tmp_path, monkeypatch)
    grid = _grid_with_data(
        [
            "538000001",
            "Оборудование ТСО",
            "10.88.1.1",
            "",
            "",
            "Объект А",
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
    )
    cmdb_path = input_dir / "cmdb-export.xlsx"
    _write_cmdb_xlsx(cmdb_path, grid)

    r = client.post(
        "/objects/sync-cmdb",
        follow_redirects=False,
        headers={"HX-Request": "true"},
    )
    assert r.status_code == 200
    assert "toast=success" in r.headers["hx-redirect"]
    assert "showToast" in r.headers.get("hx-trigger", "")

    page = client.get("/monitoring", follow_redirects=True)
    assert "10.88.1.1" in page.text
    assert "Объект А" in page.text

    sources = client.get("/sources")
    assert "Обновлено:" in sources.text
    assert "cmdb-export.xlsx" in sources.text


def test_sources_load_cmdb_returns_job_panel(
    client: TestClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_dir = _setup_input_data(tmp_path, monkeypatch)
    grid = _grid_with_data(
        [
            "538000001",
            "Оборудование ТСО",
            "10.88.1.2",
            "",
            "",
            "Объект B",
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
    )
    _write_cmdb_xlsx(input_dir / "cmdb.xlsx", grid)

    r = client.post("/sources/cmdb/load")
    assert r.status_code == 200
    assert "poll-job-panel" in r.text
    assert "progressbar" in r.text.lower() or "progress" in r.text.lower()


def test_sync_from_cmdb_replaces_recorders(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"
    store = ConfigStore(path=config_path)
    store.create_recorder(
        RecorderCreate(
            object_name="Старый",
            host="192.168.1.1",
            port=80,
        )
    )

    grid = _grid_with_data(
        [
            "538000001",
            "Оборудование ТСО",
            "10.0.0.99",
            "",
            "",
            "Новый объект",
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
            "NVR-1",
            "",
            "",
            "",
            "",
            "",
            "",
            FUNCTIONAL_TYPE_VIDEO,
        ],
    )
    cmdb_path = tmp_path / "cmdb.xlsx"
    _write_cmdb_xlsx(cmdb_path, grid)

    result = sync_from_cmdb(store, cmdb_path)
    assert result.ok
    recorders = store.list_recorders()
    assert len(recorders) == 1
    assert recorders[0].host == "10.0.0.99"
    assert recorders[0].object_name == "Новый объект"
