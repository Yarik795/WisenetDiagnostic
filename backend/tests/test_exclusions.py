from app.exclusions import (
    is_excluded,
    is_pollable,
    migrate_config_raw,
    pollable_recorders,
    prune_exclusions,
)
from app.models import AppConfig, ExclusionSettings, Recorder


def test_migrate_enabled_false() -> None:
    raw = {
        "recorders": [
            {"id": "a", "object_name": "O", "host": "1.1.1.1", "enabled": False},
            {"id": "b", "object_name": "O", "host": "2.2.2.2", "enabled": True},
        ]
    }
    data = migrate_config_raw(raw)
    assert set(data["exclusions"]["recorder_ids"]) == {"a"}
    assert "enabled" not in data["recorders"][0]


def test_pollable_recorders() -> None:
    config = AppConfig(
        recorders=[
            Recorder(id="a", object_name="O", host="1.1.1.1"),
            Recorder(id="b", object_name="O", host="2.2.2.2"),
        ],
        exclusions=ExclusionSettings(recorder_ids=["b"]),
    )
    pollable = pollable_recorders(config)
    assert [r.id for r in pollable] == ["a"]
    assert is_excluded("b", config)
    assert is_pollable(pollable[0], config)


def test_prune_exclusions() -> None:
    config = AppConfig(
        recorders=[Recorder(id="a", object_name="O", host="1.1.1.1")],
        exclusions=ExclusionSettings(recorder_ids=["a", "ghost"]),
    )
    pruned = prune_exclusions(config)
    assert pruned.exclusions.recorder_ids == ["a"]
