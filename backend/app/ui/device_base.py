"""Контекст страницы «База устройств»."""

from __future__ import annotations

from typing import Any, Optional

from ..device_base import (
    DEVICE_TYPE_LABELS,
    DEVICE_TYPES,
    LOCKER_MODELS,
    DeviceBaseFormData,
    list_device_addresses,
    list_devices,
)
from ..state_store import DeviceBaseRow, StateStore


def device_base_page_context(
    state: StateStore,
    *,
    search: str = "",
    device_type: str = "",
) -> dict[str, Any]:
    rows = list_devices(state, search=search, device_type=device_type)
    return {
        "device_base_search": search,
        "device_base_type": device_type,
        "device_base_rows": rows,
        "device_base_count": len(rows),
        "device_types": DEVICE_TYPES,
        "device_type_labels": DEVICE_TYPE_LABELS,
        "locker_models": LOCKER_MODELS,
        "address_options": list_device_addresses(state),
    }


def device_base_form_context(
    state: StateStore,
    *,
    device: Optional[DeviceBaseRow] = None,
    form: Optional[DeviceBaseFormData] = None,
    errors: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    return {
        "device": device,
        "form": form,
        "errors": errors,
        "device_types": DEVICE_TYPES,
        "device_type_labels": DEVICE_TYPE_LABELS,
        "locker_models": LOCKER_MODELS,
        "address_options": list_device_addresses(state),
    }
