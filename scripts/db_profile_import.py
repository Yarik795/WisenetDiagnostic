#!/usr/bin/env python3
"""
Создание тестовой monitoring.db по JSON-профилю (выход db_profile_export.py).

Генерирует строки в количестве row_count каждой таблицы, подбирая значения
по распределениям и числовым диапазонам из профиля. Примеры sample_rows
используются как шаблоны.

Запуск (из корня репозитория):
  python scripts/db_profile_import.py data/reports/db_profile_20260623_191656.json
  python scripts/db_profile_import.py profile.json --db data/monitoring.db --sync-config

Переменные окружения:
  STATE_DB_PATH — путь к целевой SQLite
"""

from __future__ import annotations

import argparse
import json
import os
import random
import secrets
import shutil
import sqlite3
import sys
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Optional

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
DEFAULT_DB_PATH = ROOT / "data" / "monitoring.db"
DEFAULT_CONFIG_PATH = ROOT / "config.json"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.chat_store import ChatStore  # noqa: E402
from app.config_store import ConfigStore  # noqa: E402
from app.models import CheckStatus, Recorder  # noqa: E402
from app.state_store import StateStore  # noqa: E402

TABLE_INSERT_ORDER = [
    "recorder_metrics",
    "channels",
    "category_status_history",
    "status_history",
    "recorder_poll_attempts",
    "source_imports",
    "naumen_records",
    "arsenal_analytics",
    "arsenal_systems",
    "chat_sessions",
    "chat_messages",
]

BATCH_SIZE = 2000


@dataclass
class SharedPools:
    rng: random.Random
    recorder_ids: list[str] = field(default_factory=list)
    channel_pairs: set[tuple[str, int]] = field(default_factory=set)
    passport_numbers: set[str] = field(default_factory=set)
    external_ids: set[str] = field(default_factory=set)
    session_ids: list[str] = field(default_factory=list)
    job_ids: list[str] = field(default_factory=list)
    entity_ids: set[str] = field(default_factory=set)
    channel_counters: dict[str, int] = field(default_factory=lambda: defaultdict(int))


def _quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _normalize_value(value: Any) -> Any:
    if isinstance(value, dict) and "value" in value:
        return value["value"]
    return value


def _harvest_strings(profile: dict[str, Any], *field_names: str) -> set[str]:
    found: set[str] = set()
    for table in profile["tables"].values():
        for row in table.get("sample_rows", []):
            for name in field_names:
                val = row.get(name)
                if isinstance(val, str) and val.strip():
                    found.add(val.strip())
        for col in table.get("columns", []):
            if col["name"] not in field_names:
                continue
            stats = col.get("value_stats") or {}
            for item in stats.get("sample_values", []):
                val = _normalize_value(item)
                if isinstance(val, str) and val.strip():
                    found.add(val.strip())
            for item in stats.get("distribution", []):
                val = _normalize_value(item.get("value"))
                if isinstance(val, str) and val.strip():
                    found.add(val.strip())
    return found


def _device_kind_from_id(recorder_id: str) -> str:
    if recorder_id.startswith("bio-"):
        return "bio"
    if recorder_id.startswith("skud-"):
        return "skud"
    if recorder_id.startswith("sots-"):
        return "sots"
    return "tsv"


def _build_recorder_pool(profile: dict[str, Any], count: int, rng: random.Random) -> list[str]:
    harvested = _harvest_strings(profile, "recorder_id")
    harvested.update(
        rid
        for rid in harvested.copy()
        if rid.startswith(("nvr-", "bio-", "skud-", "sots-"))
    )
    ids = {rid for rid in harvested if "-" in rid}
    prefixes = ["nvr", "bio", "skud", "sots"]
    weights = [0.82, 0.08, 0.06, 0.04]
    while len(ids) < count:
        prefix = rng.choices(prefixes, weights=weights, k=1)[0]
        ids.add(f"{prefix}-{secrets.token_hex(4)}")
    result = sorted(ids)
    rng.shuffle(result)
    return result[:count]


