"""Импорт выгрузки CMDB из Excel в SQLite."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from .state_store import StateStore

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = PROJECT_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from cmdb_reader import CmdbDeviceRow, CmdbParseResult, read_cmdb_xlsx  # noqa: E402

from .state_store import CmdbRecordRow

ProgressCallback = Callable[[str, int], None]

BATCH_SIZE = 500


def _to_record_row(row: CmdbDeviceRow) -> CmdbRecordRow:
    return CmdbRecordRow(
        host=row.host,
        functional_type=row.functional_type,
        manufacturer=row.manufacturer,
        object_name=row.object_name,
        model_name=row.name or "",
        mac=row.mac,
        device_kind=row.device_kind,
        source_row=row.source_row,
    )


def import_cmdb_parsed(
    parsed: CmdbParseResult,
    state: "StateStore",
    on_progress: Optional[ProgressCallback] = None,
    *,
    imported_at: Optional[datetime] = None,
) -> int:
    """Записывает распарсенные строки CMDB в cmdb_records (полная замена)."""
    progress = on_progress or (lambda _phase, _percent: None)
    when = imported_at or datetime.now(timezone.utc)
    total = len(parsed.rows)
    progress("Сохранение CMDB", 50)

    with state.replace_cmdb_records(when) as session:
        batch: list[CmdbRecordRow] = []
        for idx, row in enumerate(parsed.rows, start=1):
            batch.append(_to_record_row(row))
            if len(batch) >= BATCH_SIZE:
                session.write_batch(batch)
                batch = []
            if idx % (BATCH_SIZE * 4) == 0 or idx == total:
                percent = 50 + int(idx / max(total, 1) * 40)
                progress("Сохранение CMDB", min(percent, 90))

        if batch:
            session.write_batch(batch)

    progress("Сохранение CMDB", 95)
    return session.count


def import_cmdb_xlsx(
    path: Path,
    state: "StateStore",
    on_progress: Optional[ProgressCallback] = None,
    *,
    parsed: Optional[CmdbParseResult] = None,
) -> int:
    """Читает xlsx и полностью заменяет cmdb_records в SQLite."""
    progress = on_progress or (lambda _phase, _percent: None)
    progress("Чтение CMDB", 30)

    data = parsed if parsed is not None else read_cmdb_xlsx(path)
    return import_cmdb_parsed(data, state, on_progress=progress)
