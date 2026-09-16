from datetime import datetime, timezone

from app.inex_lockers import (
    IDENT_CARD,
    InexCabinet,
    InexLocker,
    InexLockersSnapshot,
    InexNotice,
    InexPanel,
)
from app.locker_health import build_locker_snapshot, evaluate_locker_health
from app.models import MonitoringSettings, Recorder
from app.pridex_adb import PridexAdbInfo, TOUCH_VID_PID, UsbDevice


def _settings() -> MonitoringSettings:
    return MonitoringSettings()


def _recorder() -> Recorder:
    return Recorder(
        id="lkr-1",
        object_name="Объект",
        host="10.0.0.9",
        port=5555,
        device_kind="lockers",
        inex_panel_id=7,
    )


def _inex(*, cells: list[InexLocker] | None = None, notices=None, issues=None, cabinet_state="online"):
    cabinet = InexCabinet(
        id=10,
        name="Шкаф А",
        controller_type=1,
        identification_method=IDENT_CARD,
        cabinet_state=cabinet_state,
    )
    panel = InexPanel(id=7, name="Панель", cabinet_id=10, ip="10.0.0.9")
    return InexLockersSnapshot(
        api_ok=True,
        cabinets=[cabinet],
        panels=[panel],
        lockers=cells or [],
        notifications=notices or [],
        issues=issues or [],
    )


def test_evaluate_offline_panel() -> None:
    snapshot = {
        "locker_model": "Pridex",
        "ping_ok": False,
        "ping_error": "timeout",
        "api_ok": True,
        "adb_ok": False,
        "cabinet_id": 10,
        "cells": [],
        "usb": [],
        "notifications": [],
        "issues": [],
    }
    status, reason, enriched = evaluate_locker_health(snapshot, _settings())
    assert status == "error"
    assert enriched["categories"]["panel"] == "error"
    assert "timeout" in (reason or "")


def test_evaluate_usb_rfid_missing() -> None:
    adb = PridexAdbInfo(
        ok=True,
        wakefulness="Awake",
        focus="ru.inexdigital.panel/.MainActivity",
        usb=[UsbDevice(vid=TOUCH_VID_PID[0], pid=TOUCH_VID_PID[1], label="тач")],
    )
    raw = build_locker_snapshot(
        _recorder(),
        locker_model="Pridex",
        ping_ok=True,
        ping_error=None,
        inex=_inex(),
        adb=adb,
    )
    status, reason, enriched = evaluate_locker_health(raw, _settings())
    assert enriched["categories"]["usb"] == "error"
    assert status == "error"
    assert reason and "RFID" in reason


def test_evaluate_cell_disconnected() -> None:
    cells = [
        InexLocker(
            id=i,
            cabinet_id=10,
            display_no=str(i),
            locker_type=0,
            status=2 if i <= 3 else 1,
            reserve_status=0,
            is_active=1,
            status_from_detail=True,
        )
        for i in range(1, 9)
    ]
    raw = build_locker_snapshot(
        _recorder(),
        locker_model="Pridex",
        ping_ok=True,
        ping_error=None,
        inex=_inex(cells=cells),
        adb=None,
    )
    status, _reason, enriched = evaluate_locker_health(raw, _settings())
    assert enriched["categories"]["cells"] == "error"
    assert status == "error"


def test_evaluate_open_issues_are_warn() -> None:
    issues = [InexNotice(id=1, cabinet_id=10, text="Нет бумаги", created_at="2026-01-01")]
    cells = [
        InexLocker(
            id=1,
            cabinet_id=10,
            display_no="1",
            locker_type=0,
            status=1,
            reserve_status=0,
            is_active=1,
            status_from_detail=True,
        )
    ]
    adb = PridexAdbInfo(
        ok=True,
        wakefulness="Awake",
        focus="ru.inexdigital.panel/.MainActivity",
        usb=[
            UsbDevice(vid=TOUCH_VID_PID[0], pid=TOUCH_VID_PID[1], label="тач"),
            UsbDevice(vid=0x0403, pid=0x6001, label="GTUSB"),
        ],
    )
    raw = build_locker_snapshot(
        _recorder(),
        locker_model="Pridex",
        ping_ok=True,
        ping_error=None,
        inex=_inex(cells=cells, issues=issues),
        adb=adb,
    )
    status, reason, enriched = evaluate_locker_health(raw, _settings())
    assert enriched["categories"]["issues"] == "warn"
    assert status == "warn"
    assert reason and "заяв" in reason.lower()


def test_list_status_unknown_not_treated_as_warn() -> None:
    cells = [
        InexLocker(
            id=1,
            cabinet_id=10,
            display_no="1",
            locker_type=0,
            status=3,
            reserve_status=0,
            is_active=1,
            status_from_detail=False,
        )
    ]
    snapshot = build_locker_snapshot(
        _recorder(),
        locker_model="Pridex",
        ping_ok=True,
        ping_error=None,
        inex=_inex(cells=cells),
        adb=None,
    )
    _status, _reason, enriched = evaluate_locker_health(snapshot, _settings())
    assert enriched["categories"]["cells"] == "ok"
    assert _status == "ok"


def test_cabinet_offline_is_controller_error() -> None:
    snapshot = build_locker_snapshot(
        _recorder(),
        locker_model="Pridex",
        ping_ok=True,
        ping_error=None,
        inex=_inex(cabinet_state="offline"),
        adb=None,
        now=datetime.now(timezone.utc),
    )
    status, _reason, enriched = evaluate_locker_health(snapshot, _settings())
    assert enriched["categories"]["controller"] == "error"
    assert status == "error"