def _weighted_pick(
    distribution: list[dict[str, Any]],
    rng: random.Random,
    *,
    allow_null: bool,
) -> Any:
    items = []
    weights = []
    for item in distribution:
        value = _normalize_value(item.get("value"))
        if value is None and not allow_null:
            continue
        items.append(value)
        weights.append(max(int(item.get("count", 1)), 1))
    if not items:
        return None
    return rng.choices(items, weights=weights, k=1)[0]


def _numeric_pick(stats: dict[str, Any], rng: random.Random) -> Any:
    lo = stats.get("min")
    hi = stats.get("max")
    avg = stats.get("avg")
    if lo is None or hi is None:
        return avg
    if lo == hi:
        return lo
    if avg is not None and lo <= avg <= hi:
        return round(rng.triangular(float(lo), float(hi), float(avg)), 4)
    return round(rng.uniform(float(lo), float(hi)), 4)


def _text_pick(stats: dict[str, Any], rng: random.Random, row_idx: int) -> Any:
    samples = [_normalize_value(v) for v in stats.get("sample_values", [])]
    samples = [v for v in samples if v is not None]
    if samples:
        return rng.choice(samples)
    length = stats.get("length") or {}
    target_len = int(length.get("avg") or 12)
    return f"synth-{row_idx}-{secrets.token_hex(4)}"[: max(target_len, 8)]


class ColumnGenerator:
    def __init__(
        self,
        col: dict[str, Any],
        table_name: str,
        pools: SharedPools,
        custom: Optional[Callable[[int, dict[str, Any]], Any]] = None,
    ) -> None:
        self.col = col
        self.table_name = table_name
        self.pools = pools
        self.custom = custom
        self.stats = col.get("value_stats") or {}
        self.fill_percent = col.get("fill_rate", {}).get("fill_percent")
        self.counter = 0

    def should_null(self) -> bool:
        if self.col.get("not_null"):
            return False
        if self.fill_percent is None:
            return False
        return self.pools.rng.random() * 100 > float(self.fill_percent)

    def generate(self, row_idx: int, template: dict[str, Any]) -> Any:
        if self.custom:
            return self.custom(row_idx, template)
        name = self.col["name"]
        if self.should_null():
            return None
        if name in template and template[name] is not None and self.pools.rng.random() < 0.35:
            return template[name]

        kind = self.stats.get("kind")
        if kind in {"categorical", "boolean_or_enum_integer"}:
            dist = self.stats.get("distribution") or []
            return _weighted_pick(dist, self.pools.rng, allow_null=not self.col.get("not_null"))
        if kind == "numeric":
            return _numeric_pick(self.stats, self.pools.rng)
        if kind == "text_high_cardinality":
            return _text_pick(self.stats, self.pools.rng, row_idx)
        if kind == "empty_table":
            return None
        return template.get(name)


