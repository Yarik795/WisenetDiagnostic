"""Тесты страницы исходных данных."""

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


def test_sources_page_has_load_buttons(client: TestClient) -> None:
    r = client.get("/sources")
    assert r.status_code == 200
    assert "Обновить заявки с ПП" in r.text
    assert 'hx-post="/sources/requests/load"' in r.text
    assert "Данные не загружены" in r.text
    assert "Обновить CMDB" not in r.text
    assert 'hx-post="/sources/cmdb/load"' not in r.text
    assert 'href="/device-base"' in r.text
