from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Optional


def parse_key_value_body(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if "=" in line:
            key, _, value = line.partition("=")
            fields[key.strip()] = value.strip()
    return fields


def parse_channel_indexed(fields: dict[str, str], prefix: str) -> dict[int, dict[str, str]]:
    """Parse keys like Channel.0.Name into {0: {Name: ...}}."""
    pattern = re.compile(rf"^{re.escape(prefix)}\.(\d+)\.(.+)$")
    result: dict[int, dict[str, str]] = {}
    for key, value in fields.items():
        m = pattern.match(key)
        if m:
            ch = int(m.group(1))
            attr = m.group(2)
            result.setdefault(ch, {})[attr] = value
    return result


def parse_storage_indexed(fields: dict[str, str]) -> list[dict[str, str]]:
    pattern = re.compile(r"^Storage\.(\d+)\.(.+)$")
    storages: dict[int, dict[str, str]] = {}
    for key, value in fields.items():
        m = pattern.match(key)
        if m:
            idx = int(m.group(1))
            attr = m.group(2)
            storages.setdefault(idx, {})["Storage"] = str(idx)
            storages[idx][attr] = value
    return [storages[k] for k in sorted(storages)]


def try_parse_json(text: str) -> Optional[Any]:
    text = text.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def parse_datetime_local(value: str) -> Optional[datetime]:
    value = value.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


RECORD_FRAME_DROP_LOG_TYPE = "RecordFrameDrop"

_RECORD_FRAME_DROP_MARKERS = (
    "recordframedrop",
    "recording frame drop",
)

_SYSTEMLOG_BRACKET_LINE_RE = re.compile(
    r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[([^\]]+)\](?:\s+(.*))?$"
)
_SYSTEMLOG_COLON_LINE_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*:\s*(.+)$"
)


def log_entry_matches_type(log_type: str, entry_type: str, description: str) -> bool:
    wanted = log_type.strip().lower()
    if entry_type.strip().lower() == wanted:
        return True
    if wanted == RECORD_FRAME_DROP_LOG_TYPE.lower():
        haystack = f"{entry_type} {description}".lower()
        return any(marker in haystack for marker in _RECORD_FRAME_DROP_MARKERS)
    return False


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


def parse_systemlog_latest_timestamp(body: str, log_type: str) -> Optional[str]:
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