def _make_generators(
    table_name: str,
    columns: list[dict[str, Any]],
    pools: SharedPools,
) -> dict[str, ColumnGenerator]:
    gens: dict[str, ColumnGenerator] = {}

    def recorder_id_gen(row_idx: int, template: dict[str, Any]) -> Any:
        if pools.recorder_ids:
            return pools.recorder_ids[row_idx % len(pools.recorder_ids)]
        return template.get("recorder_id") or f"nvr-{secrets.token_hex(4)}"

    def channel_pair_gen(row_idx: int, template: dict[str, Any]) -> Any:
        return None  # handled in row builder

    custom: dict[str, Callable[[int, dict[str, Any]], Any]] = {}
    if table_name in {
        "recorder_metrics",
        "category_status_history",
        "recorder_poll_attempts",
    }:
        custom["recorder_id"] = recorder_id_gen

    if table_name == "channels":
        def channel_no(_row_idx: int, template: dict[str, Any]) -> Any:
            return template.get("channel_no", 0)

        custom["channel_no"] = channel_no

    if table_name == "arsenal_analytics":
        def passport_gen(_row_idx: int, _template: dict[str, Any]) -> Any:
            while True:
                candidate = f"{pools.rng.randint(100000, 999999)}"
                if candidate not in pools.passport_numbers:
                    pools.passport_numbers.add(candidate)
                    return candidate

        custom["passport_number"] = passport_gen

    if table_name == "naumen_records":
        def external_id_gen(_row_idx: int, _template: dict[str, Any]) -> Any:
            while True:
                candidate = secrets.token_hex(8)
                if candidate not in pools.external_ids:
                    pools.external_ids.add(candidate)
                    return candidate

        custom["external_id"] = external_id_gen

    if table_name == "chat_sessions":
        def session_id_gen(_row_idx: int, template: dict[str, Any]) -> Any:
            val = template.get("id")
            if isinstance(val, str):
                return val
            return str(uuid.uuid4())

        custom["id"] = session_id_gen

    if table_name == "chat_messages":
        def session_ref(row_idx: int, _template: dict[str, Any]) -> Any:
            if pools.session_ids:
                return pools.session_ids[row_idx % len(pools.session_ids)]
            return str(uuid.uuid4())

        custom["session_id"] = session_ref

    if table_name == "status_history":
        def entity_id_gen(row_idx: int, template: dict[str, Any]) -> Any:
            if template.get("entity_id"):
                base = template["entity_id"]
            elif pools.recorder_ids:
                rid = pools.recorder_ids[row_idx % len(pools.recorder_ids)]
                base = f"{rid}:{row_idx % 32}"
            else:
                base = f"nvr-{secrets.token_hex(4)}:{row_idx % 32}"
            if base in pools.entity_ids and pools.rng.random() < 0.7:
                return base
            pools.entity_ids.add(base)
            return base

        custom["entity_id"] = entity_id_gen

    if table_name == "recorder_poll_attempts":
        def job_id_gen(row_idx: int, template: dict[str, Any]) -> Any:
            if pools.job_ids:
                return pools.job_ids[row_idx % len(pools.job_ids)]
            return template.get("job_id") or secrets.token_hex(6)

        custom["job_id"] = job_id_gen

    for col in columns:
        gens[col["name"]] = ColumnGenerator(
            col,
            table_name,
            pools,
            custom=custom.get(col["name"]),
        )
    return gens


def _column_names(columns: list[dict[str, Any]], *, include_autoincrement_pk: bool) -> list[str]:
    names: list[str] = []
    for col in columns:
        if col.get("primary_key") and "INT" in (col.get("declared_type") or "").upper():
            if not include_autoincrement_pk:
                continue
        names.append(col["name"])
    return names


def _build_channel_row(row_idx: int, template: dict[str, Any], gens: dict[str, ColumnGenerator], pools: SharedPools) -> dict[str, Any]:
    for _ in range(50):
        recorder_id = pools.recorder_ids[row_idx % len(pools.recorder_ids)] if pools.recorder_ids else template.get("recorder_id")
        if not recorder_id:
            recorder_id = f"nvr-{secrets.token_hex(4)}"
        counters: dict[str, int] = pools.channel_counters
        channel_no = counters[recorder_id]
        counters[recorder_id] += 1
        pair = (recorder_id, channel_no)
        if pair in pools.channel_pairs:
            continue
        pools.channel_pairs.add(pair)
        row = dict(template)
        row["recorder_id"] = recorder_id
        row["channel_no"] = channel_no
        for name, gen in gens.items():
            if name in {"recorder_id", "channel_no", "id"}:
                continue
            row[name] = gen.generate(row_idx, row)
        return row
    row = dict(template)
    row["recorder_id"] = f"nvr-{secrets.token_hex(4)}"
    row["channel_no"] = row_idx
    for name, gen in gens.items():
        if name in {"recorder_id", "channel_no", "id"}:
            continue
        row[name] = gen.generate(row_idx, row)
    return row


