#!/usr/bin/env python3
"""Замена списка recorders в config.json данными из cmdb.xlsx."""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(SCRIPTS))

from app.config_store import ConfigStore  # noqa: E402
from app.models import AppConfig  # noqa: E402
from cmdb_reader import (  # noqa: E402
    FUNCTIONAL_TYPE_VIDEO,
    merge_recorders_from_cmdb,
    read_cmdb_xlsx,
)


def _default_config() -> Path:
    return ROOT / "config.json"


def _default_cmdb() -> Path:
    return Path.cwd() / "cmdb.xlsx"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Обновить recorders в config.json из CMDB (Excel)"
    )
    parser.add_argument(
        "--cmdb",
        type=Path,
        default=_default_cmdb(),
        help="Путь к cmdb.xlsx (по умолчанию: cmdb.xlsx в текущей директории)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=_default_config(),
        help="Путь к config.json (по умолчанию: config.json в корне проекта)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только отчёт, без записи config",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Не создавать резервную копию config перед записью",
    )
    args = parser.parse_args()

    cmdb_path: Path = args.cmdb.resolve()
    config_path: Path = args.config.resolve()

    if not cmdb_path.is_file():
        print(f"Ошибка: файл CMDB не найден: {cmdb_path}", file=sys.stderr)
        return 1

    try:
        parsed = read_cmdb_xlsx(cmdb_path)
    except Exception as e:
        print(f"Ошибка чтения CMDB: {e}", file=sys.stderr)
        return 1

    store = ConfigStore(config_path)
    try:
        old_config = store.load()
    except Exception as e:
        print(f"Ошибка чтения config: {e}", file=sys.stderr)
        return 1

    merged, stats, errors = merge_recorders_from_cmdb(
        parsed.rows, old_config.recorders
    )

    print(f"CMDB: строк данных после заголовка — {parsed.total_data_rows}")
    print(f"Фильтр «{FUNCTIONAL_TYPE_VIDEO}»: {len(parsed.rows)} регистраторов")
    print(
        f"Пропущено: пустой IP — {parsed.skipped_empty_ip}, "
        f"другой тип — {parsed.skipped_wrong_type}"
    )

    if errors:
        print("Ошибки валидации (config не изменён):", file=sys.stderr)
        for err in errors:
            print(f"  строка {err.source_row}: {err.message}", file=sys.stderr)
        return 1

    print(
        f"Итог: сохранено по IP — {stats.preserved}, новых — {stats.added}, "
        f"удалено из старого config — {stats.removed}"
    )

    if args.dry_run:
        print("Dry-run: запись в config пропущена.")
        return 0

    new_config = AppConfig(
        credentials=old_config.credentials,
        monitoring=old_config.monitoring,
        recorders=merged,
    )
    try:
        AppConfig.model_validate(new_config.model_dump(mode="json"))
    except Exception as e:
        print(f"Ошибка валидации итогового config: {e}", file=sys.stderr)
        return 1

    if not args.no_backup and config_path.exists():
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = config_path.with_suffix(f".json.bak.{ts}")
        shutil.copy2(config_path, backup_path)
        print(f"Резервная копия: {backup_path}")

    store.save(new_config)
    print(f"Записано: {config_path} ({len(merged)} регистраторов)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
