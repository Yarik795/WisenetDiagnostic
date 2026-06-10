"""Синхронизация устройств в config.json из cmdb.xlsx."""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from .config_store import ConfigStore
from .models import AppConfig

if TYPE_CHECKING:
    from .state_store import StateStore

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CMDB_PATH = PROJECT_ROOT / "cmdb.xlsx"

_SCRIPTS = PROJECT_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from cmdb_reader import (  # noqa: E402
    FUNCTIONAL_TYPE_VIDEO,
    MANUFACTURER_BIO,
    MANUFACTURER_SKUD,
    MergeError,
    MergeStats,
    merge_devices_from_cmdb,
    read_cmdb_xlsx,
)


@dataclass(frozen=True)
class CmdbSyncResult:
    ok: bool
    message: str
    stats: Optional[MergeStats] = None
    merge_errors: Optional[list[MergeError]] = None
    total_recorders: int = 0
    cmdb_row_count: int = 0
    skipped_empty_ip: int = 0
    skipped_unclassified: int = 0
    total_data_rows: int = 0
    counts_by_kind: dict[str, int] = field(default_factory=dict)

    @property
    def skipped_wrong_type(self) -> int:
        return self.skipped_unclassified


def _kind_breakdown(counts: dict[str, int]) -> str:
    tsv = counts.get("tsv", 0)
    skud = counts.get("skud", 0)
    bio = counts.get("bio", 0)
    return f"ТСВ {tsv}, СКУД {skud}, Био {bio}"


def _success_message(stats: MergeStats, total: int, counts: dict[str, int]) -> str:
    return (
        f"Обновлено из CMDB: {total} устройств ({_kind_breakdown(counts)}); "
        f"новых {stats.added}, сохранено {stats.preserved}, удалено {stats.removed}"
    )


def _no_change_message(total: int, counts: dict[str, int]) -> str:
    return f"Изменений нет: {total} устройств ({_kind_breakdown(counts)})"


def _recorders_snapshot(recorders: list) -> list[dict]:
    return sorted(
        (r.model_dump(mode="json") for r in recorders),
        key=lambda item: item["id"],
    )


def _configs_equivalent(old_config: AppConfig, new_config: AppConfig) -> bool:
    return (
        _recorders_snapshot(old_config.recorders)
        == _recorders_snapshot(new_config.recorders)
        and old_config.exclusions.model_dump(mode="json")
        == new_config.exclusions.model_dump(mode="json")
    )


