from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

HOST_RE = re.compile(
    r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[01]?\d?\d)){3}|"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*)$"
)


@dataclass
class RecorderFormData:
    object_name: str
    name: str
    host: str
    port: int
    use_https: bool


def parse_recorder_form(
    object_name: str,
    name: str,
    host: str,
    port: str,
    use_https: str,
) -> tuple[Optional[RecorderFormData], dict[str, str]]:
    errors: dict[str, str] = {}
    obj = object_name.strip()
    h = host.strip()
    n = name.strip()
    if not obj:
        errors["object_name"] = "Укажите название объекта"
    if not h:
        errors["host"] = "Укажите IP или DNS"
    elif not HOST_RE.match(h):
        errors["host"] = "Некорректный формат адреса"
    try:
        port_num = int(port)
        if port_num < 1 or port_num > 65535:
            errors["port"] = "Порт должен быть от 1 до 65535"
    except ValueError:
        errors["port"] = "Укажите корректный порт"
        port_num = 80

    if errors:
        return None, errors

    return (
        RecorderFormData(
            object_name=obj,
            name=n,
            host=h,
            port=port_num,
            use_https=use_https == "true",
        ),
        {},
    )
