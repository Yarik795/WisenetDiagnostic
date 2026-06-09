from __future__ import annotations

from typing import Literal

DeviceKind = Literal["tsv", "skud", "bio", "sots"]

ALL_DEVICE_KINDS: tuple[DeviceKind, ...] = ("tsv", "skud", "bio", "sots")

SYSTEM_KIND_LABELS: dict[DeviceKind, str] = {
    "tsv": "ТСВ",
    "skud": "СКУД",
    "bio": "Биотерминалы",
    "sots": "СОТС",
}

SOURCE_KEY_LABELS: dict[str, str] = {
    "cmdb": "CMDB",
    "arsenal": "Арсенал",
    "smartview": "Smartview",
    "budget": "Бюджет",
}


def kind_label(kind: str) -> str:
    return SYSTEM_KIND_LABELS.get(kind, kind)  # type: ignore[arg-type]


def source_label(source_key: str) -> str:
    return SOURCE_KEY_LABELS.get(source_key, source_key)


CMDB_MANAGED_KINDS: tuple[DeviceKind, ...] = ("tsv", "skud", "bio")


def recorder_device_kind(recorder: object) -> DeviceKind:
    kind = getattr(recorder, "device_kind", None)
    return kind if kind in ALL_DEVICE_KINDS else "tsv"
