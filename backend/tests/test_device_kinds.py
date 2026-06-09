from app.device_kinds import ALL_DEVICE_KINDS, SYSTEM_KIND_LABELS, kind_label
from app.models import Recorder
from app.ui.grouping import build_devices_by_kind


def test_device_kinds_labels() -> None:
    assert len(ALL_DEVICE_KINDS) == 4
    assert kind_label("tsv") == "ТСВ"
    assert SYSTEM_KIND_LABELS["skud"] == "СКУД"


def test_build_devices_by_kind_puts_recorders_under_tsv() -> None:
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
