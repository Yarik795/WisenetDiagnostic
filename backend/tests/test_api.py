from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config_store import ConfigStore
from app.main import app
from app.routers.recorders import get_store as get_recorders_store
from app.routers.settings import get_store as get_settings_store


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    config_path = tmp_path / "config.json"
    store = ConfigStore(path=config_path)

    def override_store() -> ConfigStore:
        return store

    app.dependency_overrides[get_recorders_store] = override_store
    app.dependency_overrides[get_settings_store] = override_store
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client: TestClient) -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_recorders_crud(client: TestClient) -> None:
    payload = {
        "object_name": "ВСП-045",
        "name": "NVR-main",
        "host": "10.1.2.3",
        "port": 80,
        "use_https": False,
        "enabled": True,
    }
    created = client.post("/api/recorders", json=payload)
    assert created.status_code == 201
    rid = created.json()["id"]

    listed = client.get("/api/recorders")
    assert len(listed.json()) == 1

    updated = client.put(
        f"/api/recorders/{rid}", json={**payload, "name": "NVR-2"}
    )
    assert updated.json()["name"] == "NVR-2"

    deleted = client.delete(f"/api/recorders/{rid}")
    assert deleted.status_code == 204
    assert client.get("/api/recorders").json() == []


def test_settings(client: TestClient) -> None:
    r = client.put(
        "/api/settings",
        json={"username": "admin", "password": "test"},
    )
    assert r.status_code == 200
    assert client.get("/api/settings").json()["username"] == "admin"
