from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config_store import ConfigStore
from app.main import app
from app.ui.dependencies import get_store


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    config_path = tmp_path / "config.json"
    store = ConfigStore(path=config_path)

    def override_store() -> ConfigStore:
        return store

    app.dependency_overrides[get_store] = override_store
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_root_redirects(client: TestClient) -> None:
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "/objects"


def test_objects_page_empty(client: TestClient) -> None:
    r = client.get("/objects")
    assert r.status_code == 200
    assert "Нет регистраторов" in r.text


def test_recorders_crud_via_forms(client: TestClient) -> None:
    r = client.post(
        "/recorders",
        data={
            "object_name": "ВСП-045",
            "name": "NVR-main",
            "host": "10.1.2.3",
            "port": "80",
            "use_https": "false",
            "enabled": "true",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert "/objects" in r.headers["location"]

    page = client.get("/objects")
    assert "ВСП-045" in page.text
    assert "10.1.2.3" in page.text

    list_page = client.get("/recorders")
    assert "ВСП-045" in list_page.text


def test_settings_form(client: TestClient) -> None:
    r = client.post(
        "/settings",
        data={"username": "admin", "password": "secret"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    page = client.get("/settings?saved=1")
    assert "admin" in page.text


def test_check_returns_row_fragment(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from datetime import datetime, timezone

    from app.models import CheckStatus
    from app.sunapi import SunapiCheckOutcome
    from app.web import routes as web_routes

    async def fake_check(recorder, credentials):
        return SunapiCheckOutcome(
            status=CheckStatus.ONLINE,
            checked_at=datetime.now(timezone.utc),
            error=None,
            device=None,
        )

    monkeypatch.setattr(web_routes, "check_recorder", fake_check)

    client.post(
        "/recorders",
        data={
            "object_name": "Obj",
            "name": "",
            "host": "10.0.0.5",
            "port": "80",
            "use_https": "false",
            "enabled": "true",
        },
        follow_redirects=True,
    )

    store = app.dependency_overrides[get_store]()
    recs = store.list_recorders()
    assert len(recs) == 1
    rid = recs[0].id

    r = client.post(
        f"/recorders/{rid}/check",
        headers={
            "HX-Request": "true",
            "HX-Current-URL": "http://127.0.0.1/objects",
        },
    )
    assert r.status_code == 200
    assert "recorder-row" in r.text
    assert "Доступен" in r.text
