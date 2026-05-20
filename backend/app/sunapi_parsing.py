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
