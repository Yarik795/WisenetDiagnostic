"""Тесты отчёта «Конфигурации NVR/SPD»."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.config_backup import (
    ConfigBackupError,
    ConfigBackupTarget,
    build_object_config_zip,
    config_backup_filename,
    fetch_config_backup,
    object_zip_filename,
    sanitize_filename_part,
)
from app.config_store import ConfigStore
from app.main import app
from app.models import Credentials, RecorderCreate
from app.state_store import CmdbRecordRow, StateStore
from app.ui.dependencies import get_state_store, get_store
from app.ui.device_configs import (
    build_device_config_groups,
    device_configs_page_context,
    filter_device_config_groups,
    find_device_in_groups,
    is_spd_model,
    resolve_object_devices,
)


@pytest.fixture
def config_store(tmp_path: Path) -> ConfigStore:
    store = ConfigStore(path=tmp_path / "config.json")
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
    store.create_recorder(
        RecorderCreate(
            object_name="Объект 2",
            name="NVR-2",
            host="10.2.2.20",
            port=443,
            use_https=True,
            device_kind="tsv",
        )
    )
    return store


@pytest.fixture
def state_store(tmp_path: Path) -> StateStore:
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    with state.replace_cmdb_records() as session:
        session.write_batch(
            [
                CmdbRecordRow(
                    host="10.1.1.40",
                    functional_type="Вспомогательное оборудование",
                    manufacturer="Hanwha",
                    object_name="Объект 1",
                    model_name="SPD-151",
                    mac="AA:BB:CC:DD:EE:04",
                    device_kind=None,
                    source_row=1,
                ),
                CmdbRecordRow(
                    host="10.1.1.50",
                    functional_type="Вспомогательное оборудование",
                    manufacturer="Hanwha",
                    object_name="Объект 1",
                    model_name="Switch-24",
                    mac="AA:BB:CC:DD:EE:05",
                    device_kind=None,
                    source_row=2,
                ),
                CmdbRecordRow(
                    host="10.2.2.40",
                    functional_type="Вспомогательное оборудование",
                    manufacturer="Hanwha",
                    object_name="Объект 2",
                    model_name="spd-150",
                    mac="AA:BB:CC:DD:EE:06",
                    device_kind=None,
                    source_row=3,
                ),
            ]
        )
    return state


def test_is_spd_model() -> None:
    assert is_spd_model("SPD-151")
    assert is_spd_model("spd-150")
    assert not is_spd_model("Switch-24")
    assert not is_spd_model(None)


def test_build_device_config_groups(config_store: ConfigStore, state_store: StateStore) -> None:
    groups = build_device_config_groups(config_store, state_store)
    assert len(groups) == 2

    obj1 = next(group for group in groups if group.object_name == "Объект 1")
    assert len(obj1.nvrs) == 1
    assert obj1.nvrs[0].host == "10.1.1.10"
    assert len(obj1.spd_devices) == 1
    assert obj1.spd_devices[0].model == "SPD-151"

    obj2 = next(group for group in groups if group.object_name == "Объект 2")
    assert len(obj2.nvrs) == 1
    assert obj2.nvrs[0].use_https is True
    assert len(obj2.spd_devices) == 1


def test_filter_device_config_groups(config_store: ConfigStore, state_store: StateStore) -> None:
    groups = build_device_config_groups(config_store, state_store)
    filtered = filter_device_config_groups(groups, "SPD-151")
    assert len(filtered) == 1
    assert filtered[0].object_name == "Объект 1"
    assert len(filtered[0].nvrs) == 0
    assert len(filtered[0].spd_devices) == 1


def test_find_device_in_groups(config_store: ConfigStore, state_store: StateStore) -> None:
    groups = build_device_config_groups(config_store, state_store)
    device = find_device_in_groups(
        groups,
        object_name="Объект 1",
        kind="spd",
        host="10.1.1.40",
    )
    assert device is not None
    assert device.model == "SPD-151"
    assert find_device_in_groups(
        groups,
        object_name="Объект 1",
        kind="spd",
        host="10.9.9.9",
    ) is None


def test_resolve_object_devices(config_store: ConfigStore, state_store: StateStore) -> None:
    groups = build_device_config_groups(config_store, state_store)
    devices = resolve_object_devices(groups, "Объект 1")
    assert len(devices) == 2
    kinds = {device.kind for device in devices}
    assert kinds == {"nvr", "spd"}


def test_device_configs_page_context(config_store: ConfigStore, state_store: StateStore) -> None:
    ctx = device_configs_page_context(config_store, state_store)
    assert ctx["device_configs_has_data"] is True
    assert ctx["device_configs_object_count"] == 2
    assert ctx["device_configs_device_count"] == 4


def test_filename_helpers() -> None:
    assert sanitize_filename_part("ул. Ленина, 1") == "ул._Ленина,_1"
    assert config_backup_filename("Объект 1", "nvr", "10.1.1.10") == "Объект_1_nvr_10-1-1-10.bin"
    assert object_zip_filename("Объект 1") == "Объект_1_configs.zip"


@pytest.mark.asyncio
async def test_fetch_config_backup_success() -> None:
    credentials = Credentials(username="admin", password="secret")

    class FakeResponse:
        status_code = 200
        content = b"\x00\x01binary"

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, url, auth=None):
            assert "configbackup" in url
            return FakeResponse()

    with patch("app.config_backup.httpx.AsyncClient", return_value=FakeClient()):
        content = await fetch_config_backup("10.1.1.10", 80, False, credentials)
    assert content == b"\x00\x01binary"


@pytest.mark.asyncio
async def test_fetch_config_backup_auth_error() -> None:
    credentials = Credentials(username="admin", password="secret")

    class FakeResponse:
        status_code = 401
        content = b"Unauthorized"

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, url, auth=None):
            return FakeResponse()

    with patch("app.config_backup.httpx.AsyncClient", return_value=FakeClient()):
        with pytest.raises(ConfigBackupError, match="авторизации"):
            await fetch_config_backup("10.1.1.10", 80, False, credentials)


@pytest.mark.asyncio
async def test_build_object_config_zip_partial_errors() -> None:
    credentials = Credentials(username="admin", password="secret")
    targets = [
        ConfigBackupTarget("Объект 1", "nvr", "10.1.1.10"),
        ConfigBackupTarget("Объект 1", "spd", "10.1.1.40"),
    ]

    async def fake_fetch(target: ConfigBackupTarget, creds: Credentials) -> bytes:
        if target.host == "10.1.1.10":
            return b"ok"
        raise ConfigBackupError("недоступно")

    with patch(
        "app.config_backup.fetch_config_backup_for_target",
        new=AsyncMock(side_effect=fake_fetch),
    ):
        zip_bytes, errors = await build_object_config_zip(targets, credentials)

    assert len(errors) == 1
    archive = zipfile.ZipFile(io.BytesIO(zip_bytes))
    names = set(archive.namelist())
    assert "errors.txt" in names
    assert config_backup_filename("Объект 1", "nvr", "10.1.1.10") in names
    assert archive.read(config_backup_filename("Объект 1", "nvr", "10.1.1.10")) == b"ok"


@pytest.fixture
def client(
    tmp_path: Path,
    config_store: ConfigStore,
    state_store: StateStore,
) -> TestClient:
    def override_store() -> ConfigStore:
        return config_store

    def override_state() -> StateStore:
        return state_store

    app.dependency_overrides[get_store] = override_store
    app.dependency_overrides[get_state_store] = override_state
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_device_configs_page_renders(client: TestClient) -> None:
    response = client.get("/device-configs")
    assert response.status_code == 200
    assert "Конфигурации NVR/SPD" in response.text
    assert "SPD-151" in response.text
    assert "NVR-1" in response.text


def test_device_configs_download_single(client: TestClient) -> None:
    with patch(
        "app.web.routes.fetch_config_backup_for_target",
        new=AsyncMock(return_value=b"backup-data"),
    ):
        response = client.get(
            "/device-configs/download",
            params={"object": "Объект 1", "kind": "nvr", "host": "10.1.1.10"},
        )
    assert response.status_code == 200
    assert response.content == b"backup-data"
    disposition = response.headers.get("content-disposition", "")
    assert "attachment" in disposition
    assert "10-1-1-10.bin" in disposition


def test_device_configs_download_zip(client: TestClient) -> None:
    with patch(
        "app.web.routes.build_object_config_zip",
        new=AsyncMock(return_value=(b"zip-bytes", [])),
    ):
        response = client.get(
            "/device-configs/download",
            params={"object": "Объект 1", "kind": "all"},
        )
    assert response.status_code == 200
    assert response.content == b"zip-bytes"
    assert response.headers.get("content-type") == "application/zip"


def test_device_configs_download_unknown_device(client: TestClient) -> None:
    response = client.get(
        "/device-configs/download",
        params={"object": "Объект 1", "kind": "spd", "host": "10.9.9.9"},
    )
    assert response.status_code == 404
    assert "не найдено" in response.text.lower()
