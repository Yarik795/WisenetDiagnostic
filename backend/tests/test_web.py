from pathlib import Path
from urllib.parse import quote

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
    assert r.headers["location"] == "/summary"


def test_monitoring_page_empty(client: TestClient) -> None:
    r = client.get("/monitoring")
    assert r.status_code == 200
    assert "Нет устройств" in r.text


def test_summary_page_renders(client: TestClient) -> None:
    r = client.get("/summary")
    assert r.status_code == 200
    assert "Дашборд руководителя ТСО" in r.text or "Сводка" in r.text
    assert "Биотерминалы" in r.text


def test_kind_section_pages(client: TestClient) -> None:
    for path, label in (("/skud", "СКУД"), ("/bio", "Биотерминалы")):
        r = client.get(path)
        assert r.status_code == 200
        assert label in r.text


def test_removed_detail_routes_return_404(client: TestClient) -> None:
    assert client.get("/channels").status_code == 404
    assert client.get("/history").status_code == 404


def test_placeholder_sections(client: TestClient) -> None:
    for path in ("/budget", "/smartview"):
        r = client.get(path)
        assert r.status_code == 200
        assert "в разработке" in r.text.lower()


def test_recorders_age_page_renders(client: TestClient) -> None:
    r = client.get("/recorders-age")
    assert r.status_code == 200
    assert "Регистраторы по времени" in r.text
    assert "data-recorder-age-dashboard" in r.text or "Нет данных" in r.text


def test_disks_wear_page_renders(client: TestClient) -> None:
    r = client.get("/disks-wear")
    assert r.status_code == 200
    assert "Диски по времени" in r.text
    assert "data-disk-wear-dashboard" in r.text or "Нет данных" in r.text


def test_site_devices_page_renders(client: TestClient) -> None:
    r = client.get("/site-devices")
    assert r.status_code == 200
    assert "Устройства на объекте" in r.text
    assert "site-object-details" in r.text or "Нет данных" in r.text
    assert r.text.count("<form") == r.text.count("</form>")


def test_site_devices_ping_zombies_returns_panel(
    client: TestClient,
    tmp_path: Path,
) -> None:
    from app.state_store import CmdbRecordRow
    from app.ui.site_inventory import CMDB_TYPE_CAMERA

    store = ConfigStore(path=tmp_path / "config_ping.json")
    store.create_recorder(
        RecorderCreate(
            object_name="Объект 1",
            name="NVR-1",
            host="10.1.1.10",
            port=80,
            use_https=False,
            device_kind="tsv",
        )
    )

    from app.state_store import StateStore

    state = StateStore(path=tmp_path / "ping.db")
    state.init_db()
    with state.replace_cmdb_records() as session:
        session.write_batch(
            [
                CmdbRecordRow(
                    host="10.1.1.30",
                    functional_type=CMDB_TYPE_CAMERA,
                    manufacturer="Hanwha",
                    object_name="Объект 1",
                    model_name="XNO-6080R",
                    mac=None,
                    device_kind=None,
                    source_row=1,
                ),
            ]
        )

    def override_store() -> ConfigStore:
        return store

    def override_state() -> StateStore:
        return state

    app.dependency_overrides[get_store] = override_store
    app.dependency_overrides[get_state_store] = override_state
    try:
        r = client.post("/site-devices/ping-zombies", data={"search": ""})
        assert r.status_code == 200
        assert 'id="site-ping-panel"' in r.text
        assert "Ping выполняется" in r.text or "Запуск" in r.text or "Завершён" in r.text
    finally:
        app.dependency_overrides.clear()


def test_rvr_repeat_page_renders(client: TestClient) -> None:
    r = client.get("/rvr-repeat")
    assert r.status_code == 200
    assert "Анализ повторных РВР" in r.text
    assert "Повторные РВР" in r.text
    assert 'id="rvr-object-type"' in r.text
    assert 'data-rvr-date-from' in r.text
    assert "rvr-kind-cell" not in r.text


def test_rvr_repeat_page_export_buttons_when_no_data(client: TestClient) -> None:
    r = client.get("/rvr-repeat")
    assert r.status_code == 200
    assert 'data-rvr-export-html' not in r.text
    assert 'data-rvr-email-html' not in r.text


def test_rvr_repeat_page_with_object_type_filter(client: TestClient) -> None:
    r = client.get("/rvr-repeat?object_type=%D0%92%D0%A1%D0%9F")
    assert r.status_code == 200
    assert 'value="ВСП" selected' in r.text
    assert "object_type=%D0%92%D0%A1%D0%9F" in r.text or "object_type=ВСП" in r.text


