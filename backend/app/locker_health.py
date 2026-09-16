"""Правила здоровья панелей локеров Pridex. Транспорт — inex_lockers / pridex_adb."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

from .health import worst_status
from .inex_lockers import (
    CELL_TYPE_PANEL,
    CONTROLLER_LOCKERBOX,
    IDENT_CARD,
    IDENT_FACE,
    InexLockersSnapshot,
    InexLocker,
    LOCK_DISCONNECTED,
    LOCK_OPEN,
    LOCK_UNKNOWN,
    match_panel_cabinet,
)
from .models import MonitoringSettings, Recorder
from .pridex_adb import (
    CAMERA_VID_PID,
    KIOSK_PACKAGE,
    KNOWN_USB,
    LOCK_CONTROLLER_VID_PID,
    RFID_VID_PID,
    TOUCH_VID_PID,
    PridexAdbInfo,
    UsbDevice,
)

LOCKER_CATEGORIES = (
    "api",
    "panel",
    "controller",
    "kiosk",
    "usb",
    "cells",
    "issues",
)

CATEGORY_LABELS = {
    "api": "Inex API",
    "panel": "Панель",
    "controller": "Контроллер",
    "kiosk": "Киоск",
    "usb": "USB",
    "cells": "Ячейки",
    "issues": "Заявки",
}

CELL_TYPE_LABELS = {
    0: "гостевой",
    1: "сотрудник",
    2: "панель",
    3: "курьерский",
}

LOCK_STATE_LABELS = {
    0: "открыт",
    1: "закрыт",
    2: "не подключён",
    3: "неизвестно",
}

RESERVE_LABELS = {
    0: "свободен",
    2: "занят",
}


def parse_lockers_json(raw: Optional[str]) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def dump_lockers_json(snapshot: dict[str, Any]) -> str:
    return json.dumps(snapshot, ensure_ascii=False)


def _parse_opened_at(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    text = value.strip()
    if not text or text.lower().startswith("не открывал"):
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _usb_present(devices: list[UsbDevice], pairs: frozenset[tuple[int, int]]) -> bool:
    present = {(d.vid, d.pid) for d in devices}
    return bool(present & pairs)


def _expected_usb(
    *,
    identification_method: Optional[int],
    controller_type: Optional[int],
) -> list[dict[str, Any]]:
    expected: list[dict[str, Any]] = [
        {
            "vid": TOUCH_VID_PID[0],
            "pid": TOUCH_VID_PID[1],
            "label": "тач WingCool",
            "role": "touch",
        }
    ]
    ident = identification_method or 0
    if ident & IDENT_CARD:
        expected.append(
            {
                "vid": 0x0403,
                "pid": 0x6001,
                "label": "RFID GTUSB / Arduino",
                "role": "rfid",
            }
        )
    if ident & IDENT_FACE:
        expected.append(
            {
                "vid": 0x0BDA,
                "pid": 0x3460,
                "label": "USB RGB/IR камера",
                "role": "camera",
            }
        )
    if controller_type == CONTROLLER_LOCKERBOX:
        expected.append(
            {
                "vid": LOCK_CONTROLLER_VID_PID[0],
                "pid": LOCK_CONTROLLER_VID_PID[1],
                "label": "LockerBox_USB (замки)",
                "role": "locks",
            }
        )
    return expected


def _usb_rows(
    devices: list[UsbDevice],
    expected: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    present_pairs = {(d.vid, d.pid) for d in devices}
    rows: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for item in expected:
        role = item["role"]
        if role == "rfid":
            ok = _usb_present(devices, RFID_VID_PID)
        elif role == "camera":
            ok = _usb_present(devices, CAMERA_VID_PID)
        else:
            ok = (item["vid"], item["pid"]) in present_pairs
        rows.append(
            {
                "vid": f"{item['vid']:04x}",
                "pid": f"{item['pid']:04x}",
                "label": item["label"],
                "role": role,
                "expected": True,
                "present": ok,
            }
        )
        if role == "rfid":
            seen |= RFID_VID_PID
        elif role == "camera":
            seen |= CAMERA_VID_PID
        else:
            seen.add((item["vid"], item["pid"]))
    for device in devices:
        pair = (device.vid, device.pid)
        if pair in seen or pair == (0x2207, 0x0006):
            continue
        rows.append(
            {
                "vid": f"{device.vid:04x}",
                "pid": f"{device.pid:04x}",
                "label": device.label,
                "role": "other",
                "expected": False,
                "present": True,
                "manufacturer": device.manufacturer,
                "product": device.product,
            }
        )
        seen.add(pair)
    return rows


def _cell_dict(cell: InexLocker) -> dict[str, Any]:
    return {
        "id": cell.id,
        "display_no": cell.display_no,
        "type": cell.locker_type,
        "type_label": CELL_TYPE_LABELS.get(cell.locker_type, str(cell.locker_type)),
        "status": cell.status,
        "lock_label": LOCK_STATE_LABELS.get(cell.status or LOCK_UNKNOWN, "—"),
        "reserve_status": cell.reserve_status,
        "reserve_label": RESERVE_LABELS.get(cell.reserve_status or 0, "—"),
        "is_active": cell.is_active,
        "unit_no": cell.unit_no,
        "port_no": cell.port_no,
        "opened_at": cell.opened_at,
        "status_from_detail": cell.status_from_detail,
    }


def build_locker_snapshot(
    recorder: Recorder,
    *,
    locker_model: str,
    ping_ok: bool,
    ping_error: Optional[str],
    inex: Optional[InexLockersSnapshot],
    adb: Optional[PridexAdbInfo],
    now: Optional[datetime] = None,
) -> dict[str, Any]:
    panel, cabinet = (None, None)
    if inex and inex.api_ok:
        panel, cabinet = match_panel_cabinet(
            inex,
            panel_id=recorder.inex_panel_id,
            host=recorder.host,
        )
    cells: list[InexLocker] = []
    if inex and cabinet:
        cells = [c for c in inex.lockers if c.cabinet_id == cabinet.id]
    ident = None
    if panel and panel.identification_method is not None:
        ident = panel.identification_method
    elif cabinet and cabinet.identification_method is not None:
        ident = cabinet.identification_method
    controller_type = cabinet.controller_type if cabinet else None
    usb_devices = list(adb.usb) if adb and adb.ok else []
    expected = _expected_usb(
        identification_method=ident,
        controller_type=controller_type,
    )
    usb_rows = _usb_rows(usb_devices, expected) if adb and adb.ok else []
    notices: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    if inex and cabinet:
        notices = [
            {"id": n.id, "text": n.text, "created_at": n.created_at}
            for n in inex.notifications
            if n.cabinet_id == cabinet.id
        ]
        issues = [
            {"id": n.id, "text": n.text, "created_at": n.created_at}
            for n in inex.issues
            if n.cabinet_id == cabinet.id
        ]
    return {
        "locker_model": locker_model or "",
        "ping_ok": ping_ok,
        "ping_error": ping_error,
        "api_ok": bool(inex and inex.api_ok),
        "api_error": None if inex is None else inex.error,
        "adb_ok": bool(adb and adb.ok),
        "adb_error": None if adb is None else adb.error,
        "panel_id": (panel.id if panel else recorder.inex_panel_id),
        "cabinet_id": cabinet.id if cabinet else None,
        "cabinet_name": cabinet.name if cabinet else None,
        "controller_type": controller_type,
        "controller_ip": cabinet.controller_ip if cabinet else None,
        "controller_port": cabinet.controller_port if cabinet else None,
        "cabinet_state": cabinet.cabinet_state if cabinet else "",
        "identification_method": ident,
        "android": adb.android if adb and adb.ok else "",
        "model": adb.model if adb and adb.ok else "",
        "serial": adb.serial if adb and adb.ok else "",
        "eth0_ip": adb.eth0_ip if adb and adb.ok else "",
        "eth0_mac": adb.eth0_mac if adb and adb.ok else "",
        "focus": adb.focus if adb and adb.ok else "",
        "wakefulness": adb.wakefulness if adb and adb.ok else "",
        "thermal": list(adb.thermal) if adb and adb.ok else [],
        "usb": usb_rows,
        "cells": [_cell_dict(c) for c in cells],
        "notifications": notices,
        "issues": issues,
        "polled_at": (now or datetime.now(timezone.utc)).isoformat(),
    }


def evaluate_locker_health(
    snapshot: dict[str, Any],
    settings: MonitoringSettings,
    *,
    now: Optional[datetime] = None,
) -> tuple[str, Optional[str], dict[str, Any]]:
    ref = now or datetime.now(timezone.utc)
    model = (snapshot.get("locker_model") or "").strip().lower()
    ping_only = model == "lockerbox"
    categories: dict[str, str] = {key: "unknown" for key in LOCKER_CATEGORIES}
    reasons: dict[str, str] = {}

    if ping_only:
        if snapshot.get("ping_ok"):
            categories["panel"] = "ok"
        else:
            categories["panel"] = "error"
            reasons["panel"] = snapshot.get("ping_error") or "нет ответа ping"
        status = categories["panel"]
        reason = reasons.get("panel")
        snapshot = dict(snapshot)
        snapshot["categories"] = categories
        snapshot["category_reasons"] = reasons
        return status, reason, snapshot

    if snapshot.get("api_ok"):
        categories["api"] = "ok"
    else:
        categories["api"] = "error"
        reasons["api"] = snapshot.get("api_error") or "Inex API недоступен"

    if snapshot.get("ping_ok"):
        categories["panel"] = "ok"
    else:
        categories["panel"] = "error"
        reasons["panel"] = snapshot.get("ping_error") or "нет ответа ping"

    notices = snapshot.get("notifications") or []
    lost = [
        n
        for n in notices
        if "потеряна связь" in str(n.get("text") or "").lower()
    ]
    cabinet_offline = (snapshot.get("cabinet_state") or "").lower() == "offline"
    if lost or cabinet_offline:
        categories["controller"] = "error"
        reasons["controller"] = (
            (lost[0].get("text") if lost else None) or "шкаф offline"
        )
    elif snapshot.get("api_ok") and snapshot.get("cabinet_id"):
        categories["controller"] = "ok"
    elif snapshot.get("api_ok"):
        categories["controller"] = "unknown"
        reasons["controller"] = "шкаф не сопоставлен"

    if snapshot.get("adb_ok"):
        wake = (snapshot.get("wakefulness") or "").strip()
        focus = snapshot.get("focus") or ""
        if wake and wake.lower() != "awake":
            categories["kiosk"] = "error"
            reasons["kiosk"] = f"экран {wake}"
        elif KIOSK_PACKAGE not in focus:
            categories["kiosk"] = "error"
            reasons["kiosk"] = "киоск не на переднем плане"
        elif "SettingsActivity" in focus:
            categories["kiosk"] = "warn"
            reasons["kiosk"] = "открыты настройки панели"
        else:
            categories["kiosk"] = "ok"
    else:
        categories["kiosk"] = "unknown"
        if snapshot.get("adb_error"):
            reasons["kiosk"] = str(snapshot.get("adb_error"))

    usb_rows = snapshot.get("usb") or []
    if snapshot.get("adb_ok"):
        missing = [
            row for row in usb_rows if row.get("expected") and not row.get("present")
        ]
        unknown_vid = []
        for row in usb_rows:
            if row.get("expected"):
                continue
            try:
                pair = (int(str(row.get("vid")), 16), int(str(row.get("pid")), 16))
            except (TypeError, ValueError):
                continue
            if pair not in KNOWN_USB:
                unknown_vid.append(row)
        if missing:
            categories["usb"] = "error"
            reasons["usb"] = "нет " + ", ".join(
                str(row.get("label") or row.get("role")) for row in missing
            )
        elif unknown_vid:
            categories["usb"] = "warn"
            reasons["usb"] = "неизвестный обязательный VID"
        else:
            categories["usb"] = "ok"
    else:
        categories["usb"] = "unknown"

    usable_cells = [
        c
        for c in (snapshot.get("cells") or [])
        if int(c.get("type") or 0) != CELL_TYPE_PANEL
    ]
    if snapshot.get("api_ok") and snapshot.get("cabinet_id") is not None:
        disconnected = [
            c for c in usable_cells if c.get("status") == LOCK_DISCONNECTED
        ]
        unknown = [
            c
            for c in usable_cells
            if c.get("status") == LOCK_UNKNOWN and c.get("status_from_detail")
        ]
        open_stale = []
        threshold_min = settings.lockers_door_open_warn_minutes
        for cell in usable_cells:
            if cell.get("status") != LOCK_OPEN:
                continue
            opened = _parse_opened_at(cell.get("opened_at"))
            if opened is None:
                continue
            age_min = (ref - opened).total_seconds() / 60.0
            if age_min >= threshold_min:
                open_stale.append(cell)
        total = len(usable_cells)
        disc_pct = round(100 * len(disconnected) / total) if total else 0
        if total and disc_pct >= settings.lockers_cells_error_threshold_percent:
            categories["cells"] = "error"
            reasons["cells"] = (
                f"не подключено {len(disconnected)} из {total} ячеек ({disc_pct}%)"
            )
        elif unknown or open_stale:
            categories["cells"] = "warn"
            bits = []
            if unknown:
                bits.append(f"{len(unknown)} с неизвестным замком")
            if open_stale:
                bits.append(f"{len(open_stale)} долго открыты")
            reasons["cells"] = "; ".join(bits)
        else:
            categories["cells"] = "ok"
    elif snapshot.get("api_ok"):
        categories["cells"] = "unknown"

    issues = snapshot.get("issues") or []
    if issues:
        categories["issues"] = "warn"
        reasons["issues"] = f"открытых заявок: {len(issues)}"
    elif snapshot.get("api_ok"):
        categories["issues"] = "ok"

    known = [value for value in categories.values() if value != "unknown"]
    status = worst_status(*known) if known else "unknown"
    if status in ("ok", "unknown"):
        reason = reasons.get("panel") or reasons.get("api")
    else:
        reason = next(
            (
                reasons[key]
                for key in LOCKER_CATEGORIES
                if categories.get(key) == status
            ),
            None,
        )
    snapshot = dict(snapshot)
    snapshot["categories"] = categories
    snapshot["category_reasons"] = reasons
    return status, reason, snapshot
