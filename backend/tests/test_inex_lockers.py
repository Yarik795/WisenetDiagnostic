from app.inex_lockers import (
    InexLockersSnapshot,
    match_panel_cabinet,
    parse_cabinets_payload,
    parse_locker_status_payload,
    parse_lockers_payload,
    parse_notices_payload,
    parse_panels_payload,
)

CABINETS_FIXTURE = {
    "data": {
        "cabinets": [
            {
                "id": 10,
                "name": "Шкаф А",
                "controllerType": 1,
                "controllerIp": "10.0.0.5",
                "controllerPort": 5000,
                "identificationMethod": [4],
                "cabinetState": "online",
            }
        ]
    },
    "error": None,
}

LOCKERS_FIXTURE = {
    "data": {
        "lockers": [
            {
                "id": 1,
                "cabinetId": 10,
                "displayNo": "1",
                "type": 0,
                "status": 3,
                "reserveStatus": 0,
                "isActive": 1,
                "openedAtDt": None,
            },
            {
                "id": 2,
                "cabinetId": 10,
                "displayNo": "P",
                "type": 2,
                "status": 1,
                "reserveStatus": 0,
                "isActive": 1,
            },
            {
                "id": 3,
                "cabinetId": 10,
                "displayNo": "3",
                "type": 0,
                "status": 2,
                "reserveStatus": 2,
                "isActive": 1,
                "openedAtDt": "2026-01-01T12:00:00Z",
            },
        ]
    },
    "error": None,
}

PANELS_FIXTURE = {
    "data": {
        "panels": [
            {
                "id": 7,
                "name": "Панель 1",
                "cabinetId": 10,
                "ip": "10.0.0.9",
                "port": 5555,
            }
        ]
    },
    "error": None,
}

NOTIFICATIONS_FIXTURE = {
    "data": {
        "securityNotifications": [
            {
                "id": 41,
                "cabinetId": 10,
                "text": "Потеряна связь со шкафом",
                "createdAt": "2026-01-01T12:00:00Z",
                "status": 1,
            }
        ]
    },
    "error": None,
}


def test_parse_cabinets_payload() -> None:
    cabinets = parse_cabinets_payload(CABINETS_FIXTURE)
    assert len(cabinets) == 1
    assert cabinets[0].id == 10
    assert cabinets[0].name == "Шкаф А"
    assert cabinets[0].controller_type == 1
    assert cabinets[0].controller_ip == "10.0.0.5"
    assert cabinets[0].identification_method == 4
    assert cabinets[0].cabinet_state == "online"


def test_parse_lockers_payload() -> None:
    lockers = parse_lockers_payload(LOCKERS_FIXTURE)
    assert [row.display_no for row in lockers] == ["1", "P", "3"]
    assert lockers[1].locker_type == 2
    assert lockers[2].status == 2
    assert lockers[2].opened_at == "2026-01-01T12:00:00Z"


def test_parse_notifications_payload() -> None:
    notes = parse_notices_payload(NOTIFICATIONS_FIXTURE, "securityNotifications")
    assert len(notes) == 1
    assert notes[0].cabinet_id == 10
    assert "Потеряна связь" in notes[0].text


def test_parse_locker_status_payload() -> None:
    assert parse_locker_status_payload({"data": {"status": 0}, "error": None}) == 0
    assert parse_locker_status_payload({"data": {"locker": {"status": 1}}}) == 1
    assert parse_locker_status_payload({"data": {"lockState": 2}}) == 2


def test_match_panel_cabinet_by_panel_id() -> None:
    snapshot = InexLockersSnapshot(
        api_ok=True,
        cabinets=parse_cabinets_payload(CABINETS_FIXTURE),
        lockers=parse_lockers_payload(LOCKERS_FIXTURE),
        panels=parse_panels_payload(PANELS_FIXTURE),
    )
    panel, cabinet = match_panel_cabinet(snapshot, panel_id=7, host="10.9.9.9")
    assert panel is not None and panel.id == 7
    assert cabinet is not None and cabinet.id == 10


def test_match_panel_cabinet_by_ip() -> None:
    snapshot = InexLockersSnapshot(
        api_ok=True,
        cabinets=parse_cabinets_payload(CABINETS_FIXTURE),
        lockers=parse_lockers_payload(LOCKERS_FIXTURE),
        panels=parse_panels_payload(PANELS_FIXTURE),
    )
    panel, cabinet = match_panel_cabinet(snapshot, panel_id=None, host="10.0.0.9")
    assert panel is not None and panel.id == 7
    assert cabinet is not None and cabinet.id == 10
