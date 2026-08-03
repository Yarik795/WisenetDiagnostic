"""Тесты справочника производителя камеры по модели."""

from __future__ import annotations

from app.camera_manufacturer_lookup import (
    ANALOG_MODEL_LABEL,
    is_analog_camera_channel,
    manufacturer_from_model,
    resolve_camera_manufacturer,
    resolve_camera_model_display,
)
from app.state_store import ChannelRow


def _channel(**kwargs) -> ChannelRow:
    defaults = dict(
        id=1,
        recorder_id="nvr-1",
        channel_no=0,
        name="Cam 1",
        camera_ip=None,
        camera_model=None,
        source_state="On",
        health_status="ok",
        health_reason=None,
        video_loss=False,
        last_polled_at=None,
    )
    defaults.update(kwargs)
    return ChannelRow(**defaults)


def test_manufacturer_from_model_hanwha() -> None:
    assert manufacturer_from_model("QND-6070R") == "hanwha"
    assert manufacturer_from_model("qnd-6070r") == "hanwha"


def test_manufacturer_from_model_unknown_is_analog() -> None:
    assert manufacturer_from_model("Unknown") == "analog"
    assert manufacturer_from_model("UNKNOWN") == "analog"


def test_resolve_manufacturer_model_overrides_inventory() -> None:
    ch = _channel(camera_model="QND-6070R", manufacturer="dahua")
    assert resolve_camera_manufacturer(ch) == "hanwha"


def test_resolve_manufacturer_trassir_overrides_other() -> None:
    ch = _channel(camera_model="TR-D4D2V2", manufacturer="other")
    assert resolve_camera_manufacturer(ch) == "trassir"


def test_manufacturer_from_model_dh_ipc_prefix() -> None:
    assert manufacturer_from_model("DH-IPC-HFW1230") == "dahua"
    assert manufacturer_from_model("dh-ipc-hdw2431tp-as-0280b") == "dahua"


def test_manufacturer_from_model_tr_d_prefix() -> None:
    assert manufacturer_from_model("TR-D4D2V2") == "trassir"
    assert manufacturer_from_model("TR-D4D2V2-EXTRA") == "trassir"


def test_resolve_manufacturer_from_model_when_unknown() -> None:
    ch = _channel(camera_model="QND-6070R", manufacturer="unknown")
    assert resolve_camera_manufacturer(ch) == "hanwha"


def test_resolve_manufacturer_from_model_when_missing() -> None:
    ch = _channel(camera_model="TR-D4D2V2", manufacturer=None)
    assert resolve_camera_manufacturer(ch) == "trassir"


def test_resolve_model_display_for_unknown() -> None:
    ch = _channel(camera_model="Unknown", source_state="On")
    assert resolve_camera_model_display(ch) == ANALOG_MODEL_LABEL
    assert resolve_camera_manufacturer(ch) == "analog"


def test_is_analog_camera_channel_without_ip() -> None:
    ch = _channel(camera_ip=None, camera_model="Some model", source_state="On")
    assert is_analog_camera_channel(ch)


def test_is_not_analog_when_has_ip() -> None:
    ch = _channel(camera_ip="10.0.0.5", camera_model="Unknown", source_state="On")
    assert is_analog_camera_channel(ch)
    assert resolve_camera_model_display(ch) == ANALOG_MODEL_LABEL
