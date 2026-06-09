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


def test_sources_page_has_cmdb_sync_button(client: TestClient) -> None:
    r = client.get("/sources")
    assert r.status_code == 200
    assert "Обновить из CMDB" in r.text
    assert 'hx-post="/sources/sync-cmdb"' in r.text
    assert 'hx-target="body"' in r.text
    assert 'hx-swap="none"' in r.text


def test_sync_cmdb_missing_file(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    missing = Path("/nonexistent/cmdb-missing-test.xlsx")
    monkeypatch.setattr("app.cmdb_sync.DEFAULT_CMDB_PATH", missing)
    r = client.post(
        "/objects/sync-cmdb",
        follow_redirects=False,
        headers={"HX-Request": "true"},
    )
    assert r.status_code == 200
    assert "toast=error" in r.headers["hx-redirect"]
    assert "showToast" in r.headers.get("hx-trigger", "")


def test_sync_cmdb_missing_file_without_htmx(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    missing = Path("/nonexistent/cmdb-missing-test.xlsx")
    monkeypatch.setattr("app.cmdb_sync.DEFAULT_CMDB_PATH", missing)
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
    cmdb_path = tmp_path / "cmdb.xlsx"
    _write_cmdb_xlsx(cmdb_path, grid)
    monkeypatch.setattr("app.cmdb_sync.DEFAULT_CMDB_PATH", cmdb_path)

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
    assert "CMDB" in sources.text
    assert "cmdb.xlsx" in sources.text


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