def _build_row(
    table_name: str,
    row_idx: int,
    template: dict[str, Any],
    columns: list[dict[str, Any]],
    gens: dict[str, ColumnGenerator],
    pools: SharedPools,
) -> dict[str, Any]:
    if table_name == "channels":
        return _build_channel_row(row_idx, template, gens, pools)

    row = dict(template)
    insert_cols = _column_names(columns, include_autoincrement_pk=False)

    pk_cols = {c["name"] for c in columns if c.get("primary_key")}

    if table_name == "recorder_metrics" and pools.recorder_ids:
        row["recorder_id"] = pools.recorder_ids[row_idx]

    for name in insert_cols:
        if table_name == "recorder_metrics" and name == "recorder_id":
            continue
        if name in pk_cols:
            row[name] = gens[name].generate(row_idx, row)
            continue
        if name in row and row[name] is not None and name in template:
            if pools.rng.random() < 0.25:
                row[name] = gens[name].generate(row_idx, row)
            continue
        row[name] = gens[name].generate(row_idx, row)
    return {k: row.get(k) for k in insert_cols}


def _generate_rows(
    table_name: str,
    table_data: dict[str, Any],
    pools: SharedPools,
) -> list[dict[str, Any]]:
    target = int(table_data["row_count"])
    columns = table_data["columns"]
    samples = table_data.get("sample_rows") or []
    gens = _make_generators(table_name, columns, pools)
    insert_cols = _column_names(columns, include_autoincrement_pk=False)

    rows: list[dict[str, Any]] = []
    seen_pk: set[Any] = set()

    for sample in samples:
        row = _build_row(table_name, len(rows), sample, columns, gens, pools)
        pk_cols = [c["name"] for c in columns if c.get("primary_key")]
        pk_key = tuple(row.get(c) for c in pk_cols) if pk_cols else None
        if pk_key and None not in pk_key and pk_key in seen_pk:
            continue
        if pk_key and None not in pk_key:
            seen_pk.add(pk_key)
            if table_name == "arsenal_analytics" and row.get("passport_number"):
                pools.passport_numbers.add(str(row["passport_number"]))
            if table_name == "naumen_records" and row.get("external_id"):
                pools.external_ids.add(str(row["external_id"]))
        rows.append({k: row.get(k) for k in insert_cols})

    templates = samples if samples else [{}]
    while len(rows) < target:
        template = templates[len(rows) % len(templates)]
        row = _build_row(table_name, len(rows), template, columns, gens, pools)
        pk_cols = [c["name"] for c in columns if c.get("primary_key")]
        if pk_cols:
            pk_key = tuple(row.get(c) for c in pk_cols)
            if pk_key in seen_pk:
                row[pk_cols[0]] = None  # force regen for autoincrement
                if table_name == "naumen_records":
                    row["external_id"] = secrets.token_hex(8)
                elif table_name == "arsenal_analytics":
                    row["passport_number"] = f"{900000 + len(rows)}"
                elif table_name == "chat_sessions":
                    row["id"] = str(uuid.uuid4())
            else:
                seen_pk.add(pk_key)
        rows.append({k: row.get(k) for k in insert_cols})

    if table_name == "chat_sessions":
        pools.session_ids = [str(r["id"]) for r in rows if r.get("id")]

    if table_name == "recorder_poll_attempts":
        pools.job_ids = list(
            {
                str(r.get("job_id"))
                for r in rows
                if r.get("job_id")
            }
        )

    return rows


