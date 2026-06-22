#!/usr/bin/env python3
r"""Проверка алгоритма «Потеря кадров записи» + дата из systemlog.

Опрашивает NVR:
  1. eventstatus.cgi — активен ли SystemEvent.RecordFrameDrop
  2. system.cgi/systemlog — дата последней записи в журнале (если флаг активен)

Запуск (PowerShell, Python 3.13, проект WisenetDiagnostic-main):

  $env:Path += ";C:/Program Files/Python313;C:/Program Files/Python313/Scripts"
  Set-Location "C:/Users/21204476/Documents/Python/WisenetDiagnostic-main/WisenetDiagnostic-main/backend"

  # логи за год + помесячные чанки + сохранение дампа
  python ../scripts/probe_record_frame_drop.py --host 100.111.4.19 --save --dump

  # сверка с датой из веб-UI (апрель 2026)
  python ../scripts/probe_record_frame_drop.py --host 100.111.4.19 `
    --ui-date 2026-04-25 --from-date 2026-04-01 --to-date 2026-04-30 --save

  # точный день из UI
  python ../scripts/probe_record_frame_drop.py --host 100.111.4.19 `
    --from-date 2026-03-16 --to-date 2026-03-16 --save --dump

  # явный календарный период
  python ../scripts/probe_record_frame_drop.py --host 100.111.4.19 `
    --from-date 2025-06-22 --to-date 2026-06-22 --save --dump

  # если пароль не в config.json (файл в корне проекта)
  python ../scripts/probe_record_frame_drop.py --host 100.111.4.19 `
    --username admin --password "ВАШ_ПАРОЛЬ" --log-days 365 --save

  # парсер без сети
  python ../scripts/probe_record_frame_drop.py --self-test

  config.json читается из корня проекта автоматически (не зависит от текущей папки).

  Дампы: docs/nvr-samples/raw/record-frame-drop-probe/<host>_<UTC>/

  Без FromDate/ToDate NVR отдаёт только кольцевой буфер (часто Total=3…100).
  История — через --log-days 365 или --from-date / --to-date (SUNAPI systemlog).
  На XRN диапазон FromDate…ToDate часто обрезан (~86 строк); дату RecordFrameDrop
  ищите посуточным сканом (--scan-days, по умолчанию 120) или --ui-date YYYY-MM-DD.

  Веб-UI может показывать строки, которых нет в широком запросе systemlog — сверка: --ui-date.

Учётные данные — credentials из config.json (как у опроса NVR в приложении).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.models import Recorder  # noqa: E402
from app.sunapi_extended import build_url, parse_eventstatus, try_parse_json  # noqa: E402

DEFAULT_CONFIG = ROOT / "config.json"
DEFAULT_HOST = "100.111.4.19"
DEFAULT_SAVE_DIR = ROOT / "docs" / "nvr-samples" / "raw" / "record-frame-drop-probe"
LOG_TYPE = "RecordFrameDrop"

_SYSTEMLOG_BRACKET_LINE_RE = re.compile(
    r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[([^\]]+)\](?:\s+(.*))?$"
)
_SYSTEMLOG_COLON_LINE_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*:\s*(.+)$"
)
_RECORD_FRAME_DROP_MARKERS = (
    "recordframedrop",
    "recording frame drop",
)
# Типы systemlog для перебора, если Type=RecordFrameDrop даёт NG 612 на старых NVR.
_FALLBACK_SYSTEMLOG_TYPES = (
    "RecordFrameDrop",
    "RecordingError",
    "StreamCorrupt",
)


def load_credentials(config_path: Path) -> tuple[str, str]:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    creds = data.get("credentials") or {}
    user = (creds.get("username") or "").strip()
    password = creds.get("password") or ""
    if not user:
        raise SystemExit(f"Нет credentials.username в {config_path}")
    if not password or password == "CHANGE_ME":
        raise SystemExit(
            f"Задайте реальный пароль API в {config_path} (credentials.password)"
        )
    return user, password


def find_recorder_in_config(config_path: Path, host: str) -> tuple[int, bool]:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    for rec in data.get("recorders") or []:
        if (rec.get("host") or "").strip() == host:
            port = int(rec.get("port") or 80)
            use_https = bool(rec.get("use_https"))
            return port, use_https
    return 80, False


def fetch(
    client: httpx.Client, url: str, timeout: float
) -> tuple[int, str, str | None]:
    try:
        response = client.get(url, timeout=timeout)
        return response.status_code, response.text, None
    except httpx.TimeoutException:
        return 0, "", "timeout"
    except httpx.RequestError as exc:
        return 0, "", str(exc)


def log_entry_matches_type(log_type: str, entry_type: str, description: str) -> bool:
    wanted = log_type.strip().lower()
    if entry_type.strip().lower() == wanted:
        return True
    if wanted == LOG_TYPE.lower():
        haystack = f"{entry_type} {description}".lower()
        return any(marker in haystack for marker in _RECORD_FRAME_DROP_MARKERS)
    return False


def parse_systemlog_latest_timestamp(body: str, log_type: str) -> str | None:
    """Самая свежая запись systemlog указанного типа (первая в ответе NVR)."""
    data = try_parse_json(body)
    if isinstance(data, dict):
        entries = data.get("SystemLog")
        if isinstance(entries, list):
            for item in entries:
                if not isinstance(item, dict):
                    continue
                entry_type = str(item.get("Type") or "")
                description = str(item.get("Description") or "")
                if not log_entry_matches_type(log_type, entry_type, description):
                    continue
                date = str(item.get("Date") or "").strip()
                if date:
                    return date

    for line in (body or "").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("Total="):
            continue
        bracket = _SYSTEMLOG_BRACKET_LINE_RE.match(stripped)
        if bracket:
            timestamp, entry_type, description = bracket.groups()
            description = description or ""
            if log_entry_matches_type(log_type, entry_type, description):
                return timestamp
            continue
        colon = _SYSTEMLOG_COLON_LINE_RE.match(stripped)
        if colon:
            timestamp, description = colon.groups()
            if log_entry_matches_type(log_type, "", description):
                return timestamp
    return None


def format_display_timestamp(raw: str) -> str:
    raw = raw.strip()
    for fmt, size in (("%Y-%m-%d %H:%M:%S", 19), ("%Y-%m-%d %H:%M", 16)):
        try:
            dt = datetime.strptime(raw[:size], fmt)
            return dt.strftime("%d.%m.%Y %H:%M")
        except ValueError:
            continue
    return raw


def resolve_log_date_range(
    *,
    from_date: str | None,
    to_date: str | None,
    log_days: int,
) -> tuple[str, str, str]:
    """Возвращает (from_date, to_date, note) в формате YYYY-MM-DD."""
    today = datetime.now().date()
    if from_date and to_date:
        return from_date, to_date, f"явный период {from_date} … {to_date}"
    if from_date and not to_date:
        return from_date, today.isoformat(), f"с {from_date} по сегодня"
    if to_date and not from_date:
        start = today - timedelta(days=log_days)
        return start.isoformat(), to_date, f"{log_days} сут. до {to_date}"
    start = today - timedelta(days=log_days)
    return (
        start.isoformat(),
        today.isoformat(),
        f"последние {log_days} сут. ({start.isoformat()} … {today.isoformat()})",
    )


def is_sunapi_ng_error(body: str) -> bool:
    text = (body or "").strip()
    return text.startswith("NG") or "Error Code:" in text


def extract_log_timestamps(body: str) -> list[str]:
    timestamps: list[str] = []
    for line in (body or "").splitlines():
        stripped = line.strip()
        bracket = _SYSTEMLOG_BRACKET_LINE_RE.match(stripped)
        if bracket:
            timestamps.append(bracket.group(1))
            continue
        colon = _SYSTEMLOG_COLON_LINE_RE.match(stripped)
        if colon:
            timestamps.append(colon.group(1))
    return timestamps


def find_frame_drop_lines(body: str) -> list[str]:
    lines: list[str] = []
    for line in (body or "").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("Total="):
            continue
        lower = stripped.lower()
        if any(marker in lower for marker in _RECORD_FRAME_DROP_MARKERS):
            lines.append(stripped)
    return lines


def analyze_systemlog_body(body: str) -> dict:
    timestamps = extract_log_timestamps(body)
    frame_lines = find_frame_drop_lines(body)
    return {
        "total_reported": parse_systemlog_total(body),
        "parsed_lines": len(timestamps),
        "oldest": min(timestamps) if timestamps else None,
        "newest": max(timestamps) if timestamps else None,
        "frame_drop_lines": frame_lines,
        "is_ng_error": is_sunapi_ng_error(body),
    }


def iter_date_chunks(
    from_iso: str, to_iso: str, *, chunk_days: int
) -> list[tuple[str, str]]:
    start = datetime.strptime(from_iso, "%Y-%m-%d").date()
    end = datetime.strptime(to_iso, "%Y-%m-%d").date()
    if start > end:
        return []
    chunks: list[tuple[str, str]] = []
    current = start
    while current <= end:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end)
        chunks.append((current.isoformat(), chunk_end.isoformat()))
        current = chunk_end + timedelta(days=1)
    return chunks


def merge_systemlog_bodies(parts: list[tuple[str, str, str]]) -> str:
    """parts: (from_date, to_date, body). Объединяет строки, убирает дубликаты."""
    seen: set[str] = set()
    merged_lines: list[str] = []
    for from_d, to_d, body in parts:
        if is_sunapi_ng_error(body):
            merged_lines.append(f"# chunk {from_d}…{to_d}: NG error")
            continue
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("Total="):
                continue
            if stripped in seen:
                continue
            seen.add(stripped)
            merged_lines.append(stripped)
    merged_lines.sort(reverse=True)
    header = [f"Total={len(merged_lines)}", ""]
    return "\n".join(header + merged_lines) + ("\n" if merged_lines else "")


def fetch_systemlog_range(
    client: httpx.Client,
    recorder: Recorder,
    *,
    from_date: str,
    to_date: str,
    timeout: float,
    log_type: str | None = None,
) -> tuple[int, str, str | None, str]:
    params: dict[str, str] = {"FromDate": from_date, "ToDate": to_date}
    if log_type:
        params["Type"] = log_type
    url = build_url(recorder, "system.cgi", "systemlog", action="view", **params)
    status, body, err = fetch(client, url, timeout)
    return status, body, err, url


def find_lines_matching(body: str, *needles: str) -> list[str]:
    lowered = [needle.strip().lower() for needle in needles if needle and needle.strip()]
    if not lowered:
        return []
    hits: list[str] = []
    for line in (body or "").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        haystack = stripped.lower()
        if any(needle in haystack for needle in lowered):
            hits.append(stripped)
    return hits


def cross_check_ui_date(result: dict, ui_date: str) -> None:
    """Ищет дату/событие из веб-UI во всех собранных ответах SUNAPI."""
    needles = (ui_date, "recording frame drop", "recordframedrop")
    sources = [
        ("systemlog chunked", result.get("systemlog_chunked_body") or ""),
        ("systemlog single", result.get("systemlog_ranged_all_body") or ""),
        ("systemlog ui-day", result.get("ui_day_systemlog_body") or ""),
        ("accesslog period", result.get("accesslog_body") or ""),
        ("accesslog ui-day", result.get("ui_day_accesslog_body") or ""),
        ("accesslog buffer", result.get("accesslog_recent_body") or ""),
        ("eventlog period", result.get("eventlog_ranged_body") or ""),
    ]
    result["ui_date_checks"] = []
    any_hit = False
    for label, body in sources:
        hits = find_lines_matching(body, *needles)
        result["ui_date_checks"].append({"source": label, "hits": hits})
        if hits:
            any_hit = True
            result["notes"].append(f"UI-сверка: в {label} найдено {len(hits)} строк(и)")
    for chunk in result.get("systemlog_chunk_bodies") or []:
        if chunk["from"] <= ui_date <= chunk["to"]:
            hits = find_lines_matching(chunk.get("body") or "", *needles)
            result["notes"].append(
                f"чанк {chunk['from']}…{chunk['to']}: "
                f"{chunk.get('parsed_lines', '?')} строк, совпадений с UI={len(hits)}"
            )
            if hits:
                any_hit = True
    if not any_hit:
        result["notes"].append(
            f"дата {ui_date} и Recording Frame Drop не найдены в SUNAPI "
            "(веб-UI, вероятно, читает другой источник или расширенный журнал)"
        )


def fetch_systemlog_chunked(
    client: httpx.Client,
    recorder: Recorder,
    *,
    from_date: str,
    to_date: str,
    timeout: float,
    chunk_days: int,
    log_type: str | None = None,
) -> tuple[str, list[dict], list[dict]]:
    chunks_meta: list[dict] = []
    chunk_bodies: list[dict] = []
    parts: list[tuple[str, str, str]] = []
    for chunk_from, chunk_to in iter_date_chunks(from_date, to_date, chunk_days=chunk_days):
        status, body, err, url = fetch_systemlog_range(
            client,
            recorder,
            from_date=chunk_from,
            to_date=chunk_to,
            timeout=timeout,
            log_type=log_type,
        )
        analysis = analyze_systemlog_body(body)
        chunks_meta.append(
            {
                "from": chunk_from,
                "to": chunk_to,
                "http": status,
                "error": err,
                "url": url,
                **analysis,
            }
        )
        chunk_bodies.append(
            {
                "from": chunk_from,
                "to": chunk_to,
                "body": body,
                **analysis,
            }
        )
        parts.append((chunk_from, chunk_to, body))
    return merge_systemlog_bodies(parts), chunks_meta, chunk_bodies


def parse_systemlog_total(body: str) -> int | None:
    for line in (body or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("Total="):
            try:
                return int(stripped.split("=", 1)[1])
            except ValueError:
                return None
    data = try_parse_json(body)
    if isinstance(data, dict):
        entries = data.get("SystemLog")
        if isinstance(entries, list):
            return len(entries)
    return None


def _first_timestamp_from_bodies(
    bodies: list[tuple[str, str]],
    log_type: str,
) -> tuple[str | None, str | None]:
    for label, body in bodies:
        timestamp = parse_systemlog_latest_timestamp(body, log_type)
        if timestamp:
            return timestamp, label
    return None, None


def probe_record_frame_drop(
    client: httpx.Client,
    recorder: Recorder,
    *,
    timeout: float,
    save_extra_logs: bool,
    from_date: str,
    to_date: str,
    log_range_note: str,
    chunk_days: int,
    ui_date: str | None = None,
    scan_days: int = 120,
) -> dict:
    result: dict = {
        "host": recorder.host,
        "port": recorder.port,
        "use_https": recorder.use_https,
        "record_frame_drop_active": False,
        "last_log_timestamp": None,
        "last_log_display": None,
        "last_log_source": None,
        "log_from_date": from_date,
        "log_to_date": to_date,
        "log_range_note": log_range_note,
        "chunk_days": chunk_days,
        "systemlog_retention": {},
        "systemlog_chunks": [],
        "systemlog_chunk_bodies": [],
        "ui_date_checks": [],
        "frame_drop_hits": [],
        "eventstatus_http": None,
        "systemlog_recent_http": None,
        "systemlog_ranged_type_http": None,
        "systemlog_ranged_all_http": None,
        "systemlog_chunked_http": None,
        "accesslog_http": None,
        "eventlog_ranged_http": None,
        "notes": [],
        "urls": {},
        "eventstatus_body": "",
        "systemlog_recent_body": "",
        "systemlog_ranged_type_body": "",
        "systemlog_ranged_all_body": "",
        "systemlog_chunked_body": "",
        "accesslog_body": "",
        "accesslog_recent_body": "",
        "ui_day_systemlog_body": "",
        "ui_day_accesslog_body": "",
        "day_scan_log": [],
        "day_scan_body": "",
        "eventlog_ranged_body": "",
        "systemlog_filtered_http": None,
        "systemlog_full_http": None,
        "systemlog_filtered_body": "",
        "systemlog_full_body": "",
        "eventlog_http": None,
        "eventlog_body": "",
    }

    event_url = build_url(recorder, "eventstatus.cgi", "eventstatus", action="check")
    result["urls"]["eventstatus"] = event_url
    status, body, err = fetch(client, event_url, timeout)
    result["eventstatus_http"] = status
    result["eventstatus_body"] = body
    if err:
        result["notes"].append(f"eventstatus: {err}")
        return result
    if status != 200:
        result["notes"].append(f"eventstatus HTTP {status}")
        return result

    events = parse_eventstatus(body).system_events
    active = bool(events.get("RecordFrameDrop"))
    result["record_frame_drop_active"] = active

    if not active:
        result["notes"].append("RecordFrameDrop=False, systemlog не запрашивается")
        return result

    result["notes"].append(f"период systemlog: {log_range_note}")

    status, ranged_type_body, err, ranged_type_url = fetch_systemlog_range(
        client,
        recorder,
        from_date=from_date,
        to_date=to_date,
        timeout=timeout,
        log_type=LOG_TYPE,
    )
    result["urls"]["systemlog_ranged_type"] = ranged_type_url
    result["systemlog_ranged_type_http"] = status
    result["systemlog_ranged_type_body"] = ranged_type_body
    result["systemlog_filtered_http"] = status
    result["systemlog_filtered_body"] = ranged_type_body
    if is_sunapi_ng_error(ranged_type_body):
        result["notes"].append(
            f"Type={LOG_TYPE} на этой модели не поддержан (NG 612 Configuration Not Found)"
        )
    elif status == 200 and not err:
        total = parse_systemlog_total(ranged_type_body)
        if total is not None:
            result["notes"].append(f"systemlog Type={LOG_TYPE} одним запросом: Total={total}")
    elif err:
        result["notes"].append(f"systemlog Type+даты: {err}")
    else:
        result["notes"].append(f"systemlog Type+даты: HTTP {status}")

    status, ranged_all_body, err, ranged_all_url = fetch_systemlog_range(
        client,
        recorder,
        from_date=from_date,
        to_date=to_date,
        timeout=timeout,
    )
    result["urls"]["systemlog_ranged_all"] = ranged_all_url
    result["systemlog_ranged_all_http"] = status
    result["systemlog_ranged_all_body"] = ranged_all_body
    ranged_analysis = analyze_systemlog_body(ranged_all_body)
    result["systemlog_retention"]["single_request"] = ranged_analysis
    if status == 200 and not err and not ranged_analysis["is_ng_error"]:
        result["notes"].append(
            "systemlog одним запросом: "
            f"Total={ranged_analysis['total_reported']}, "
            f"строк={ranged_analysis['parsed_lines']}, "
            f"диапазон {ranged_analysis['oldest']} … {ranged_analysis['newest']}"
        )
    elif err:
        result["notes"].append(f"systemlog за период: {err}")
    else:
        result["notes"].append(f"systemlog за период: HTTP {status}")

    chunked_body = ranged_all_body
    if chunk_days > 0:
        chunked_body, chunks_meta, chunk_bodies = fetch_systemlog_chunked(
            client,
            recorder,
            from_date=from_date,
            to_date=to_date,
            timeout=timeout,
            chunk_days=chunk_days,
        )
        result["systemlog_chunks"] = chunks_meta
        result["systemlog_chunk_bodies"] = chunk_bodies
        result["systemlog_chunked_body"] = chunked_body
        result["systemlog_chunked_http"] = 200
        result["urls"]["systemlog_chunked"] = (
            f"chunked:{chunk_days}d:{from_date}…{to_date}"
        )
        chunked_analysis = analyze_systemlog_body(chunked_body)
        result["systemlog_retention"]["chunked"] = chunked_analysis
        result["notes"].append(
            f"systemlog помесячно ({chunk_days} сут./запрос, "
            f"{len(chunks_meta)} чанков): "
            f"строк={chunked_analysis['parsed_lines']}, "
            f"диапазон {chunked_analysis['oldest']} … {chunked_analysis['newest']}"
        )

    recent_url = build_url(recorder, "system.cgi", "systemlog", action="view")
    result["urls"]["systemlog_recent"] = recent_url
    status, recent_body, err = fetch(client, recent_url, timeout)
    result["systemlog_recent_http"] = status
    result["systemlog_recent_body"] = recent_body
    result["systemlog_full_http"] = status
    result["systemlog_full_body"] = recent_body
    if status == 200 and not err:
        total = parse_systemlog_total(recent_body)
        if total is not None:
            result["notes"].append(f"systemlog без дат (кольцевой буфер): Total={total}")

    search_bodies: list[tuple[str, str]] = [
        ("systemlog chunked", chunked_body),
        ("systemlog single", ranged_all_body),
        ("systemlog Type filter", ranged_type_body),
        ("systemlog buffer", recent_body),
    ]
    timestamp, source = _first_timestamp_from_bodies(search_bodies, LOG_TYPE)
    all_hits: list[str] = []
    for label, body in search_bodies:
        all_hits.extend(find_frame_drop_lines(body))
    result["frame_drop_hits"] = list(dict.fromkeys(all_hits))

    if timestamp:
        result["last_log_timestamp"] = timestamp
        result["last_log_display"] = format_display_timestamp(timestamp)
        result["last_log_source"] = source
        result["notes"].append(f"дата найдена в {source}")

    if save_extra_logs:
        accesslog_url = build_url(
            recorder,
            "system.cgi",
            "accesslog",
            action="view",
            FromDate=from_date,
            ToDate=to_date,
        )
        result["urls"]["accesslog"] = accesslog_url
        status, accesslog_body, err = fetch(client, accesslog_url, timeout)
        result["accesslog_http"] = status
        result["accesslog_body"] = accesslog_body
        if err:
            result["notes"].append(f"accesslog: {err}")
        elif status != 200:
            result["notes"].append(f"accesslog: HTTP {status}")
        else:
            analysis = analyze_systemlog_body(accesslog_body)
            result["notes"].append(
                f"accesslog за период: строк={analysis['parsed_lines']}, "
                f"диапазон {analysis['oldest']} … {analysis['newest']}"
            )

        eventlog_url = build_url(
            recorder,
            "system.cgi",
            "eventlog",
            action="view",
            FromDate=from_date,
            ToDate=to_date,
        )
        result["urls"]["eventlog_ranged"] = eventlog_url
        status, eventlog_body, err = fetch(client, eventlog_url, timeout)
        result["eventlog_ranged_http"] = status
        result["eventlog_ranged_body"] = eventlog_body
        result["eventlog_http"] = status
        result["eventlog_body"] = eventlog_body
        if err:
            result["notes"].append(f"eventlog за период: {err}")
        elif status != 200:
            result["notes"].append(f"eventlog за период: HTTP {status}")
        else:
            total = parse_systemlog_total(eventlog_body)
            if total is not None:
                result["notes"].append(f"eventlog за период: Total={total}")

        accesslog_recent_url = build_url(recorder, "system.cgi", "accesslog", action="view")
        result["urls"]["accesslog_recent"] = accesslog_recent_url
        status, accesslog_recent_body, err = fetch(client, accesslog_recent_url, timeout)
        if status == 200 and not err:
            result["accesslog_recent_body"] = accesslog_recent_body
            analysis = analyze_systemlog_body(accesslog_recent_body)
            result["notes"].append(
                f"accesslog без дат (буфер): строк={analysis['parsed_lines']}, "
                f"диапазон {analysis['oldest']} … {analysis['newest']}"
            )

    if ui_date:
        result["notes"].append(f"сверка с датой из веб-UI: {ui_date}")
        status, body, err, url = fetch_systemlog_range(
            client,
            recorder,
            from_date=ui_date,
            to_date=ui_date,
            timeout=timeout,
        )
        result["urls"]["ui_day_systemlog"] = url
        result["ui_day_systemlog_body"] = body
        if status == 200 and not err:
            analysis = analyze_systemlog_body(body)
            result["notes"].append(
                f"systemlog за {ui_date}: строк={analysis['parsed_lines']}, "
                f"frame_drop={len(analysis['frame_drop_lines'])}"
            )
        access_url = build_url(
            recorder,
            "system.cgi",
            "accesslog",
            action="view",
            FromDate=ui_date,
            ToDate=ui_date,
        )
        result["urls"]["ui_day_accesslog"] = access_url
        status, body, err = fetch(client, access_url, timeout)
        result["ui_day_accesslog_body"] = body
        if status == 200 and not err:
            analysis = analyze_systemlog_body(body)
            result["notes"].append(
                f"accesslog за {ui_date}: строк={analysis['parsed_lines']}"
            )
        cross_check_ui_date(result, ui_date)

    if ui_date and result.get("ui_day_systemlog_body"):
        if apply_frame_drop_timestamp(
            result,
            result["ui_day_systemlog_body"],
            f"systemlog за {ui_date}",
        ):
            result["notes"].append(
                f"дата RecordFrameDrop из сверки с веб-UI ({ui_date})"
            )

    if not result["last_log_timestamp"] and scan_days > 0:
        ts, scan_body, scan_log = scan_last_frame_drop_by_day(
            client,
            recorder,
            end_date=to_date,
            scan_days=scan_days,
            timeout=timeout,
        )
        result["day_scan_log"] = scan_log
        result["day_scan_body"] = scan_body or ""
        if ts:
            result["last_log_timestamp"] = ts
            result["last_log_display"] = format_display_timestamp(ts)
            result["last_log_source"] = "посуточный скан systemlog"
            hit_day = next(
                (e["date"] for e in scan_log if e.get("frame_drop_lines")),
                None,
            )
            result["notes"].append(
                f"дата найдена посуточным сканом ({scan_days} сут. назад от {to_date}"
                + (f", день {hit_day}" if hit_day else "")
                + ")"
            )
            if scan_body:
                hits = find_frame_drop_lines(scan_body)
                result["frame_drop_hits"] = list(
                    dict.fromkeys(result["frame_drop_hits"] + hits)
                )
        else:
            result["notes"].append(
                f"посуточный скан ({scan_days} сут. от {to_date}): "
                "RecordFrameDrop не найден"
            )

    if not result["last_log_timestamp"]:
        retention = result["systemlog_retention"].get("chunked") or ranged_analysis
        oldest = retention.get("oldest")
        newest = retention.get("newest")
        if oldest and newest:
            result["notes"].append(
                "RecordFrameDrop в доступном systemlog не найден; "
                f"на NVR сохранились только записи {oldest} … {newest} "
                "(широкий запрос обрезан — используйте посуточный скан)"
            )
        else:
            result["notes"].append("RecordFrameDrop в systemlog за период не найден")
        result["notes"].append(
            "флаг eventstatus может оставаться True после старого события — сброс: Alarm Reset"
        )

    return result


def scan_last_frame_drop_by_day(
    client: httpx.Client,
    recorder: Recorder,
    *,
    end_date: str,
    scan_days: int,
    timeout: float,
    hint_date: str | None = None,
) -> tuple[str | None, str | None, list[dict]]:
    """Ищет последнее RecordFrameDrop, обходя дни назад (FromDate=ToDate=день)."""
    if scan_days <= 0:
        return None, None, []

    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    scan_log: list[dict] = []
    days_to_try: list[str] = []
    if hint_date:
        days_to_try.append(hint_date)
    for offset in range(scan_days + 1):
        day_iso = (end - timedelta(days=offset)).isoformat()
        if day_iso not in days_to_try:
            days_to_try.append(day_iso)

    for day_iso in days_to_try:
        status, body, err, url = fetch_systemlog_range(
            client,
            recorder,
            from_date=day_iso,
            to_date=day_iso,
            timeout=timeout,
        )
        analysis = analyze_systemlog_body(body)
        scan_log.append(
            {
                "date": day_iso,
                "http": status,
                "error": err,
                "url": url,
                **analysis,
            }
        )
        if analysis["frame_drop_lines"]:
            timestamp = parse_systemlog_latest_timestamp(body, LOG_TYPE)
            return timestamp, body, scan_log
    return None, None, scan_log


def apply_frame_drop_timestamp(
    result: dict,
    body: str | None,
    source: str,
) -> bool:
    if not body:
        return False
    timestamp = parse_systemlog_latest_timestamp(body, LOG_TYPE)
    if not timestamp:
        return False
    result["last_log_timestamp"] = timestamp
    result["last_log_display"] = format_display_timestamp(timestamp)
    result["last_log_source"] = source
    return True


def save_probe_dump(recorder: Recorder, result: dict, out_dir: Path) -> Path:
    """Сохраняет сырые ответы SUNAPI для ручного разбора формата лога."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    folder = out_dir / f"{recorder.host}_{ts}"
    folder.mkdir(parents=True, exist_ok=True)

    summary = {
        k: v
        for k, v in result.items()
        if not k.endswith("_body")
        and k not in ("urls", "systemlog_chunk_bodies")
    }
    summary["saved_at_utc"] = ts
    summary["urls"] = result.get("urls") or {}
    (folder / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    files = [
        ("eventstatus.txt", "eventstatus_body", "urls", "eventstatus", "eventstatus_http"),
        (
            "systemlog_Type_RecordFrameDrop_FromDate_ToDate.txt",
            "systemlog_ranged_type_body",
            "urls",
            "systemlog_ranged_type",
            "systemlog_ranged_type_http",
        ),
        (
            "systemlog_FromDate_ToDate_single.txt",
            "systemlog_ranged_all_body",
            "urls",
            "systemlog_ranged_all",
            "systemlog_ranged_all_http",
        ),
        (
            "systemlog_FromDate_ToDate_chunked.txt",
            "systemlog_chunked_body",
            "urls",
            "systemlog_chunked",
            "systemlog_chunked_http",
        ),
        (
            "systemlog_recent_buffer.txt",
            "systemlog_recent_body",
            "urls",
            "systemlog_recent",
            "systemlog_recent_http",
        ),
        (
            "accesslog_FromDate_ToDate.txt",
            "accesslog_body",
            "urls",
            "accesslog",
            "accesslog_http",
        ),
        (
            "eventlog_FromDate_ToDate.txt",
            "eventlog_ranged_body",
            "urls",
            "eventlog_ranged",
            "eventlog_ranged_http",
        ),
    ]
    for filename, body_key, urls_key, url_name, http_key in files:
        body = result.get(body_key) or ""
        url = (result.get(urls_key) or {}).get(url_name, "")
        http_status = result.get(http_key, "")
        header = [
            f"# host={recorder.host}",
            f"# url={url}",
            f"# http={http_status}",
            "",
        ]
        (folder / filename).write_text("\n".join(header) + body, encoding="utf-8")

    if result.get("frame_drop_hits"):
        (folder / "frame_drop_hits.txt").write_text(
            "\n".join(result["frame_drop_hits"]) + "\n",
            encoding="utf-8",
        )
    if result.get("systemlog_chunks"):
        (folder / "systemlog_chunks.json").write_text(
            json.dumps(result["systemlog_chunks"], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    chunk_dir = folder / "chunks"
    for chunk in result.get("systemlog_chunk_bodies") or []:
        chunk_dir.mkdir(parents=True, exist_ok=True)
        chunk_path = chunk_dir / f"systemlog_{chunk['from']}_{chunk['to']}.txt"
        header = [
            f"# from={chunk['from']}",
            f"# to={chunk['to']}",
            f"# parsed_lines={chunk.get('parsed_lines')}",
            f"# oldest={chunk.get('oldest')}",
            f"# newest={chunk.get('newest')}",
            "",
        ]
        chunk_path.write_text("\n".join(header) + (chunk.get("body") or ""), encoding="utf-8")
    if result.get("ui_date_checks"):
        (folder / "ui_date_checks.json").write_text(
            json.dumps(result["ui_date_checks"], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    if result.get("day_scan_log"):
        (folder / "day_scan_log.json").write_text(
            json.dumps(result["day_scan_log"], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    if result.get("day_scan_body"):
        (folder / "systemlog_day_scan_hit.txt").write_text(
            result["day_scan_body"],
            encoding="utf-8",
        )
    if result.get("ui_day_systemlog_body"):
        (folder / "systemlog_ui_day.txt").write_text(
            result["ui_day_systemlog_body"],
            encoding="utf-8",
        )

    readme = folder / "README.txt"
    readme.write_text(
        "\n".join(
            [
                "Дамп probe_record_frame_drop.py для анализа RecordFrameDrop.",
                f"NVR: {recorder.host}:{recorder.port}",
                f"UTC: {ts}",
                "",
                "Файлы:",
                "  summary.json — метаданные опроса",
                "  eventstatus.txt — флаги SystemEvent",
                "  systemlog_Type_RecordFrameDrop_FromDate_ToDate.txt — журнал за период с фильтром Type",
                "  systemlog_FromDate_ToDate_single.txt — один запрос за весь период",
                "  systemlog_FromDate_ToDate_chunked.txt — объединение помесячных запросов",
                "  systemlog_chunks.json — статистика по каждому чанку",
                "  systemlog_recent_buffer.txt — кольцевой буфер без FromDate/ToDate",
                "  accesslog_FromDate_ToDate.txt — журнал входов (для сравнения с UI)",
                "  eventlog_FromDate_ToDate.txt — eventlog за период",
                "  frame_drop_hits.txt — строки с Recording Frame Drop (если найдены)",
                "  day_scan_log.json — посуточный скан (если выполнялся)",
                "  systemlog_ui_day.txt — systemlog за --ui-date",
                "",
                "Важно: NVR хранит ограниченный объём systemlog (ротация).",
                "Широкий FromDate…ToDate на XRN часто обрезан (~86 строк) — дату ищите посуточно.",
                "Type=RecordFrameDrop на XRN-2010A часто даёт NG 612 — используйте поиск по тексту.",
            ]
        ),
        encoding="utf-8",
    )
    return folder


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"IP NVR (по умолчанию {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=None, help="Порт (иначе из config.json или 80)")
    parser.add_argument(
        "--https",
        action="store_true",
        default=None,
        help="Использовать HTTPS (иначе из config.json или HTTP)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("CONFIG_PATH", DEFAULT_CONFIG)),
        help="Путь к config.json",
    )
    parser.add_argument("--username", default=os.environ.get("NVR_USERNAME"), help="Логин API")
    parser.add_argument("--password", default=os.environ.get("NVR_PASSWORD"), help="Пароль API")
    parser.add_argument("--timeout", type=float, default=25.0, help="Таймаут HTTP, сек")
    parser.add_argument(
        "--dump",
        action="store_true",
        help="Вывести сырые фрагменты ответов в консоль",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Сохранить сырые ответы в каталог (см. --save-dir)",
    )
    parser.add_argument(
        "--no-auto-save",
        action="store_true",
        help="Не сохранять автоматически, если дата в логе не найдена",
    )
    parser.add_argument(
        "--save-dir",
        type=Path,
        default=DEFAULT_SAVE_DIR,
        help=f"Каталог для дампов (по умолчанию {DEFAULT_SAVE_DIR.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--from-date",
        metavar="YYYY-MM-DD",
        default=None,
        help="Начало периода systemlog/eventlog (SUNAPI FromDate)",
    )
    parser.add_argument(
        "--to-date",
        metavar="YYYY-MM-DD",
        default=None,
        help="Конец периода systemlog/eventlog (SUNAPI ToDate)",
    )
    parser.add_argument(
        "--log-days",
        type=int,
        default=365,
        help="Если --from-date не задан: искать за последние N суток (по умолчанию 365)",
    )
    parser.add_argument(
        "--chunk-days",
        type=int,
        default=31,
        help="Дробить период на запросы по N суток (0 = только один запрос за период)",
    )
    parser.add_argument(
        "--ui-date",
        metavar="YYYY-MM-DD",
        default=None,
        help="Дата события из веб-UI для сверки (напр. 2026-04-25)",
    )
    parser.add_argument(
        "--scan-days",
        type=int,
        default=120,
        help=(
            "Если дата не найдена в широком запросе: сканировать systemlog "
            "по одному дню назад от --to-date (0 = отключить)"
        ),
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Проверить парсер systemlog на встроенных примерах (без сети)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Сохранить результат в JSON-файл",
    )
    return parser.parse_args()


def run_self_test() -> None:
    samples = [
        (
            "SUNAPI text",
            """
Total=3
[2026-03-16 05:08:04] [RecordFrameDrop] Recording buffer overflow
[2026-03-10 12:00:00] [Network] link up
""",
            "2026-03-16 05:08:04",
        ),
        (
            "UI colon format",
            """
2026-03-16 05:08:04 : Recording Frame Drop
2026-03-15 23:45:33 : Login(Admin) (admin)
""",
            "2026-03-16 05:08:04",
        ),
        (
            "JSON",
            json.dumps(
                {
                    "SystemLog": [
                        {
                            "Date": "2026-03-16 05:08:04",
                            "Type": "RecordFrameDrop",
                            "Description": "Recording Frame Drop",
                        },
                        {
                            "Date": "2026-03-15 23:45:33",
                            "Type": "AdminLogin",
                            "Description": "Login",
                        },
                    ]
                }
            ),
            "2026-03-16 05:08:04",
        ),
    ]
    failed = 0
    for name, body, expected in samples:
        got = parse_systemlog_latest_timestamp(body, LOG_TYPE)
        ok = got == expected
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {name}: {got!r} (ожидалось {expected!r})")
        if not ok:
            failed += 1
    if failed:
        raise SystemExit(f"self-test: {failed} ошибок")
    print("self-test: все примеры прошли")


def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return

    if args.username and args.password:
        username, password = args.username, args.password
    else:
        username, password = load_credentials(args.config)

    port = args.port
    use_https = args.https
    if port is None or use_https is None:
        cfg_port, cfg_https = find_recorder_in_config(args.config, args.host)
        if port is None:
            port = cfg_port
        if use_https is None:
            use_https = cfg_https

    recorder = Recorder(
        id="probe-record-frame-drop",
        object_name="probe",
        name=f"probe-{args.host}",
        host=args.host,
        port=port,
        use_https=bool(use_https),
    )

    from_date, to_date, log_range_note = resolve_log_date_range(
        from_date=args.from_date,
        to_date=args.to_date,
        log_days=args.log_days,
    )

    print(f"Опрос {recorder.host}:{recorder.port} ({'HTTPS' if recorder.use_https else 'HTTP'})")
    print(f"Период systemlog: {from_date} … {to_date} ({log_range_note})")
    if args.chunk_days > 0:
        print(f"Чанки: по {args.chunk_days} сут.")
    if args.scan_days > 0:
        print(f"Посуточный скан при отсутствии даты: до {args.scan_days} сут. от {to_date}")
    should_save = args.save or not args.no_auto_save
    with httpx.Client(auth=httpx.DigestAuth(username, password)) as client:
        result = probe_record_frame_drop(
            client,
            recorder,
            timeout=args.timeout,
            save_extra_logs=should_save,
            from_date=from_date,
            to_date=to_date,
            log_range_note=log_range_note,
            chunk_days=args.chunk_days,
            ui_date=args.ui_date,
            scan_days=args.scan_days,
        )

    saved_dir: Path | None = None
    if should_save and (
        args.save
        or (
            result["record_frame_drop_active"]
            and not result["last_log_timestamp"]
        )
    ):
        saved_dir = save_probe_dump(recorder, result, args.save_dir)

    print()
    print(f"RecordFrameDrop активен: {result['record_frame_drop_active']}")
    if result["record_frame_drop_active"]:
        if result["last_log_timestamp"]:
            print(f"Последняя запись в systemlog: {result['last_log_timestamp']}")
            if result.get("last_log_source"):
                print(f"Источник: {result['last_log_source']}")
            print(f"Для UI (план): Потеря кадров записи ({result['last_log_display']})")
        else:
            print("Дата в systemlog: не найдена")
    print()
    print("HTTP:")
    print(f"  eventstatus: {result['eventstatus_http']}")
    if result.get("systemlog_ranged_type_http") is not None:
        print(f"  systemlog Type={LOG_TYPE}+даты: {result['systemlog_ranged_type_http']}")
    if result.get("systemlog_ranged_all_http") is not None:
        print(f"  systemlog за период (один запрос): {result['systemlog_ranged_all_http']}")
    if result.get("systemlog_chunked_http") is not None:
        print(f"  systemlog за период (чанки): {result['systemlog_chunked_http']}")
    if result.get("systemlog_recent_http") is not None:
        print(f"  systemlog буфер (без дат): {result['systemlog_recent_http']}")
    if result.get("accesslog_http") is not None:
        print(f"  accesslog за период: {result['accesslog_http']}")
    if result.get("eventlog_ranged_http") is not None:
        print(f"  eventlog за период: {result['eventlog_ranged_http']}")
    retention = (result.get("systemlog_retention") or {}).get("chunked") or (
        result.get("systemlog_retention") or {}
    ).get("single_request")
    if retention and retention.get("oldest"):
        print()
        print(
            f"Фактически в systemlog на NVR: {retention.get('oldest')} … "
            f"{retention.get('newest')} ({retention.get('parsed_lines')} строк)"
        )
    if saved_dir:
        print()
        print(f"Сырые ответы сохранены: {saved_dir}")
    if result["notes"]:
        print()
        print("Примечания:")
        for note in result["notes"]:
            print(f"  - {note}")

    if args.dump:
        print()
        print("--- RAW eventstatus (фрагмент) ---")
        body = result.get("eventstatus_body", "")
        for line in body.splitlines():
            if "RecordFrameDrop" in line or line.startswith("SystemEvent"):
                print(line)
        for title, key in (
            (f"systemlog Type+даты", "systemlog_ranged_type_body"),
            ("systemlog chunked (первые 20)", "systemlog_chunked_body"),
            ("systemlog single (первые 20)", "systemlog_ranged_all_body"),
            ("systemlog буфер", "systemlog_recent_body"),
        ):
            if result.get(key):
                print()
                print(f"--- RAW {title} ---")
                for line in result[key].splitlines()[:20]:
                    print(line)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        payload = {k: v for k, v in result.items() if not k.endswith("_body")}
        if saved_dir:
            payload["saved_dump_dir"] = str(saved_dir)
        args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print()
        print(f"Сводка сохранена: {args.out}")


if __name__ == "__main__":
    main()
