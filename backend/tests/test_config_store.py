import json
from pathlib import Path

import pytest

from app.config_store import ConfigStore
from app.models import CheckStatus, RecorderCreate


@pytest.fixture
def store(tmp_path: Path) -> ConfigStore:
    return ConfigStore(path=tmp_path / "config.json")


def test_load_empty(store: ConfigStore) -> None:
    config = store.load()
    assert config.recorders == []
    assert config.credentials.username == ""


def test_create_and_list(store: ConfigStore) -> None:
    created = store.create_recorder(
        RecorderCreate(
            object_name="Отделение №12",
            name="NVR-1",
            host="10.1.2.3",
            port=80,
            use_https=False,
            enabled=True,
        )
    )
    assert created.object_name == "Отделение №12"
    assert len(store.list_recorders()) == 1


def test_atomic_save(store: ConfigStore) -> None:
    store.create_recorder(
        RecorderCreate(
            object_name="A",
            host="1.1.1.1",
            port=80,
            use_https=False,
            enabled=True,
        )
    )
    data = json.loads(store.path.read_text(encoding="utf-8"))
    assert len(data["recorders"]) == 1


def test_update_and_delete(store: ConfigStore) -> None:
    r = store.create_recorder(
        RecorderCreate(
            object_name="A",
            host="1.1.1.1",
            port=80,
            use_https=False,
            enabled=True,
        )
    )
    updated = store.update_recorder(
        r.id,
        RecorderCreate(
            object_name="B",
            host="2.2.2.2",
            port=443,
            use_https=True,
            enabled=False,
        ),
    )
    assert updated is not None
    assert updated.object_name == "B"
    assert updated.use_https is True
    assert store.delete_recorder(r.id) is True
    assert store.list_recorders() == []


def test_update_status(store: ConfigStore) -> None:
    from datetime import datetime, timezone

    r = store.create_recorder(
        RecorderCreate(
            object_name="A",
            host="1.1.1.1",
            port=80,
            use_https=False,
            enabled=True,
        )
    )
    ts = datetime.now(timezone.utc)
    updated = store.update_recorder_status(
        r.id, CheckStatus.ONLINE, ts, error=None
    )
    assert updated is not None
    assert updated.last_status == CheckStatus.ONLINE
    assert updated.last_check_at == ts


def test_credentials(store: ConfigStore) -> None:
    creds = store.update_credentials("admin", "secret")
    assert creds.username == "admin"
    assert store.get_credentials().password == "secret"
