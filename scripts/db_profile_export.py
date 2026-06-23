#!/usr/bin/env python3
"""
Профилирование SQLite-базы monitoring.db для генерации тестовых данных.

Собирает по каждой таблице:
  - количество строк;
  - заполненность столбцов (non-NULL, для TEXT — без пустых строк);
  - min / max / avg / stddev для числовых столбцов;
  - распределение значений для категориальных (TEXT, enum, boolean-like INTEGER);
  - 5–10 примеров строк (случайная выборка).

Результат — JSON (основной) и опционально плоский CSV со статистикой столбцов.

Запуск (из корня репозитория):
  python scripts/db_profile_export.py
  python scripts/db_profile_export.py --db data/monitoring.db -o data/reports/db_profile.json
  python scripts/db_profile_export.py --samples 8 --csv

Переменные окружения:
  STATE_DB_PATH — путь к monitoring.db
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = ROOT / "data" / "monitoring.db"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "reports"

# Пороги классификации столбцов
MAX_CATEGORICAL_DISTINCT = 80
MAX_DISTRIBUTION_ITEMS = 30
TEXT_SAMPLE_VALUES = 10
LONG_TEXT_THRESHOLD = 500
TRUNCATE_AT = 400

# INTEGER-столбцы с малым числом distinct — категориальные (0/1, enum)
BOOLEAN_LIKE_MAX_DISTINCT = 5


@dataclass(frozen=True)
class ColumnInfo:
    name: str
    declared_type: str
    not_null: bool
    primary_key: bool
    default_value: Optional[str]


def _default_output_path() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return DEFAULT_OUTPUT_DIR / f"db_profile_{stamp}.json"


def _connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.is_file():
        raise FileNotFoundError(f"База не найдена: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _list_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()
    return [row[0] for row in rows]


def _table_ddl(conn: sqlite3.Connection, table: str) -> Optional[str]:
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()
    return row[0] if row else None


def _column_infos(conn: sqlite3.Connection, table: str) -> list[ColumnInfo]:
    return [
        ColumnInfo(
            name=row[1],
            declared_type=(row[2] or "").upper(),
            not_null=bool(row[3]),
            default_value=row[4],
            primary_key=bool(row[5]),
        )
        for row in conn.execute(f"PRAGMA table_info({_quote_ident(table)})")
    ]


def _row_count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {_quote_ident(table)}").fetchone()[0])


def _fill_rate(
    conn: sqlite3.Connection,
    table: str,
    column: ColumnInfo,
    total_rows: int,
) -> dict[str, Any]:
    col = _quote_ident(column.name)
    tbl = _quote_ident(table)
    if total_rows == 0:
        return {
            "total_rows": 0,
            "non_null": 0,
            "filled": 0,
            "fill_percent": None,
        }

    non_null = int(
        conn.execute(f"SELECT COUNT({col}) FROM {tbl}").fetchone()[0]
    )
    if "TEXT" in column.declared_type or column.declared_type == "":
        filled = int(
            conn.execute(
                f"SELECT COUNT(*) FROM {tbl} WHERE {col} IS NOT NULL AND TRIM({col}) != ''"
            ).fetchone()[0]
        )
    else:
        filled = non_null

    return {
        "total_rows": total_rows,
        "non_null": non_null,
        "filled": filled,
        "fill_percent": round(100.0 * filled / total_rows, 2),
    }


def _distinct_count(conn: sqlite3.Connection, table: str, column: str) -> int:
    col = _quote_ident(column)
    tbl = _quote_ident(table)
    return int(
        conn.execute(f"SELECT COUNT(DISTINCT {col}) FROM {tbl}").fetchone()[0]
    )


def _is_numeric_type(declared_type: str) -> bool:
    upper = declared_type.upper()
    return "INT" in upper or "REAL" in upper or "FLOAT" in upper or "NUM" in upper


def _numeric_stats(
    conn: sqlite3.Connection,
    table: str,
    column: str,
) -> Optional[dict[str, Any]]:
    col = _quote_ident(column)
    tbl = _quote_ident(table)
    row = conn.execute(
        f"""
        SELECT
            MIN({col}) AS min_v,
            MAX({col}) AS max_v,
            AVG({col}) AS avg_v,
            COUNT({col}) AS non_null
        FROM {tbl}
        """
    ).fetchone()
    if not row or row["non_null"] == 0:
        return None

    result: dict[str, Any] = {
        "kind": "numeric",
        "min": row["min_v"],
        "max": row["max_v"],
        "avg": round(float(row["avg_v"]), 4) if row["avg_v"] is not None else None,
        "non_null": int(row["non_null"]),
    }

    # stddev через отдельный запрос — проще, чем тянуть расширения
    std_row = conn.execute(
        f"""
        SELECT
            SUM(({col} - sub.avg_v) * ({col} - sub.avg_v)) / COUNT({col}) AS variance
        FROM {tbl}, (SELECT AVG({col}) AS avg_v FROM {tbl} WHERE {col} IS NOT NULL) AS sub
        WHERE {col} IS NOT NULL
        """
    ).fetchone()
    if std_row and std_row[0] is not None:
        result["stddev"] = round(math.sqrt(float(std_row[0])), 4)

    result["distinct_count"] = _distinct_count(conn, table, column)
    return result


def _categorical_distribution(
    conn: sqlite3.Connection,
    table: str,
    column: str,
    total_rows: int,
) -> dict[str, Any]:
    col = _quote_ident(column)
    tbl = _quote_ident(table)
    distinct = _distinct_count(conn, table, column)

    rows = conn.execute(
        f"""
        SELECT {col} AS value, COUNT(*) AS cnt
        FROM {tbl}
        GROUP BY {col}
        ORDER BY cnt DESC, value
        LIMIT ?
        """,
        (MAX_DISTRIBUTION_ITEMS,),
    ).fetchall()

    distribution = []
    for row in rows:
        value = row["value"]
        count = int(row["cnt"])
        item: dict[str, Any] = {
            "value": value,
            "count": count,
            "percent": round(100.0 * count / total_rows, 2) if total_rows else 0,
        }
        if isinstance(value, str) and len(value) > TRUNCATE_AT:
            item["value"] = value[:TRUNCATE_AT] + "…"
            item["truncated"] = True
        distribution.append(item)

    return {
        "kind": "categorical",
        "distinct_count": distinct,
        "distribution": distribution,
        "distribution_truncated": distinct > len(distribution),
    }


def _text_summary(
    conn: sqlite3.Connection,
    table: str,
    column: str,
    total_rows: int,
) -> dict[str, Any]:
    col = _quote_ident(column)
    tbl = _quote_ident(table)
    distinct = _distinct_count(conn, table, column)

    len_row = conn.execute(
        f"""
        SELECT
            MIN(LENGTH({col})) AS min_len,
            MAX(LENGTH({col})) AS max_len,
            AVG(LENGTH({col})) AS avg_len
        FROM {tbl}
        WHERE {col} IS NOT NULL AND TRIM({col}) != ''
        """
    ).fetchone()

    sample_rows = conn.execute(
        f"""
        SELECT DISTINCT {col} AS value
        FROM {tbl}
        WHERE {col} IS NOT NULL AND TRIM({col}) != ''
        ORDER BY RANDOM()
        LIMIT ?
        """,
        (TEXT_SAMPLE_VALUES,),
    ).fetchall()

    samples: list[Any] = []
    for row in sample_rows:
        value = row["value"]
        if isinstance(value, str) and len(value) > TRUNCATE_AT:
            samples.append({"value": value[:TRUNCATE_AT] + "…", "truncated": True})
        else:
            samples.append(value)

    result: dict[str, Any] = {
        "kind": "text_high_cardinality",
        "distinct_count": distinct,
        "sample_values": samples,
    }
    if len_row and len_row["min_len"] is not None:
        result["length"] = {
            "min": int(len_row["min_len"]),
            "max": int(len_row["max_len"]),
            "avg": round(float(len_row["avg_len"]), 2),
        }

    is_json = column.endswith("_json")
    if is_json or (len_row and len_row["max_len"] and int(len_row["max_len"]) > LONG_TEXT_THRESHOLD):
        result["note"] = "вероятно JSON или длинный текст — в примерах строк см. полные значения"

    return result


def _column_stats(
    conn: sqlite3.Connection,
    table: str,
    column: ColumnInfo,
    total_rows: int,
) -> dict[str, Any]:
    if total_rows == 0:
        return {"kind": "empty_table"}

    distinct = _distinct_count(conn, table, column.name)
    numeric_type = _is_numeric_type(column.declared_type)

    if numeric_type:
        if distinct <= BOOLEAN_LIKE_MAX_DISTINCT:
            cat = _categorical_distribution(conn, table, column.name, total_rows)
            cat["kind"] = "boolean_or_enum_integer"
            return cat
        stats = _numeric_stats(conn, table, column.name)
        if stats:
            return stats

    if distinct <= MAX_CATEGORICAL_DISTINCT:
        return _categorical_distribution(conn, table, column.name, total_rows)

    return _text_summary(conn, table, column.name, total_rows)


def _serialize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (int, float, str, bool)):
        if isinstance(value, str) and len(value) > LONG_TEXT_THRESHOLD:
            return value[:TRUNCATE_AT] + "…"
        return value
    return str(value)


def _sample_rows(
    conn: sqlite3.Connection,
    table: str,
    columns: list[ColumnInfo],
    sample_count: int,
    total_rows: int,
) -> list[dict[str, Any]]:
    if total_rows == 0:
        return []

    count = min(sample_count, total_rows)
    tbl = _quote_ident(table)
    col_names = ", ".join(_quote_ident(c.name) for c in columns)
    rows = conn.execute(
        f"SELECT {col_names} FROM {tbl} ORDER BY RANDOM() LIMIT ?",
        (count,),
    ).fetchall()

    result: list[dict[str, Any]] = []
    for row in rows:
        item = {col.name: _serialize_value(row[col.name]) for col in columns}
        result.append(item)
    return result


def _profile_table(
    conn: sqlite3.Connection,
    table: str,
    sample_count: int,
) -> dict[str, Any]:
    columns = _column_infos(conn, table)
    total_rows = _row_count(conn, table)

    column_profiles: list[dict[str, Any]] = []
    for col in columns:
        column_profiles.append(
            {
                "name": col.name,
                "declared_type": col.declared_type or "TEXT",
                "not_null": col.not_null,
                "primary_key": col.primary_key,
                "default": col.default_value,
                "fill_rate": _fill_rate(conn, table, col, total_rows),
                "value_stats": _column_stats(conn, table, col, total_rows),
            }
        )

    return {
        "ddl": _table_ddl(conn, table),
        "row_count": total_rows,
        "columns": column_profiles,
        "sample_rows": _sample_rows(conn, table, columns, sample_count, total_rows),
    }


def _export_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)


def _export_csv(payload: dict[str, Any], path: Path) -> None:
    """Плоский CSV: одна строка на столбец каждой таблицы."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "table",
        "row_count",
        "column",
        "declared_type",
        "not_null",
        "primary_key",
        "fill_percent",
        "non_null",
        "filled",
        "stats_kind",
        "distinct_count",
        "min",
        "max",
        "avg",
        "stddev",
        "top_values",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for table_name, table_data in payload["tables"].items():
            row_count = table_data["row_count"]
            for col in table_data["columns"]:
                stats = col.get("value_stats") or {}
                top_values = ""
                if stats.get("kind") in {
                    "categorical",
                    "boolean_or_enum_integer",
                }:
                    parts = []
                    for item in stats.get("distribution", [])[:10]:
                        val = item.get("value")
                        val_repr = json.dumps(val, ensure_ascii=False) if val is not None else "NULL"
                        parts.append(f"{val_repr}:{item['count']}")
                    top_values = "; ".join(parts)

                writer.writerow(
                    {
                        "table": table_name,
                        "row_count": row_count,
                        "column": col["name"],
                        "declared_type": col["declared_type"],
                        "not_null": col["not_null"],
                        "primary_key": col["primary_key"],
                        "fill_percent": col["fill_rate"].get("fill_percent"),
                        "non_null": col["fill_rate"].get("non_null"),
                        "filled": col["fill_rate"].get("filled"),
                        "stats_kind": stats.get("kind"),
                        "distinct_count": stats.get("distinct_count"),
                        "min": stats.get("min"),
                        "max": stats.get("max"),
                        "avg": stats.get("avg"),
                        "stddev": stats.get("stddev"),
                        "top_values": top_values,
                    }
                )