def test_rvr_repeat_export_without_data_redirects(client: TestClient) -> None:
    r = client.get("/rvr-repeat/export.xlsx", follow_redirects=False)
    assert r.status_code == 303
    assert "/rvr-repeat" in r.headers["location"]


def test_rvr_repeat_export_html_without_data_redirects(client: TestClient) -> None:
    r = client.get("/rvr-repeat/export.html", follow_redirects=False)
    assert r.status_code == 303
    assert "/rvr-repeat" in r.headers["location"]


def test_rvr_repeat_email_without_data(client: TestClient) -> None:
    r = client.post("/rvr-repeat/report/email")
    assert r.status_code == 400
    data = r.json()
    assert data["ok"] is False


def test_rvr_repeat_email_html_without_data(client: TestClient) -> None:
    r = client.post("/rvr-repeat/report/email.html")
    assert r.status_code == 400
    data = r.json()
    assert data["ok"] is False


def test_objects_redirects_to_monitoring(client: TestClient) -> None:
    r = client.get("/objects", follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "/monitoring"


def test_recorders_crud_via_forms(client: TestClient) -> None:
    r = client.post(
        "/recorders",
        data={
            "object_name": "ВСП-045",
            "name": "NVR-main",
            "host": "10.1.2.3",
            "port": "80",
            "use_https": "false",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert "/monitoring" in r.headers["location"]

    page = client.get("/monitoring")
    assert "ВСП-045" in page.text
    assert "10.1.2.3" in page.text

    list_page = client.get("/recorders", follow_redirects=True)
    assert list_page.url.path == "/monitoring"
    assert "view=table" in str(list_page.url.query)
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


def test_time_redirects_to_status(client: TestClient) -> None:
    r = client.get("/time", follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"].startswith("/monitoring?tab=health")
    assert "category=time" in r.headers["location"]

    page = client.get("/time", follow_redirects=True)
    assert page.status_code == 200
    assert "Сводка" in page.text
    assert "time-dashboard" in page.text


def test_recorders_redirects_to_objects_table(client: TestClient) -> None:
    r = client.get("/recorders", follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "/monitoring?view=table"


def test_status_time_category_ntp_fail_in_critical_kpi(client: TestClient) -> None:
    from datetime import datetime, timezone

    store = app.dependency_overrides[get_store]()
    store.update_credentials("admin", "secret")
    rec = store.create_recorder(
        RecorderCreate(
            object_name="Obj",
            host="10.0.0.1",
            port=80,
            use_https=False,
        )
    )
    state = app.dependency_overrides[get_state_store]()
    state.upsert_recorder_metrics(
        rec.id,
        device_online=True,
        health_status="warn",
        ntp_status="Fail",
        sync_type="Manual",
        last_polled_at=datetime.now(timezone.utc),
    )

    r = client.get("/status?category=time&problems_only=true", follow_redirects=True)
    assert r.status_code == 200
    assert 'time-kpi--error' in r.text
    assert "time-problem-row--error" in r.text


def test_objects_page_has_inventory_kpi_not_dashboard_stack(client: TestClient) -> None:
    store = app.dependency_overrides[get_store]()
    store.update_credentials("admin", "secret")
    store.create_recorder(
        RecorderCreate(
            object_name="Obj",
            host="10.0.0.1",
            port=80,
            use_https=False,
        )
    )
    r = client.get("/monitoring")
    assert r.status_code == 200
    assert "fleet-overview" in r.text
    assert "object-health-matrix" in r.text
    assert "health-dashboard-stack" not in r.text
    assert "inventory-view-tabs" in r.text
    assert "Сводка мониторинга" in r.text
    assert "Объектов" in r.text
    assert "Исправность" in r.text


def test_status_page_has_category_dashboard_stack(client: TestClient) -> None:
    store = app.dependency_overrides[get_store]()
    store.update_credentials("admin", "secret")
    store.create_recorder(
        RecorderCreate(
            object_name="Obj",
            host="10.0.0.1",
            port=80,
            use_https=False,
        )
    )
    r = client.get("/status", follow_redirects=True)
    assert r.status_code == 200
    assert "status-overview" in r.text
    assert "Исправность парка" in r.text
    assert "health-dashboard-stack" in r.text
    assert "category-dashboard-temperature" in r.text


def test_objects_fleet_category_chip_links(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from datetime import datetime, timezone

    store = app.dependency_overrides[get_store]()
    rec = store.create_recorder(
        RecorderCreate(
            object_name="ВСП-1",
            host="10.0.0.1",
            port=80,
            use_https=False,
        )
    )
    state = app.dependency_overrides[get_state_store]()
    state.upsert_recorder_metrics(
        rec.id,
        device_online=True,
        health_status="warn",
        disks=[{"TemperatureCelsius": 55}],
        last_polled_at=datetime.now(timezone.utc),
    )

    page = client.get("/monitoring")
    assert "category=temperature" in page.text
    assert "problems_only=true" in page.text
    assert "TEMP:" in page.text

    status = client.get("/status?category=temperature&problems_only=true", follow_redirects=True)
    assert status.status_code == 200
    assert "category-dashboard-temperature" in status.text


def test_status_top_problem_objects(
    client: TestClient,
) -> None:
    from datetime import datetime, timezone

    store = app.dependency_overrides[get_store]()
    rec = store.create_recorder(
        RecorderCreate(
            object_name="Проблемный объект",
            host="10.0.0.9",
            port=80,
            use_https=False,
        )
    )
    state = app.dependency_overrides[get_state_store]()
    state.upsert_recorder_metrics(
        rec.id,
        device_online=True,
        health_status="error",
        ntp_status="Fail",
        sync_type="Manual",
        last_polled_at=datetime.now(timezone.utc),
    )

    r = client.get("/status", follow_redirects=True)
    assert "top-problem-objects" in r.text
    assert "Проблемный объект" in r.text
    assert 'href="/monitoring?object=' in r.text


def test_objects_health_matrix_deep_link_without_object_groups_hash(
    client: TestClient,
) -> None:
    from datetime import datetime, timezone

    object_name = "г. Тест, ул. Пример, д. 1"
    store = app.dependency_overrides[get_store]()
    rec = store.create_recorder(
        RecorderCreate(
            object_name=object_name,
            host="10.0.0.10",
            port=80,
            use_https=False,
        )
    )
    state = app.dependency_overrides[get_state_store]()
    state.upsert_recorder_metrics(
        rec.id,
        device_online=True,
        health_status="error",
        ntp_status="Fail",
        sync_type="Manual",
        last_polled_at=datetime.now(timezone.utc),
    )

    r = client.get("/monitoring")
    assert r.status_code == 200
    assert "Проблемы по объектам" in r.text
    expected_href = f'/monitoring?object={quote(object_name)}">'
    assert expected_href in r.text
    assert f'/monitoring?object={quote(object_name)}#object-groups">' not in r.text


def test_objects_dashboard_nvr_column_shows_ip(client: TestClient) -> None:
    from datetime import datetime, timezone

    store = app.dependency_overrides[get_store]()
    store.update_credentials("admin", "secret")
    rec = store.create_recorder(
        RecorderCreate(
            object_name="ВСП-001",
            name="NVR-корпус",
            host="192.168.1.10",
            port=80,
            use_https=False,
        )
    )
    state = app.dependency_overrides[get_state_store]()
    state.upsert_recorder_metrics(
        rec.id,
        device_online=True,
        health_status="warn",
        health_reason="Температура HDD выше порога",
        disks=[{"TemperatureCelsius": 55}],
        last_polled_at=datetime.now(timezone.utc),
    )

    r = client.get("/monitoring")
    assert r.status_code == 200
    assert "NVR-корпус" in r.text
    assert "192.168.1.10" in r.text

    status_page = client.get("/status?category=temperature", follow_redirects=True)
    assert "category-dashboard-temperature" in status_page.text


def test_objects_export_errors_html(client: TestClient) -> None:
    from datetime import datetime, timezone

    store = app.dependency_overrides[get_store]()
    store.update_credentials("admin", "s3cret")
    rec = store.create_recorder(
        RecorderCreate(
            object_name="ВСП-045",
            name="NVR-main",
            host="10.1.2.3",
            port=80,
            use_https=False,
        )
    )
    state = app.dependency_overrides[get_state_store]()
    state.upsert_recorder_metrics(
        rec.id,
        device_online=True,
        health_status="warn",
        health_reason="Температура HDD выше порога",
        disks=[{"TemperatureCelsius": 55}],
        last_polled_at=datetime.now(timezone.utc),
    )

    r = client.get("/summary/export/errors.html")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")
    assert "attachment" in r.headers.get("content-disposition", "").lower()
    assert "wisenet-tso-errors-" in r.headers.get("content-disposition", "")
    assert "Отчёт о неисправностях ТСО" in r.text
    assert "NVR-main" in r.text
    assert 'href="http://admin:s3cret@10.1.2.3"' in r.text
    assert "Открыть web-интерфейс NVR" in r.text
    assert "Температура" in r.text
    assert "Автоавторизация включена" not in r.text
    assert "Не пересылайте файл" not in r.text
    assert "Режим ссылок на NVR" not in r.text

    legacy = client.get("/monitoring/export/errors.html", follow_redirects=False)
    assert legacy.status_code == 302
    assert legacy.headers["location"] == "/summary/export/errors.html"

    page = client.get("/summary")
    assert "Экспорт отчета" in page.text
    assert "/summary/export/errors.html" in page.text
    assert "/summary/report/email" in page.text
    assert "Отправить отчёт на почту" in page.text
    assert "Экспорт отчёта по ошибкам" not in page.text
    assert "Экспорт с авто-входом" not in page.text

    monitoring_page = client.get("/monitoring")
    assert "Экспорт отчета" in monitoring_page.text
    assert "Автообновление" in monitoring_page.text
    assert "Опросить все устройства" in monitoring_page.text


def test_objects_report_email_post(client: TestClient) -> None:
    from unittest.mock import patch

    from app.report_delivery import SendResult

    with patch("app.report_delivery.ReportDeliveryService") as svc_cls:
        svc_cls.return_value.send_report_now.return_value = SendResult(
            ok=True,
            message="Отчёт отправлен на a@test",
        )
        r = client.post(
            "/objects/report/email",
            headers={"HX-Request": "true"},
        )
    assert r.status_code == 200
    assert "HX-Redirect" in r.headers
    assert "toast=success" in r.headers["HX-Redirect"]
    svc_cls.return_value.send_report_now.assert_called_once_with(trigger="manual")


def test_objects_table_view(client: TestClient) -> None:
    store = app.dependency_overrides[get_store]()
    store.create_recorder(
        RecorderCreate(
            object_name="ВСП-1",
            host="10.0.0.2",
            port=80,
            use_https=False,
        )
    )
    r = client.get("/monitoring?view=table")
    assert r.status_code == 200
    assert "recorders-table-body" in r.text
    assert "Таблица устройств" in r.text
    assert "data-object-group" not in r.text
    assert "fleet-overview" in r.text
    assert "object-health-matrix" not in r.text


def test_recorder_exclude_unexclude(client: TestClient) -> None:
    client.post(
        "/recorders",
        data={
            "object_name": "Obj",
            "name": "NVR",
            "host": "10.0.0.8",
            "port": "80",
            "use_https": "false",
        },
        follow_redirects=True,
    )
    store = app.dependency_overrides[get_store]()
    rid = store.list_recorders()[0].id

    r = client.post(
        f"/recorders/{rid}/exclude",
        headers={
            "HX-Request": "true",
            "HX-Current-URL": "http://127.0.0.1/objects",
        },
    )
    assert r.status_code == 200
    assert "recorder-row--excluded" in r.text
    assert rid in store.load().exclusions.recorder_ids

    r2 = client.post(
        f"/recorders/{rid}/unexclude",
        headers={
            "HX-Request": "true",
            "HX-Current-URL": "http://127.0.0.1/objects",
        },
    )
    assert r2.status_code == 200
    assert rid not in store.load().exclusions.recorder_ids


def test_settings_exclusions_page(client: TestClient) -> None:
    client.post(
        "/recorders",
        data={
            "object_name": "Obj",
            "name": "",
            "host": "10.0.0.9",
            "port": "80",
            "use_https": "false",
        },
        follow_redirects=True,
    )
    store = app.dependency_overrides[get_store]()
    rid = store.list_recorders()[0].id

    page = client.get("/settings/exclusions")
    assert page.status_code == 200
    assert "Исключения из мониторинга" in page.text

    r = client.post(
        "/settings/exclusions",
        data={"recorder_ids": [rid]},
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert rid in store.load().exclusions.recorder_ids


def test_check_blocked_for_excluded(client: TestClient) -> None:
    client.post(
        "/recorders",
        data={
            "object_name": "Obj",
            "name": "",
            "host": "10.0.0.7",
            "port": "80",
            "use_https": "false",
        },
        follow_redirects=True,
    )
    store = app.dependency_overrides[get_store]()
    rid = store.list_recorders()[0].id
    store.add_exclusion(rid)

    r = client.post(f"/recorders/{rid}/check")
    assert r.status_code == 400
