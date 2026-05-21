from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config_store import ConfigStore
from app.main import app
from app.models import MonitoringSettings, RecorderCreate
from app.ui.dependencies import get_state_store, get_store


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


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "log_file" in data
    assert Path(data["log_file"]).name == "wisenet.log"


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
    from app.web import routes as web_routes

    async def fake_poll(config_store, state_store, recorder, include_inventory=True):
        config_store.update_recorder_status(
            recorder.id,
            CheckStatus.ONLINE,
            datetime.now(timezone.utc),
            error=None,
        )

    monkeypatch.setattr(web_routes, "poll_single_recorder", fake_poll)

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
    assert "Исправно" in r.text or "Доступен" in r.text


def test_enable_ntp_missing_server_config(client: TestClient) -> None:
    store = app.dependency_overrides[get_store]()
    store.update_credentials("admin", "secret")
    rec = store.create_recorder(
        RecorderCreate(
            object_name="Obj",
            host="10.0.0.5",
            port=80,
            use_https=False,
            enabled=True,
        )
    )

    r = client.post(
        f"/recorders/{rec.id}/ntp/enable",
        headers={
            "HX-Request": "true",
            "HX-Current-URL": "http://127.0.0.1/objects",
        },
    )
    assert r.status_code == 400
    trigger = r.headers.get("HX-Trigger", "")
    assert "monitoring.ntp_server" in trigger


def test_enable_ntp_success(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from datetime import datetime, timezone

    from app.sunapi_extended import EnableNtpResult
    from app.web import routes as web_routes

    store = app.dependency_overrides[get_store]()
    config = store.load()
    config.monitoring = MonitoringSettings(ntp_server="203.248.240.140")
    store.save(config)
    store.update_credentials("admin", "secret")
    rec = store.create_recorder(
        RecorderCreate(
            object_name="Obj",
            host="10.0.0.5",
            port=80,
            use_https=False,
            enabled=True,
        )
    )

    state = app.dependency_overrides[get_state_store]()
    polled_at = datetime.now(timezone.utc)
    state.upsert_recorder_metrics(
        rec.id,
        device_online=True,
        health_status="ok",
        sync_type="Manual",
        ntp_status="Fail",
        last_polled_at=polled_at,
    )

    async def fake_enable(recorder, credentials, ntp_server, **kwargs):
        return EnableNtpResult(success=True)

    async def fake_poll(config_store, state_store, recorder, include_inventory=True):
        state_store.upsert_recorder_metrics(
            recorder.id,
            device_online=True,
            health_status="ok",
            sync_type="NTP",
            ntp_status="Success",
            last_polled_at=polled_at,
        )

    monkeypatch.setattr(web_routes, "enable_recorder_ntp", fake_enable)
    monkeypatch.setattr(web_routes, "poll_single_recorder", fake_poll)

    r = client.post(
        f"/recorders/{rec.id}/ntp/enable",
        headers={
            "HX-Request": "true",
            "HX-Current-URL": "http://127.0.0.1/objects",
        },
    )
    assert r.status_code == 200
    assert "recorder-row" in r.text
    assert "NTP" in r.text
    trigger = r.headers.get("HX-Trigger", "")
    assert "success" in trigger
    assert "203.248.240.140" in trigger
    assert "\\u043e\\u0431\\u043d\\u043e\\u0432" in trigger  # "обнов" в JSON (ensure_ascii)