def build_profile(
    db_path: Path,
    sample_count: int = 8,
) -> dict[str, Any]:
    conn = _connect(db_path)
    try:
        tables = _list_tables(conn)
        sqlite_version = conn.execute("SELECT sqlite_version()").fetchone()[0]
        profile_tables: dict[str, Any] = {}
        for table in tables:
            profile_tables[table] = _profile_table(conn, table, sample_count)

        return {
            "meta": {
                "db_path": str(db_path.resolve()),
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "sqlite_version": sqlite_version,
                "table_count": len(tables),
                "sample_rows_per_table": sample_count,
            },
            "tables": profile_tables,
        }
    finally:
        conn.close()


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Профилирование monitoring.db для генерации тестовой БД",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(os.environ.get("STATE_DB_PATH", str(DEFAULT_DB_PATH))),
        help=f"Путь к SQLite (по умолчанию: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Путь к JSON-отчёту (по умолчанию: data/reports/db_profile_YYYYMMDD_HHMMSS.json)",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=8,
        metavar="N",
        help="Число примеров строк на таблицу (5–10 рекомендуется, по умолчанию 8)",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Дополнительно сохранить плоский CSV со статистикой столбцов",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    if args.samples < 1:
        print("Ошибка: --samples должен быть >= 1", file=sys.stderr)
        return 2

    output_json = args.output or _default_output_path()
    try:
        payload = build_profile(args.db.resolve(), sample_count=args.samples)
    except FileNotFoundError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1

    _export_json(payload, output_json)
    print(f"JSON: {output_json}")

    if args.csv:
        csv_path = output_json.with_suffix(".csv")
        _export_csv(payload, csv_path)
        print(f"CSV:  {csv_path}")

    meta = payload["meta"]
    print(
        f"Таблиц: {meta['table_count']}, "
        f"примеров на таблицу: {meta['sample_rows_per_table']}"
    )
    for name, data in payload["tables"].items():
        print(f"  {name}: {data['row_count']} строк")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
