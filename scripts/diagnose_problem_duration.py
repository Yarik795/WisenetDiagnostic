#!/usr/bin/env python3
"""
Диагностика длительности проблем по таблице category_status_history.

Запуск (из корня репозитория или с указанием пути к БД):
  python scripts/diagnose_problem_duration.py
  python scripts/diagnose_problem_duration.py --category temperature
  python scripts/diagnose_problem_duration.py --db "D:/path/to/monitoring.db"

Переменные окружения (переопределяют значения по умолчанию ниже):
  STATE_DB_PATH — путь к SQLite (monitoring.db)
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# --- Настройки подключения (можно менять здесь или через env / CLI) ---

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "monitoring.db"
STATE_DB_PATH = Path(os.environ.get("STATE_DB_PATH", str(DEFAULT_DB_PATH)))

# Категория по умолчанию: temperature | time | storage | fans | channels | archive
DEFAULT_CATEGORY = "temperature"

# Ограничение, как в production StateStore.list_category_history
APP_HISTORY_LIMIT = 500

_CATEGORY_PROBLEM_STATUSES = frozenset({"warn", "error"})
_TRANSPARENT_GAP_STATUSES = frozenset({"unknown"})

CATEGORY_LABELS = {
    "time": "Время / NTP",
    "temperature": "Температура HDD",
    "storage": "Накопители",
    "fans": "Вентиляторы",
    "channels": "Каналы",
    "archive": "Глубина архива",
}


@dataclass
class HistoryRow:
    id: int
    recorder_id: str
    category: str
    status: str
    reason: Optional[str]
    recorded_at: datetime


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.is_file():
        raise FileNotFoundError(f"База не найдена: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='category_status_history'"
    ).fetchone()
    if row is None:
        conn.close()
        raise RuntimeError(
            f"В {db_path} нет таблицы category_status_history. "
            "Убедитесь, что backend хотя бы раз опрашивал устройства после обновления."
        )
    return conn


def _fetch_history(
    conn: sqlite3.Connection,
    *,
    recorder_id: Optional[str] = None,
    category: Optional[str] = None,
    limit: Optional[int] = None,
    order_asc: bool = True,
) -> list[HistoryRow]:
    sql = "SELECT * FROM category_status_history WHERE 1=1"
    params: list = []
    if recorder_id:
        sql += " AND recorder_id = ?"
        params.append(recorder_id)
    if category:
        sql += " AND category = ?"
        params.append(category)
    sql += f" ORDER BY recorded_at {'ASC' if order_asc else 'DESC'}"
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    if not order_asc:
        rows = list(reversed(rows))
    result: list[HistoryRow] = []
    for row in rows:
        result.append(
            HistoryRow(
                id=row["id"],
                recorder_id=row["recorder_id"],
                category=row["category"],
                status=row["status"],
                reason=row["reason"],
                recorded_at=_parse_iso(row["recorded_at"])
                or datetime.now(timezone.utc),
            )
        )
    return result


def problem_episode_start(rows: list[HistoryRow]) -> Optional[datetime]:
    """Логика backend: app.state_store._problem_episode_start."""
    if not rows:
        return None
    latest = rows[-1]
    if latest.status not in _CATEGORY_PROBLEM_STATUSES:
        return None
    start = latest.recorded_at
    for row in reversed(rows[:-1]):
        if row.status in _CATEGORY_PROBLEM_STATUSES:
            start = row.recorded_at
        elif row.status in _TRANSPARENT_GAP_STATUSES:
            continue
        else:
            break
    return start


def format_problem_age_display(since: datetime, ref: datetime) -> str:
    """Как в HTML-отчёте после правки: app.ui.error_report.format_problem_age_display."""
    if since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    if ref.tzinfo is None:
        ref = ref.replace(tzinfo=timezone.utc)
    total_seconds = max(0.0, (ref - since).total_seconds())
    days = int(total_seconds // 86400)
    hours = int((total_seconds % 86400) // 3600)
    if days >= 1:
        if hours > 0:
            return f"{days} сут. {hours} ч."
        return f"{days} сут."
    if hours >= 1:
        return f"{hours} ч."
    return "менее 1 ч."


def list_pairs(
    conn: sqlite3.Connection,
    *,
    category: Optional[str],
    recorder_id: Optional[str],
) -> list[tuple[str, str]]:
    sql = """
        SELECT DISTINCT recorder_id, category
        FROM category_status_history
        WHERE 1=1
    """
    params: list = []
    if category:
        sql += " AND category = ?"
        params.append(category)
    if recorder_id:
        sql += " AND recorder_id = ?"
        params.append(recorder_id)
    sql += " ORDER BY recorder_id, category"
    return [(r["recorder_id"], r["category"]) for r in conn.execute(sql, params)]


def load_recorder_names(config_path: Path) -> dict[str, str]:
    if not config_path.is_file():
        return {}
    try:
        import json

        data = json.loads(config_path.read_text(encoding="utf-8"))
        out: dict[str, str] = {}
        for rec in data.get("recorders", []):
            rid = rec.get("id")
            if not rid:
                continue
            name = rec.get("name") or rec.get("host") or rid
            obj = rec.get("object_name") or ""
            out[rid] = f"{obj} / {name}" if obj else str(name)
        return out
    except Exception as exc:
        print(f"Предупреждение: не удалось прочитать {config_path}: {exc}", file=sys.stderr)
        return {}


def diagnose_pair(
    conn: sqlite3.Connection,
    recorder_id: str,
    category: str,
    *,
    ref: datetime,
    names: dict[str, str],
    verbose_history: int,
) -> None:
    full = _fetch_history(conn, recorder_id=recorder_id, category=category)
    limited = full[-APP_HISTORY_LIMIT:] if len(full) > APP_HISTORY_LIMIT else full

    since_app = problem_episode_start(limited)
    since_full = problem_episode_start(full)
    latest = full[-1] if full else None

    label = CATEGORY_LABELS.get(category, category)
    display_name = names.get(recorder_id, recorder_id)

    print("=" * 72)
    print(f"Регистратор: {display_name}")
    print(f"  id={recorder_id}")
    print(f"Категория:   {label} ({category})")
    print(f"Записей в истории: {len(full)} (в отчёт backend берёт до {APP_HISTORY_LIMIT} старых)")

    if latest:
        print(
            f"Последний статус: {latest.status} @ "
            f"{latest.recorded_at.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        )
        if latest.reason:
            print(f"  причина: {latest.reason}")

    if since_full is None:
        print("Текущая проблема: нет (последний статус ok/unknown)")
        if latest and latest.status == "unknown":
            print(
                "  Примечание: статус unknown прерывает эпизод warn/error "
                "в логике backend (см. анализ в документации)."
            )
    else:
        age_display = format_problem_age_display(since_full, ref)
        print(f"Начало эпизода (полная история): {since_full.strftime('%d.%m.%Y %H:%M')}")
        print(f"Длительность до {ref.strftime('%d.%m.%Y %H:%M')} UTC:")
        print(f"  как в HTML-отчёте:             {age_display}")
        delta = ref - since_full
        print(
            f"  точнее: {delta.days} дн. + {delta.seconds // 3600} ч. "
            f"({delta.total_seconds():.0f} с)"
        )

    if since_app != since_full:
        print("!!! РАСХОЖДЕНИЕ: backend (limit=500 ASC) даёт другую дату начала:")
        if since_app:
            print(f"    backend since: {since_app.strftime('%d.%m.%Y %H:%M')}")
            print(f"    backend age:   {format_problem_age_display(since_app, ref)}")
        else:
            print("    backend since: — (проблема не определяется)")
        print(
            "    Причина: в list_category_history берутся первые 500 записей "
            "по времени, а не последние."
        )

    if verbose_history > 0 and full:
        print(f"\nПоследние {verbose_history} переходов:")
        for row in full[-verbose_history:]:
            ts = row.recorded_at.strftime("%Y-%m-%d %H:%M")
            reason = f" — {row.reason}" if row.reason else ""
            print(f"  [{row.id:5d}] {ts}  {row.status:7s}{reason}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Диагностика длительности проблем (category_status_history)"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=STATE_DB_PATH,
        help=f"Путь к monitoring.db (по умолчанию {STATE_DB_PATH})",
    )
    parser.add_argument(
        "--category",
        default=DEFAULT_CATEGORY,
        help=f"Категория: {', '.join(CATEGORY_LABELS)} или пусто для всех",
    )
    parser.add_argument("--recorder-id", help="Фильтр по id регистратора")
    parser.add_argument(
        "--only-active",
        action="store_true",
        help="Показывать только пары с текущим warn/error",
    )
    parser.add_argument(
        "--history",
        type=int,
        default=8,
        metavar="N",
        help="Сколько последних переходов показать (0 — скрыть)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "config.json",
        help="config.json для имён объектов (необязательно)",
    )
    parser.add_argument(
        "--at",
        help="Момент отсчёта ISO (по умолчанию — сейчас UTC)",
    )
    args = parser.parse_args()

    ref = (
        _parse_iso(args.at)
        if args.at
        else datetime.now(timezone.utc)
    )

    try:
        conn = _connect(args.db)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1

    names = load_recorder_names(args.config)
    category = args.category.strip() or None

    print(f"База: {args.db.resolve()}")
    print(f"Момент отсчёта: {ref.isoformat()}")
    if category:
        print(f"Фильтр категории: {category} ({CATEGORY_LABELS.get(category, '?')})")
    print()

    pairs = list_pairs(conn, category=category, recorder_id=args.recorder_id)
    if not pairs:
        print("Записей не найдено.")
        return 0

    shown = 0
    for recorder_id, cat in pairs:
        full = _fetch_history(conn, recorder_id=recorder_id, category=cat)
        since = problem_episode_start(full)
        if args.only_active and since is None:
            continue
        diagnose_pair(
            conn,
            recorder_id,
            cat,
            ref=ref,
            names=names,
            verbose_history=args.history,
        )
        shown += 1

    if shown == 0:
        print("Нет активных проблем по заданным фильтрам.")
    else:
        print("=" * 72)
        print(f"Показано записей: {shown}")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
