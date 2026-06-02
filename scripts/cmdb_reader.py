"""Чтение регистраторов из CMDB (Excel) для синхронизации config.json."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

FUNCTIONAL_TYPE_VIDEO = "Видеорегистраторы"
COL_IP = "IP"
COL_ADDRESS = "Адрес"
COL_MODEL = "Модель устройства"
COL_FUNCTIONAL_TYPE = "Функциональный тип"

_REQUIRED_HEADERS = {COL_IP, COL_FUNCTIONAL_TYPE}

# Latin letters that look like Cyrillic (common CMDB export corruption).
_HOMOGLYPH_MAP = str.maketrans(
    {
        "A": "А",
        "a": "а",
        "B": "В",
        "C": "С",
        "c": "с",
        "E": "Е",
        "e": "е",
        "H": "Н",
        "K": "К",
        "M": "М",
        "O": "О",
        "o": "о",
        "P": "Р",
        "p": "р",
        "T": "Т",
        "X": "Х",
        "x": "х",
        "Y": "У",
        "y": "у",
    }
)


def normalize_homoglyphs(text: str) -> str:
    if not any("\u0400" <= ch <= "\u04FF" for ch in text):
        return text
    return text.translate(_HOMOGLYPH_MAP)


def normalize_cmdb_label(value: Any) -> str:
    """Normalize CMDB headers and categorical fields (not IP/MAC/host)."""
    if value is None:
        return ""
    text = re.sub(r"\s+", " ", str(value).strip())
    return normalize_homoglyphs(text)


def normalize_header(value: Any) -> str:
    return normalize_cmdb_label(value)


def _cell_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def find_header_row(rows: list[list[Any]]) -> int:
    for idx, row in enumerate(rows):
        headers = {normalize_header(c) for c in row if c is not None and str(c).strip()}
        if _REQUIRED_HEADERS.issubset(headers):
            return idx
    raise ValueError(
        f"Строка заголовков не найдена (нужны колонки «{COL_IP}» и «{COL_FUNCTIONAL_TYPE}»)"
    )


def build_col_index(header_row: list[Any]) -> dict[str, int]:
    index: dict[str, int] = {}
    for col, cell in enumerate(header_row):
        name = normalize_header(cell)
        if name and name not in index:
            index[name] = col
    missing = _REQUIRED_HEADERS - set(index)
    if missing:
        raise ValueError(f"В заголовке отсутствуют колонки: {', '.join(sorted(missing))}")
    for col in (COL_ADDRESS, COL_MODEL):
        if col not in index:
            raise ValueError(f"В заголовке отсутствует колонка «{col}»")
    return index


@dataclass(frozen=True)
class CmdbRecorderRow:
    host: str
    object_name: str
    name: Optional[str]
    source_row: int


@dataclass
class CmdbParseResult:
    rows: list[CmdbRecorderRow]
    total_data_rows: int
    skipped_empty_ip: int
    skipped_wrong_type: int


def parse_cmdb_grid(rows: list[list[Any]]) -> CmdbParseResult:
    header_idx = find_header_row(rows)
    col_index = build_col_index(rows[header_idx])
    ip_col = col_index[COL_IP]
    addr_col = col_index[COL_ADDRESS]
    model_col = col_index[COL_MODEL]
    type_col = col_index[COL_FUNCTIONAL_TYPE]

    result_rows: list[CmdbRecorderRow] = []
    skipped_empty_ip = 0
    skipped_wrong_type = 0
    total_data_rows = 0

    for row_idx, row in enumerate(rows[header_idx + 1 :], start=header_idx + 2):
        if not row or all(c is None or str(c).strip() == "" for c in row):
            continue
        total_data_rows += 1

        func_type = normalize_cmdb_label(
            row[type_col] if type_col < len(row) else None
        )
        if func_type != FUNCTIONAL_TYPE_VIDEO:
            skipped_wrong_type += 1
            continue

        host = _cell_str(row[ip_col] if ip_col < len(row) else None)
        if not host:
            skipped_empty_ip += 1
            continue

        object_name = _cell_str(row[addr_col] if addr_col < len(row) else None)
        model = _cell_str(row[model_col] if model_col < len(row) else None)
        result_rows.append(
            CmdbRecorderRow(
                host=host,
                object_name=object_name,
                name=model or None,
                source_row=row_idx,
            )
        )

    return CmdbParseResult(
        rows=result_rows,
        total_data_rows=total_data_rows,
        skipped_empty_ip=skipped_empty_ip,
        skipped_wrong_type=skipped_wrong_type,
    )


def read_cmdb_xlsx(path: Path) -> CmdbParseResult:
    from openpyxl import load_workbook

    wb = load_workbook(path, read_only=True, data_only=True)
    try:
        ws = wb.active
        grid: list[list[Any]] = []
        for row in ws.iter_rows(values_only=True):
            grid.append(list(row))
    finally:
        wb.close()
    return parse_cmdb_grid(grid)


# --- merge with existing config ---


def new_recorder_id() -> str:
    import uuid

    return f"nvr-{uuid.uuid4().hex[:8]}"


@dataclass
class MergeStats:
    preserved: int
    added: int
    removed: int


@dataclass
class MergeError:
    source_row: int
    message: str


def merge_recorders_from_cmdb(
    cmdb_rows: list[CmdbRecorderRow],
    existing: list[Any],
) -> tuple[list[Any], MergeStats, list[MergeError]]:
    from pydantic import ValidationError

    from app.models import Recorder

    remaining: dict[str, Any] = {r.host: r for r in existing}
    old_hosts = {r.host for r in existing}

    merged: list[Any] = []
    errors: list[MergeError] = []
    preserved = 0
    added = 0

    for row in cmdb_rows:
        try:
            base = {
                "object_name": row.object_name,
                "name": row.name,
                "host": row.host,
                "port": 80,
                "use_https": False,
            }
            old = remaining.pop(row.host, None)
            if old:
                recorder = Recorder(
                    id=old.id,
                    last_status=old.last_status,
                    last_check_at=old.last_check_at,
                    last_error=old.last_error,
                    **base,
                )
                preserved += 1
            else:
                recorder = Recorder(id=new_recorder_id(), **base)
                added += 1
            merged.append(recorder)
        except ValidationError as e:
            errors.append(MergeError(source_row=row.source_row, message=str(e)))

    new_hosts = {r.host for r in merged}
    removed = len(old_hosts - new_hosts)
    stats = MergeStats(preserved=preserved, added=added, removed=removed)
    return merged, stats, errors
