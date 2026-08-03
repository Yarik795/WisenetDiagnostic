"""Справочник производителя камеры по модели NVR и признаки аналогового канала."""

from __future__ import annotations

from typing import Optional

from .state_store import ChannelRow

ANALOG_MODEL_LABEL = "Аналоговая камера"

CAMERA_BRAND_LABELS: dict[str, str] = {
    "dahua": "Dahua",
    "hanwha": "Hanwha/Samsung",
    "bosch": "Bosch",
    "trassir": "Trassir",
    "analog": "Аналоговая",
    "other": "Прочие",
    "unknown": "Неизвестно",
}

_RAW_MODEL_MANUFACTURERS: dict[str, str] = {
    "FLEXIDOME IP 4000i IR": "bosch",
    "LND-6012R": "hanwha",
    "PNF-9010R": "hanwha",
    "QND-6070R": "hanwha",
    "QND-6082R": "hanwha",
    "QNO-6014R": "hanwha",
    "QNP-6250R": "hanwha",
    "QNV-6082R": "hanwha",
    "TR-D4D2V2": "trassir",
    "Unknown": "analog",
    "Wisenet CAM": "hanwha",
    "XNZ-L6320A": "hanwha",
}

_MODEL_PREFIX_MANUFACTURERS: tuple[tuple[str, str], ...] = (
    ("dh-ipc", "dahua"),
    ("tr-d", "trassir"),
)

CAMERA_MODEL_MANUFACTURERS: dict[str, str] = {
    key.casefold(): value for key, value in _RAW_MODEL_MANUFACTURERS.items()
}


def _normalize_model(model: Optional[str]) -> str:
    return (model or "").strip().casefold()


def _is_unknown_model(model: Optional[str]) -> bool:
    return _normalize_model(model) == "unknown"


def _is_analog_by_channel_state(channel: ChannelRow) -> bool:
    if (channel.camera_ip or "").strip():
        return False
    state = (channel.source_state or "").strip().lower()
    if state == "deactive":
        return False
    if state:
        return True
    return bool((channel.name or "").strip())


def is_analog_camera_channel(channel: ChannelRow) -> bool:
    """Аналоговый вход: модель Unknown или активный канал без IP."""
    if _is_unknown_model(channel.camera_model):
        return True
    return _is_analog_by_channel_state(channel)


def manufacturer_from_model(model: Optional[str]) -> Optional[str]:
    key = _normalize_model(model)
    if not key:
        return None
    exact = CAMERA_MODEL_MANUFACTURERS.get(key)
    if exact:
        return exact
    for prefix, manufacturer in _MODEL_PREFIX_MANUFACTURERS:
        if key.startswith(prefix):
            return manufacturer
    return None


def camera_brand_label(brand: str) -> str:
    return CAMERA_BRAND_LABELS.get(brand, brand)


def resolve_camera_manufacturer(channel: ChannelRow) -> str:
    from_model = manufacturer_from_model(channel.camera_model)
    if from_model:
        return from_model
    stored = (channel.manufacturer or "").strip().lower()
    if stored and stored != "unknown":
        return stored
    return "unknown"


def resolve_camera_model_display(channel: ChannelRow) -> Optional[str]:
    if is_analog_camera_channel(channel):
        return ANALOG_MODEL_LABEL
    model = (channel.camera_model or "").strip()
    return model or None
