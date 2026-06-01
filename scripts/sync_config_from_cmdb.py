#!/usr/bin/env python3
"""Замена списка recorders в config.json данными из cmdb.xlsx."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.cmdb_sync import (  # noqa: E402
    DEFAULT_CMDB_PATH,
    cmdb_sync_report_lines,
    sync_from_cmdb,
)
from app.config_store import ConfigStore  # noqa: E402


def _default_config() -> Path:
    return ROOT / "config.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Обновить recorders в config.json из CMDB (Excel)"
    )
    parser.add_argument(
        "--cmdb",
        type=Path,
        default=DEFAULT_CMDB_PATH,
        help="Путь к cmdb.xlsx (по умолчанию: cmdb.xlsx в корне проекта)",
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
    store = ConfigStore(config_path)

    result = sync_from_cmdb(
        store,
        cmdb_path,
        backup=not args.no_backup,
        dry_run=args.dry_run,
    )

    for line in cmdb_sync_report_lines(result):
        print(line)

    if not result.ok:
        if result.merge_errors:
            print("Ошибки валидации (config не изменён):", file=sys.stderr)
            for err in result.merge_errors:
                print(f"  строка {err.source_row}: {err.message}", file=sys.stderr)
        else:
            print(f"Ошибка: {result.message}", file=sys.stderr)
        return 1

    print(result.message)

    if args.dry_run:
        print("Dry-run: запись в config пропущена.")
        return 0

    print(f"Записано: {config_path} ({result.total_recorders} регистраторов)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
