from app.device_kinds import ALL_DEVICE_KINDS, SYSTEM_KIND_LABELS, kind_label, recorder_device_kind
from app.models import Recorder
from app.ui.grouping import build_devices_by_kind


def test_device_kinds_labels() -> None:
    assert len(ALL_DEVICE_KINDS) == 4
    assert kind_label("tsv") == "ТСВ"
    assert SYSTEM_KIND_LABELS["skud"] == "СКУД"


def test_recorder_device_kind_from_model() -> None:
    tsv = Recorder(id="r1", object_name="Obj", host="10.0.0.1", device_kind="tsv")
    skud = Recorder(
        id="r2",
        object_name="Obj",
        host="10.0.0.2",
        device_kind="skud",
    )
    assert recorder_device_kind(tsv) == "tsv"
    assert recorder_device_kind(skud) == "skud"


def test_build_devices_by_kind_splits_by_kind() -> None:
    tsv = Recorder(id="r1", object_name="Obj", host="10.0.0.1", device_kind="tsv")
    skud = Recorder(
        id="r2",
        object_name="Obj",
        host="10.0.0.2",
        device_kind="skud",
    )
    by_kind = build_devices_by_kind([tsv, skud])
    assert len(by_kind["tsv"]) == 1
    assert len(by_kind["skud"]) == 1
    assert by_kind["bio"] == []


def test_build_devices_by_kind_defaults_to_tsv() -> None:
    rec = Recorder(
        id="r1",
        object_name="Obj",
        host="10.0.0.1",
        port=80,
        use_https=False,
    )
    by_kind = build_devices_by_kind([rec])
    assert len(by_kind["tsv"]) == 1
    assert by_kind["skud"] == []