def _insert_rows(conn: sqlite3.Connection, table: str, columns: list[str], rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    col_sql = ", ".join(_quote_ident(c) for c in columns)
    placeholders = ", ".join("?" for _ in columns)
    sql = f"INSERT INTO {_quote_ident(table)} ({col_sql}) VALUES ({placeholders})"
    payload = [tuple(row.get(c) for c in columns) for row in rows]
    for offset in range(0, len(payload), BATCH_SIZE):
        conn.executemany(sql, payload[offset : offset + BATCH_SIZE])


def _backup_db(db_path: Path) -> Optional[Path]:
    if not db_path.is_file():
        return None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.with_name(f"{db_path.stem}.bak.{stamp}{db_path.suffix}")
    shutil.copy2(db_path, backup)
    return backup


def _init_schema(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.is_file():
        db_path.unlink()
    StateStore(path=db_path).init_db()
    ChatStore(path=db_path).init_db()


def import_profile(
    profile_path: Path,
    db_path: Path,
    *,
    seed: int = 42,
) -> dict[str, int]:
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    rng = random.Random(seed)
    pools = SharedPools(rng=rng)

    metrics_count = int(profile["tables"].get("recorder_metrics", {}).get("row_count", 0))
    if metrics_count:
        pools.recorder_ids = _build_recorder_pool(profile, metrics_count, rng)

    _init_schema(db_path)
    counts: dict[str, int] = {}

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        for table_name in TABLE_INSERT_ORDER:
            table_data = profile["tables"].get(table_name)
            if not table_data:
                continue
            rows = _generate_rows(table_name, table_data, pools)
            columns = _column_names(table_data["columns"], include_autoincrement_pk=False)
            _insert_rows(conn, table_name, columns, rows)
            counts[table_name] = len(rows)
            print(f"  {table_name}: {len(rows)} строк")
        conn.commit()
    return counts


def sync_config_from_metrics(db_path: Path, config_path: Path) -> int:
    store = ConfigStore(path=config_path)
    config = store.load()

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT recorder_id, model, device_online, health_status, health_reason
            FROM recorder_metrics
            ORDER BY recorder_id
            """
        ).fetchall()

    recorders: list[Recorder] = []
    for idx, row in enumerate(rows):
        rid = row["recorder_id"]
        kind = _device_kind_from_id(rid)
        model = (row["model"] or "").strip()
        online = bool(row["device_online"])
        recorders.append(
            Recorder(
                id=rid,
                object_name=model or f"Объект {rid}",
                name=model or rid,
                host=f"10.89.{(idx // 256) % 256}.{(idx % 254) + 1}",
                port=80,
                use_https=False,
                device_kind=kind,  # type: ignore[arg-type]
                mac=None,
                last_status=CheckStatus.ONLINE if online else CheckStatus.OFFLINE,
                last_check_at=datetime.now(timezone.utc),
                last_error=row["health_reason"] if row["health_status"] == "error" else None,
            )
        )

    config.recorders = recorders
    store.save(config)
    return len(recorders)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Создание monitoring.db из JSON-профиля")
    parser.add_argument("profile", type=Path, help="Путь к db_profile_*.json")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(os.environ.get("STATE_DB_PATH", str(DEFAULT_DB_PATH))),
        help=f"Целевая SQLite (по умолчанию: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="config.json для синхронизации списка регистраторов",
    )
    parser.add_argument(
        "--sync-config",
        action="store_true",
        help="Заполнить config.json регистраторами из recorder_metrics",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed генератора случайных чисел")
    parser.add_argument("--no-backup", action="store_true", help="Не создавать .bak копию текущей БД")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    profile_path = args.profile.resolve()
    db_path = args.db.resolve()

    if not profile_path.is_file():
        print(f"Ошибка: профиль не найден: {profile_path}", file=sys.stderr)
        return 1

    if not args.no_backup:
        backup = _backup_db(db_path)
        if backup:
            print(f"Резервная копия: {backup}")

    print(f"Профиль: {profile_path}")
    print(f"База:    {db_path}")
    print("Импорт таблиц:")
    counts = import_profile(profile_path, db_path, seed=args.seed)
    total = sum(counts.values())
    print(f"Готово: {len(counts)} таблиц, {total} строк")

    if args.sync_config:
        if not args.config.is_file():
            print(f"Предупреждение: config не найден ({args.config}), пропуск sync", file=sys.stderr)
        else:
            n = sync_config_from_metrics(db_path, args.config.resolve())
            print(f"config.json: обновлено регистраторов — {n}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