def sync_from_cmdb(
    store: ConfigStore,
    cmdb_path: Path | None = None,
    *,
    state: Optional["StateStore"] = None,
    backup: bool = True,
    dry_run: bool = False,
) -> CmdbSyncResult:
    path = (cmdb_path or DEFAULT_CMDB_PATH).resolve()

    if not path.is_file():
        return CmdbSyncResult(
            ok=False,
            message=f"Файл CMDB не найден: {path}",
        )

    try:
        parsed = read_cmdb_xlsx(path)
    except Exception as e:
        return CmdbSyncResult(ok=False, message=f"Ошибка чтения CMDB: {e}")

    try:
        old_config = store.load()
    except Exception as e:
        return CmdbSyncResult(ok=False, message=f"Ошибка чтения config: {e}")

    merged, stats, errors = merge_devices_from_cmdb(
        parsed.rows, old_config.recorders
    )

    if errors:
        lines = [f"строка {err.source_row}: {err.message}" for err in errors]
        return CmdbSyncResult(
            ok=False,
            message="Ошибки валидации CMDB: " + "; ".join(lines),
            merge_errors=errors,
            stats=stats,
            cmdb_row_count=len(parsed.rows),
            skipped_empty_ip=parsed.skipped_empty_ip,
            skipped_unclassified=parsed.skipped_unclassified,
            total_data_rows=parsed.total_data_rows,
            counts_by_kind=dict(parsed.counts_by_kind),
        )

    if dry_run:
        return CmdbSyncResult(
            ok=True,
            message=_success_message(stats, len(merged), parsed.counts_by_kind)
            + " (dry-run, без записи)",
            stats=stats,
            total_recorders=len(merged),
            cmdb_row_count=len(parsed.rows),
            skipped_empty_ip=parsed.skipped_empty_ip,
            skipped_unclassified=parsed.skipped_unclassified,
            total_data_rows=parsed.total_data_rows,
            counts_by_kind=dict(parsed.counts_by_kind),
        )

    from .exclusions import prune_exclusions

    new_config = prune_exclusions(
        AppConfig(
            credentials=old_config.credentials,
            monitoring=old_config.monitoring,
            exclusions=old_config.exclusions,
            email_report=old_config.email_report,
            recorders=merged,
        )
    )
    try:
        AppConfig.model_validate(new_config.model_dump(mode="json"))
    except Exception as e:
        return CmdbSyncResult(
            ok=False,
            message=f"Ошибка валидации итогового config: {e}",
        )

    if _configs_equivalent(old_config, new_config):
        message = _no_change_message(len(merged), parsed.counts_by_kind)
        if state is not None:
            state.record_source_import(
                "cmdb",
                filename=path.name,
                record_count=len(merged),
                status="ok",
                message=message,
            )
        return CmdbSyncResult(
            ok=True,
            message=message,
            stats=stats,
            total_recorders=len(merged),
            cmdb_row_count=len(parsed.rows),
            skipped_empty_ip=parsed.skipped_empty_ip,
            skipped_unclassified=parsed.skipped_unclassified,
            total_data_rows=parsed.total_data_rows,
            counts_by_kind=dict(parsed.counts_by_kind),
        )

    old_ids = {r.id for r in old_config.recorders}
    new_ids = {r.id for r in merged}
    removed_ids = old_ids - new_ids

    config_path = store.path.resolve()
    if backup and config_path.exists():
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = config_path.with_suffix(f".json.bak.{ts}")
        shutil.copy2(config_path, backup_path)

    store.save(new_config)

    if state is not None:
        for recorder_id in removed_ids:
            state.delete_recorder_data(recorder_id)
        state.record_source_import(
            "cmdb",
            filename=path.name,
            record_count=len(merged),
            status="ok",
            message=_success_message(stats, len(merged), parsed.counts_by_kind),
        )

    return CmdbSyncResult(
        ok=True,
        message=_success_message(stats, len(merged), parsed.counts_by_kind),
        stats=stats,
        total_recorders=len(merged),
        cmdb_row_count=len(parsed.rows),
        skipped_empty_ip=parsed.skipped_empty_ip,
        skipped_unclassified=parsed.skipped_unclassified,
        total_data_rows=parsed.total_data_rows,
        counts_by_kind=dict(parsed.counts_by_kind),
    )


def cmdb_sync_report_lines(result: CmdbSyncResult) -> list[str]:
    """Строки отчёта для CLI (как раньше в sync_config_from_cmdb)."""
    lines: list[str] = []
    if result.total_data_rows:
        lines.append(
            f"CMDB: строк данных после заголовка — {result.total_data_rows}"
        )
        counts = result.counts_by_kind
        lines.append(
            f"Импортировано: {_kind_breakdown(counts)} "
            f"(всего {result.cmdb_row_count})"
        )
        lines.append(
            f"Фильтры: «{FUNCTIONAL_TYPE_VIDEO}», "
            f"«{MANUFACTURER_SKUD}», «{MANUFACTURER_BIO}»"
        )
        lines.append(
            f"Пропущено: пустой IP — {result.skipped_empty_ip}, "
            f"не классифицировано — {result.skipped_unclassified}"
        )
    if result.stats:
        lines.append(
            f"Итог: сохранено — {result.stats.preserved}, "
            f"новых — {result.stats.added}, "
            f"удалено из старого config — {result.stats.removed}"
        )
    return lines
