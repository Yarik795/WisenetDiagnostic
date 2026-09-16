"""Клиент Inex Lockers API v1: только транспорт и парсинг, без правил здоровья."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Optional
from urllib.parse import urljoin

import httpx

from .logging_config import get_logger

logger = get_logger("inex_lockers")

CELL_TYPE_PANEL = 2
LOCK_OPEN = 0
LOCK_CLOSED = 1
LOCK_DISCONNECTED = 2
LOCK_UNKNOWN = 3

IDENT_FACE = 0x01
IDENT_PIN = 0x02
IDENT_CARD = 0x04
IDENT_QR = 0x08

CONTROLLER_KERONG = 1
CONTROLLER_LOCKERBOX = 2


@dataclass
class InexCabinet:
    id: int
    name: str
    controller_type: Optional[int] = None
    controller_ip: str = ""
    controller_port: Optional[int] = None
    available_lockers: Optional[int] = None
    zone: str = ""
    floor: str = ""
    cabinet_type: Optional[int] = None
    identification_method: Optional[int] = None
    cabinet_state: str = ""


@dataclass
class InexLocker:
    id: int
    cabinet_id: Optional[int]
    display_no: str
    locker_type: int
    status: Optional[int]
    reserve_status: Optional[int]
    is_active: Optional[int]
    unit_no: Optional[int] = None
    port_no: Optional[int] = None
    opened_at: Optional[str] = None
    status_from_detail: bool = False


@dataclass
class InexPanel:
    id: int
    name: str
    cabinet_id: Optional[int]
    panel_type: Optional[int] = None
    ip: str = ""
    port: Optional[int] = None
    identification_method: Optional[int] = None
    standalone_mode: Optional[int] = None


@dataclass
class InexNotice:
    id: int
    cabinet_id: Optional[int]
    text: str
    created_at: str = ""
    status: Optional[int] = None
    locker_id: Optional[int] = None


@dataclass
class InexLockersSnapshot:
    api_ok: bool
    error: Optional[str] = None
    cabinets: list[InexCabinet] = field(default_factory=list)
    lockers: list[InexLocker] = field(default_factory=list)
    panels: list[InexPanel] = field(default_factory=list)
    notifications: list[InexNotice] = field(default_factory=list)
    issues: list[InexNotice] = field(default_factory=list)


def normalize_api_base_url(url: str) -> str:
    raw = (url or "").strip().rstrip("/")
    if not raw:
        return ""
    if raw.endswith("/api/lockers/v1"):
        return raw
    return f"{raw}/api/lockers/v1"


def _unwrap_data(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    data = payload.get("data")
    if isinstance(data, dict):
        return data
    return {}


def _as_int(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def parse_cabinets_payload(payload: Any) -> list[InexCabinet]:
    data = _unwrap_data(payload)
    rows = data.get("cabinets") or []
    cabinets: list[InexCabinet] = []
    if not isinstance(rows, list):
        return cabinets
    for item in rows:
        if not isinstance(item, dict):
            continue
        cid = _as_int(item.get("id"))
        if cid is None:
            continue
        ident = item.get("identificationMethod")
        if isinstance(ident, list):
            mask = 0
            for bit in ident:
                parsed = _as_int(bit)
                if parsed:
                    mask |= parsed
            ident_val: Optional[int] = mask or None
        else:
            ident_val = _as_int(ident)
        cabinets.append(
            InexCabinet(
                id=cid,
                name=_as_str(item.get("name")),
                controller_type=_as_int(item.get("controllerType")),
                controller_ip=_as_str(item.get("controllerIp") or item.get("ip")),
                controller_port=_as_int(item.get("controllerPort")),
                available_lockers=_as_int(item.get("availableLockers")),
                zone=_as_str(item.get("zone")),
                floor=_as_str(item.get("floor")),
                cabinet_type=_as_int(item.get("type")),
                identification_method=ident_val,
                cabinet_state=_as_str(
                    item.get("cabinetState") or item.get("state")
                ).lower(),
            )
        )
    return cabinets


def parse_lockers_payload(payload: Any) -> list[InexLocker]:
    data = _unwrap_data(payload)
    rows = data.get("lockers") or []
    lockers: list[InexLocker] = []
    if not isinstance(rows, list):
        return lockers
    for item in rows:
        if not isinstance(item, dict):
            continue
        lid = _as_int(item.get("id"))
        if lid is None:
            continue
        lockers.append(
            InexLocker(
                id=lid,
                cabinet_id=_as_int(item.get("cabinetId")),
                display_no=_as_str(item.get("displayNo")) or str(lid),
                locker_type=_as_int(item.get("type")) or 0,
                status=_as_int(item.get("status")),
                reserve_status=_as_int(item.get("reserveStatus")),
                is_active=_as_int(item.get("isActive")),
                unit_no=_as_int(item.get("unitNo")),
                port_no=_as_int(item.get("portNo")),
                opened_at=_as_str(item.get("openedAtDt") or item.get("openedAtDat"))
                or None,
            )
        )
    return lockers


def parse_panels_payload(payload: Any) -> list[InexPanel]:
    data = _unwrap_data(payload)
    rows = data.get("panels") or []
    panels: list[InexPanel] = []
    if not isinstance(rows, list):
        return panels
    for item in rows:
        if not isinstance(item, dict):
            continue
        pid = _as_int(item.get("id"))
        if pid is None:
            continue
        ident = item.get("identificationMethod")
        if isinstance(ident, list):
            mask = 0
            for bit in ident:
                parsed = _as_int(bit)
                if parsed:
                    mask |= parsed
            ident_val: Optional[int] = mask or None
        else:
            ident_val = _as_int(ident)
        panels.append(
            InexPanel(
                id=pid,
                name=_as_str(item.get("name")),
                cabinet_id=_as_int(item.get("cabinetId")),
                panel_type=_as_int(item.get("type")),
                ip=_as_str(item.get("ip")),
                port=_as_int(item.get("port")),
                identification_method=ident_val,
                standalone_mode=_as_int(item.get("standaloneMode")),
            )
        )
    return panels


def parse_notices_payload(payload: Any, key: str) -> list[InexNotice]:
    data = _unwrap_data(payload)
    rows = data.get(key) or []
    notices: list[InexNotice] = []
    if not isinstance(rows, list):
        return notices
    for item in rows:
        if not isinstance(item, dict):
            continue
        nid = _as_int(item.get("id"))
        if nid is None:
            continue
        notices.append(
            InexNotice(
                id=nid,
                cabinet_id=_as_int(item.get("cabinetId")),
                text=_as_str(item.get("text")),
                created_at=_as_str(item.get("createdAt")),
                status=_as_int(item.get("status")),
                locker_id=_as_int(item.get("lockerId")),
            )
        )
    return notices


def parse_locker_status_payload(payload: Any) -> Optional[int]:
    data = _unwrap_data(payload)
    if not data and isinstance(payload, dict):
        data = payload
    nested = data.get("locker") if isinstance(data, dict) else None
    if isinstance(nested, dict):
        data = nested
    if not isinstance(data, dict):
        return None
    status = data.get("status")
    if status is None:
        status = data.get("lockState") or data.get("state")
    return _as_int(status)


def match_panel_cabinet(
    snapshot: InexLockersSnapshot,
    *,
    panel_id: Optional[int],
    host: str,
) -> tuple[Optional[InexPanel], Optional[InexCabinet]]:
    needle = (host or "").strip().lower()
    panel: Optional[InexPanel] = None
    if panel_id is not None:
        panel = next((p for p in snapshot.panels if p.id == panel_id), None)
    if panel is None and needle:
        panel = next(
            (p for p in snapshot.panels if p.ip.strip().lower() == needle),
            None,
        )
    cabinet: Optional[InexCabinet] = None
    if panel and panel.cabinet_id is not None:
        cabinet = next(
            (c for c in snapshot.cabinets if c.id == panel.cabinet_id),
            None,
        )
    if cabinet is None and needle:
        cabinet = next(
            (
                c
                for c in snapshot.cabinets
                if c.controller_ip.strip().lower() == needle
            ),
            None,
        )
    return panel, cabinet


class LockersApiClient:
    def __init__(self, base_url: str, timeout: float = 20.0) -> None:
        self.base_url = normalize_api_base_url(base_url)
        self.timeout = timeout
        self._etag: dict[str, str] = {}
        self._cache: dict[str, Any] = {}

    def _url(self, path: str) -> str:
        return urljoin(self.base_url.rstrip("/") + "/", path.lstrip("/"))

    async def _get_json(
        self,
        path: str,
        *,
        params: Optional[dict[str, str]] = None,
        use_etag: bool = False,
    ) -> Any:
        headers: dict[str, str] = {}
        cache_key = path
        if use_etag and cache_key in self._etag:
            headers["If-None-Match"] = self._etag[cache_key]
        async with httpx.AsyncClient(
            timeout=self.timeout, verify=False, follow_redirects=True
        ) as client:
            response = await client.get(
                self._url(path), params=params, headers=headers
            )
        if response.status_code == 304 and cache_key in self._cache:
            return self._cache[cache_key]
        response.raise_for_status()
        payload = response.json()
        etag = response.headers.get("ETag")
        if use_etag and etag:
            self._etag[cache_key] = etag
            self._cache[cache_key] = payload
        return payload

    async def fetch_snapshot(self) -> InexLockersSnapshot:
        if not self.base_url:
            return InexLockersSnapshot(api_ok=False, error="не задан URL Inex API")
        today = date.today()
        date_from = (today - timedelta(days=30)).isoformat()
        date_to = today.isoformat()
        try:
            cabinets_raw = await self._get_json("cabinets", use_etag=True)
            lockers_raw = await self._get_json("lockers", use_etag=True)
            panels_raw = await self._get_json("panels")
            notes_raw = await self._get_json(
                "security-notifications",
                params={"from": date_from, "to": date_to, "status": "1"},
            )
            issues_raw = await self._get_json(
                "issues",
                params={"from": date_from, "to": date_to, "status": "1"},
            )
        except httpx.TimeoutException:
            return InexLockersSnapshot(api_ok=False, error="таймаут Inex API")
        except httpx.HTTPStatusError as exc:
            return InexLockersSnapshot(
                api_ok=False,
                error=f"Inex API HTTP {exc.response.status_code}",
            )
        except httpx.RequestError as exc:
            return InexLockersSnapshot(api_ok=False, error=f"Inex API: {exc}")
        except ValueError as exc:
            return InexLockersSnapshot(api_ok=False, error=f"Inex API JSON: {exc}")

        snapshot = InexLockersSnapshot(
            api_ok=True,
            cabinets=parse_cabinets_payload(cabinets_raw),
            lockers=parse_lockers_payload(lockers_raw),
            panels=parse_panels_payload(panels_raw),
            notifications=parse_notices_payload(notes_raw, "securityNotifications"),
            issues=parse_notices_payload(issues_raw, "issues"),
        )
        logger.info(
            "inex snapshot",
            extra={
                "event": "inex_snapshot",
                "extra_cabinets": len(snapshot.cabinets),
                "extra_lockers": len(snapshot.lockers),
                "extra_panels": len(snapshot.panels),
            },
        )
        return snapshot

    async def fetch_locker_status(self, locker_id: int) -> Optional[int]:
        payload = await self._get_json(f"lockers/{locker_id}/status")
        return parse_locker_status_payload(payload)

    async def enrich_lock_states(
        self,
        snapshot: InexLockersSnapshot,
        locker_ids: list[int],
    ) -> None:
        if not snapshot.api_ok or not locker_ids:
            return
        unique = list(dict.fromkeys(locker_ids))
        sem = asyncio.Semaphore(5)

        async def _one(lid: int) -> tuple[int, Optional[int]]:
            async with sem:
                try:
                    return lid, await self.fetch_locker_status(lid)
                except (httpx.HTTPError, ValueError):
                    return lid, None

        results = await asyncio.gather(*(_one(lid) for lid in unique))
        by_id = {lid: status for lid, status in results if status is not None}
        for locker in snapshot.lockers:
            if locker.id not in by_id:
                continue
            locker.status = by_id[locker.id]
            locker.status_from_detail = True
