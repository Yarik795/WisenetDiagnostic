"""Веб-тесты раздела «База устройств»."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config_store import ConfigStore
from app.main import app
from app.state_store import StateStore
from app.ui.dependencies import get_state_store, get_store


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    store = ConfigStore(path=tmp_path / "config.json")
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()

    def override_store() -> ConfigStore:
        return store

    def override_state() -> StateStore:
        return state

    app.dependency_overrides[get_store] = override_store
    app.dependency_overrides[get_state_store] = override_state
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_device_base_page_renders(client: TestClient) -> None:
    r = client.get("/device-base")
    assert r.status_code == 200
    assert "База устройств" in r.text
    assert "Добавить устройство" in r.text
    assert "Нет устройств" in r.text


def test_device_base_create_update_delete(client: TestClient, tmp_path: Path) -> None:
    created = client.post(
        "/device-base",
        data={
            "address": "Объект 1",
            "device_type": "recorder",
            "model": "",
            "host": "10.1.2.3",
        },
        follow_redirects=False,
    )
    assert created.status_code in (200, 303)

    page = client.get("/device-base")
    assert "10.1.2.3" in page.text
    assert "Регистратор" in page.text

    store = ConfigStore(path=tmp_path / "config.json")
    recorders = store.list_recorders()
    assert len(recorders) == 1
    assert recorders[0].host == "10.1.2.3"

    state = StateStore(path=tmp_path / "monitoring.db")
    row = state.list_device_base()[0]
    updated = client.post(
        f"/device-base/{row.id}",
        data={
            "address": "Объект 1",
            "device_type": "locker",
            "model": "Pridex",
            "host": "10.1.2.3",
        },
        follow_redirects=False,
    )
    assert updated.status_code in (200, 303)
    page = client.get("/device-base")
    assert "Pridex" in page.text
    recorders = store.list_recorders()
    assert len(recorders) == 1
    assert recorders[0].device_kind == "lockers"

    deleted = client.post(
        f"/device-base/{row.id}/delete",
        follow_redirects=False,
    )
    assert deleted.status_code in (200, 303)
    page = client.get("/device-base")
    assert "10.1.2.3" not in page.text


def test_device_base_form_validation(client: TestClient) -> None:
    r = client.post(
        "/device-base",
        data={
            "address": "",
            "device_type": "recorder",
            "model": "",
            "host": "bad",
        },
    )
    assert r.status_code == 400
    assert "Укажите адрес" in r.text
    assert "Некорректный IPv4" in r.text


def test_nav_has_device_base(client: TestClient) -> None:
    r = client.get("/sources")
    assert r.status_code == 200
    assert 'href="/device-base"' in r.text
    assert "Обновить CMDB" not in r.text
    assert 'hx-post="/sources/cmdb/load"' not in r.text
