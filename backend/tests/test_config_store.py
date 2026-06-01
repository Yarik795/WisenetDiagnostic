import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.config_store import ConfigStore, RecorderStatusUpdate
from app.models import CheckStatus, RecorderCreate


@pytest.fixture
def store(tmp_path: Path) -> ConfigStore:
    return ConfigStore(path=tmp_path / "config.json")


def _create(store: ConfigStore, host: str, object_name: str = "A") -> object:
    return store.create_recorder(
        RecorderCreate(
            object_name=object_name,
            host=host,
            port=80,
            use_https=False,
        )
    )


def test_load_empty(store: ConfigStore) -> None:
    config = store.load()
    assert config.recorders == []
    assert config.credentials.username == ""
    assert config.exclusions.recorder_ids == []


def test_create_and_list(store: ConfigStore) -> None:
    created = store.create_recorder(
        RecorderCreate(
            object_name="Отделение №12",
            name="NVR-1",
            host="10.1.2.3",
            port=80,
            use_https=False,
        )
    )
    assert created.object_name == "Отделение №12"
    assert len(store.list_recorders()) == 1


def test_atomic_save(store: ConfigStore) -> None:
    _create(store, "1.1.1.1")
    data = json.loads(store.path.read_text(encoding="utf-8"))
    assert len(data["recorders"]) == 1
    assert "exclusions" in data


def test_update_and_delete(store: ConfigStore) -> None:
    r = _create(store, "1.1.1.1")
    updated = store.update_recorder(
        r.id,
        RecorderCreate(
            object_name="B",
            host="2.2.2.2",
            port=443,
            use_https=True,
        ),
    )
    assert updated is not None
    assert updated.object_name == "B"
    assert updated.use_https is True
    assert store.delete_recorder(r.id) is True
    assert store.list_recorders() == []
    assert store.load().exclusions.recorder_ids == []


def test_migrate_enabled_false_to_exclusions(store: ConfigStore) -> None:
    store.path.write_text(
        json.dumps(
            {
                "recorders": [
                    {
                        "id": "nvr-old",
                        "object_name": "Obj",
                        "host": "1.2.3.4",
                        "port": 80,
                        "use_https": False,
                        "enabled": False,
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    config = store.load()
    assert "nvr-old" in config.exclusions.recorder_ids
    assert not hasattr(config.recorders[0], "enabled")


def test_exclusion_add_remove(store: ConfigStore) -> None:
    r = _create(store, "1.1.1.1")
    assert store.add_exclusion(r.id) is True
    assert r.id in store.load().exclusions.recorder_ids
    assert store.remove_exclusion(r.id) is True
    assert r.id not in store.load().exclusions.recorder_ids


def test_set_exclusions_prunes_unknown(store: ConfigStore) -> None:
    r = _create(store, "1.1.1.1")
    store.set_exclusions([r.id, "ghost-id"])
    assert store.load().exclusions.recorder_ids == [r.id]


def test_update_status(store: ConfigStore) -> None:
    r = _create(store, "1.1.1.1")
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


def test_batch_update_recorder_statuses(store: ConfigStore) -> None:
    r1 = _create(store, "1.1.1.1", "A")
    r2 = _create(store, "2.2.2.2", "B")
    ts = datetime.now(timezone.utc)
    store.update_recorder_statuses(
        [
            RecorderStatusUpdate(r1.id, CheckStatus.ONLINE, ts, None),
            RecorderStatusUpdate(r2.id, CheckStatus.OFFLINE, ts, "fail"),
        ]
    )
    updated1 = store.get_recorder(r1.id)
    updated2 = store.get_recorder(r2.id)
    assert updated1 is not None and updated1.last_status == CheckStatus.ONLINE
    assert updated2 is not None and updated2.last_status == CheckStatus.OFFLINE
    assert updated2.last_error == "fail"


def test_concurrent_status_updates(store: ConfigStore) -> None:
    recorders = [_create(store, f"10.0.0.{i}", f"Obj {i}") for i in range(6)]
    ts = datetime.now(timezone.utc)

    def _update(rec_id: str) -> None:
        store.update_recorder_status(rec_id, CheckStatus.ONLINE, ts, None)

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(_update, r.id) for r in recorders]
        for fut in as_completed(futures):
            fut.result()

    for r in recorders:
        updated = store.get_recorder(r.id)
        assert updated is not None
        assert updated.last_status == CheckStatus.ONLINE
