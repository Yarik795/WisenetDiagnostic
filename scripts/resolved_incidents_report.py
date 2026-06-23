#!/usr/bin/env python3
"""
Отчёт по устранённым инцидентам мониторинга (warn/error → ok).

Запуск (из корня репозитория):
  python scripts/resolved_incidents_report.py
  python scripts/resolved_incidents_report.py --db "D:/path/monitoring.db" --since 2026-01-01
  python scripts/resolved_incidents_report.py --sources category --output data/reports/resolved.html
  python scripts/resolved_incidents_report.py --exclude "ConnectFail" --no-default-excludes

Переменные окружения:
  STATE_DB_PATH — путь к SQLite (monitoring.db)
  CONFIG_PATH   — путь к config.json
"""

from __future__ import annotations

import argparse
import html
import json
import os
import sqlite3
import statistics
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from episode_parser import (  # noqa: E402
    DEFAULT_PROBLEM_STATUSES,
    DEFAULT_TRANSPARENT_STATUSES,
    RECORDER_PROBLEM_STATUSES,
    ResolvedEpisode,
    count_active_episodes,
    episode_duration_hours,
    filter_episodes_by_resolved_at,
    parse_resolved_episodes,
    text_matches_any_pattern,
)

from app.display_time import format_for_display  # noqa: E402
from app.ui.health_classifiers import CATEGORY_LABELS  # noqa: E402
from event_type_groups import group_sort_key, normalize_event_group  # noqa: E402

# --- Настройки подключения (можно менять здесь или через env / CLI) ---

DEFAULT_DB_PATH = REPO_ROOT / "data" / "monitoring.db"
STATE_DB_PATH = Path(os.environ.get("STATE_DB_PATH", str(DEFAULT_DB_PATH)))
DEFAULT_CONFIG_PATH = Path(
    os.environ.get("CONFIG_PATH", str(REPO_ROOT / "config.json"))
)
DEFAULT_OUTPUT = REPO_ROOT / "data" / "reports" / "resolved_incidents_report.html"

# Типы событий, исключаемые из отчёта по умолчанию (подстрока, без учёта регистра)
DEFAULT_EXCLUDED_PATTERNS: tuple[str, ...] = (
    "AuthFail",
    "PoE",
)

SourceKind = Literal["category", "status"]

# Как часто выводить промежуточный прогресс при обходе потоков истории
PROGRESS_EVERY_STREAMS = 25


class ProgressReporter:
    """Подробный вывод этапов и прогресса в терминал."""

    def __init__(self, *, enabled: bool = True) -> None:
        self.enabled = enabled
        self._run_start = time.perf_counter()
        self._stage_start = self._run_start
        self._stage_name = ""
        self._completed_stages = 0
        self._stage_durations: list[float] = []

    def _ts(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def info(self, message: str, *, indent: int = 0) -> None:
        if not self.enabled:
            return
        prefix = "  " * indent
        print(f"[{self._ts()}] {prefix}{message}", flush=True)

    def stage_start(self, name: str, *, detail: str = "") -> None:
        self._stage_name = name
        self._stage_start = time.perf_counter()
        suffix = f" — {detail}" if detail else ""
        self.info(f">> {name}{suffix}")

    def stage_done(self, detail: str = "") -> float:
        elapsed = time.perf_counter() - self._stage_start
        self._stage_durations.append(elapsed)
        self._completed_stages += 1
        suffix = f": {detail}" if detail else ""
        self.info(f"OK {self._stage_name} завершён за {elapsed:.2f} с{suffix}")
        return elapsed

    def warn(self, message: str) -> None:
        if not self.enabled:
            return
        print(f"[{self._ts()}] ! {message}", file=sys.stderr, flush=True)

    def progress(
        self,
        current: int,
        total: int,
        *,
        label: str = "",
        every: int = PROGRESS_EVERY_STREAMS,
    ) -> None:
        if not self.enabled or total <= 0:
            return
        if current != total and (current % every != 0):
            return
        pct = current / total * 100
        elapsed = time.perf_counter() - self._stage_start
        eta_text = ""
        if 0 < current < total:
            eta_sec = elapsed / current * (total - current)
            eta_text = f", ~осталось {_format_eta(eta_sec)}"
        label_part = f"{label}: " if label else ""
        self.info(
            f".. {label_part}{current}/{total} ({pct:.0f}%){eta_text}",
            indent=1,
        )

    def run_summary(self, *, output_path: Path, incident_count: int, active_count: int) -> None:
        total_elapsed = time.perf_counter() - self._run_start
        self.info(
            f"Готово за {total_elapsed:.2f} с | отчёт: {output_path} | "
            f"инцидентов: {incident_count} · активных эпизодов: {active_count}"
        )


def _format_eta(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f} с"
    if seconds < 3600:
        return f"{seconds / 60:.1f} мин"
    return f"{seconds / 3600:.1f} ч"


def _format_bytes(size: int) -> str:
    if size < 1024:
        return f"{size} Б"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} КБ"
    return f"{size / (1024 * 1024):.1f} МБ"


@dataclass
class HistoryRow:
    status: str
    recorded_at: datetime
    reason: Optional[str]


@dataclass
class ResolvedIncident:
    source: SourceKind
    event_type: str
    device_id: str
    device_label: str
    severity_peak: str
    started_at: datetime
    resolved_at: datetime
    reason: Optional[str]

    @property
    def duration_hours(self) -> float:
        return episode_duration_hours(
            ResolvedEpisode(
                severity_peak=self.severity_peak,
                started_at=self.started_at,
                resolved_at=self.resolved_at,
                reason=self.reason,
            )
        )


def incident_excluded(inc: ResolvedIncident, patterns: list[str]) -> bool:
    blob = f"{inc.event_type} {inc.reason or ''}"
    return text_matches_any_pattern(blob, patterns)


def parse_exclude_patterns(
    cli_values: Optional[list[str]],
    *,
    use_defaults: bool,
) -> list[str]:
    patterns: list[str] = []
    if use_defaults:
        patterns.extend(DEFAULT_EXCLUDED_PATTERNS)
    if cli_values:
        for raw in cli_values:
            for part in raw.split(","):
                p = part.strip()
                if p and p not in patterns:
                    patterns.append(p)
    return patterns


def apply_incident_exclusions(
    incidents: list[ResolvedIncident],
    patterns: list[str],
) -> tuple[list[ResolvedIncident], int]:
    if not patterns:
        return incidents, 0
    kept: list[ResolvedIncident] = []
    excluded = 0
    for inc in incidents:
        if incident_excluded(inc, patterns):
            excluded += 1
        else:
            kept.append(inc)
    return kept, excluded


def serialize_incidents_for_js(incidents: list[ResolvedIncident]) -> list[dict]:
    rows: list[dict] = []
    for inc in incidents:
        source_label = "Категория" if inc.source == "category" else "Статус"
        event_group = normalize_event_group(inc.event_type)
        rows.append(
            {
                "eventType": inc.event_type,
                "eventGroup": event_group,
                "deviceLabel": inc.device_label,
                "source": source_label,
                "severity": inc.severity_peak,
                "startedAt": format_for_display(inc.started_at, "%d.%m.%Y %H:%M"),
                "resolvedAt": format_for_display(inc.resolved_at, "%d.%m.%Y %H:%M"),
                "durationHours": inc.duration_hours,
                "month": format_for_display(inc.resolved_at, "%Y-%m"),
            }
        )
    return rows


def build_group_catalog(incidents: list[ResolvedIncident]) -> list[dict]:
    counts: Counter[str] = Counter()
    for inc in incidents:
        counts[normalize_event_group(inc.event_type)] += 1
    items = [
        {"group": group, "count": count}
        for group, count in counts.items()
    ]
    items.sort(key=lambda x: (-x["count"], group_sort_key(x["group"])))
    return items


@dataclass
class SummaryRow:
    event_type: str
    device_label: str
    source: str
    count: int
    avg_duration_hours: float


@dataclass
class ReportContext:
    incidents: list[ResolvedIncident]
    summary_rows: list[SummaryRow]
    totals_by_type: Counter[str]
    totals_by_device: Counter[str]
    totals_by_severity: Counter[str]
    monthly_counts: list[tuple[str, int]]
    active_problems: int
    unique_devices: int
    avg_mttr_hours: Optional[float]
    median_mttr_hours: Optional[float]
    top_types: list[tuple[str, int]]
    top_devices: list[tuple[str, int]]
    chronic_types: list[tuple[str, int]]
    chronic_devices: list[tuple[str, int]]
    since: Optional[datetime]
    until: Optional[datetime]
    db_path: Path
    generated_at: datetime
    sources: list[str]


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _connect(db_path: Path, reporter: ProgressReporter) -> sqlite3.Connection:
    reporter.stage_start("Подключение к базе данных", detail=str(db_path.resolve()))
    if not db_path.is_file():
        raise FileNotFoundError(f"База не найдена: {db_path}")
    size = db_path.stat().st_size
    reporter.info(f"Размер файла БД: {_format_bytes(size)}", indent=1)
    t0 = time.perf_counter()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    elapsed = time.perf_counter() - t0
    reporter.info(f"Соединение установлено за {elapsed:.3f} с", indent=1)
    for required in ("category_status_history", "status_history"):
        if required in tables:
            reporter.info(f"Таблица {required}: найдена", indent=1)
        else:
            reporter.warn(f"Таблица {required} отсутствует — часть данных будет пропущена")
    reporter.stage_done(f"{len(tables)} таблиц в схеме")
    return conn


def load_recorder_names(config_path: Path, reporter: ProgressReporter) -> dict[str, str]:
    reporter.stage_start("Загрузка имён устройств", detail=str(config_path))
    if not config_path.is_file():
        reporter.warn(f"config.json не найден: {config_path}")
        reporter.stage_done("0 регистраторов (файл отсутствует)")
        return {}
    try:
        t0 = time.perf_counter()
        data = json.loads(config_path.read_text(encoding="utf-8"))
        out: dict[str, str] = {}
        for rec in data.get("recorders", []):
            rid = rec.get("id")
            if not rid:
                continue
            name = rec.get("name") or rec.get("host") or rid
            obj = rec.get("object_name") or ""
            out[rid] = f"{obj} / {name}" if obj else str(name)
        elapsed = time.perf_counter() - t0
        reporter.info(f"Прочитано имён регистраторов: {len(out)} за {elapsed:.3f} с", indent=1)
        reporter.stage_done(f"{len(out)} регистраторов")
        return out
    except Exception as exc:
        reporter.warn(f"Не удалось прочитать {config_path}: {exc}")
        reporter.stage_done("ошибка чтения")
        return {}


def _channel_names(conn: sqlite3.Connection, reporter: ProgressReporter) -> dict[tuple[str, int], str]:
    reporter.stage_start("Загрузка имён каналов", detail="таблица channels")
    try:
        t0 = time.perf_counter()
        rows = conn.execute(
            "SELECT recorder_id, channel_no, name FROM channels WHERE name IS NOT NULL"
        ).fetchall()
        elapsed = time.perf_counter() - t0
        result = {(r["recorder_id"], r["channel_no"]): r["name"] for r in rows}
        reporter.info(
            f"Получено имён каналов: {len(result)} из {len(rows)} строк за {elapsed:.3f} с",
            indent=1,
        )
        reporter.stage_done(f"{len(result)} каналов с именами")
        return result
    except sqlite3.Error as exc:
        reporter.warn(f"Не удалось прочитать channels: {exc}")
        reporter.stage_done("0 каналов")
        return {}


def _recorder_label(recorder_id: str, names: dict[str, str]) -> str:
    return names.get(recorder_id, recorder_id)


def _channel_label(
    entity_id: str,
    names: dict[str, str],
    channel_names: dict[tuple[str, int], str],
) -> tuple[str, str]:
    if ":" not in entity_id:
        return entity_id, _recorder_label(entity_id, names)
    recorder_id, ch_str = entity_id.rsplit(":", 1)
    try:
        channel_no = int(ch_str)
    except ValueError:
        return entity_id, entity_id
    base = _recorder_label(recorder_id, names)
    ch_name = channel_names.get((recorder_id, channel_no))
    if ch_name:
        return entity_id, f"{base} — канал {channel_no} ({ch_name})"
    return entity_id, f"{base} — канал {channel_no}"


def _fetch_category_streams(
    conn: sqlite3.Connection,
    reporter: ProgressReporter,
) -> dict[tuple[str, str], list[HistoryRow]]:
    reporter.stage_start("Получение данных", detail="category_status_history")
    t0 = time.perf_counter()
    rows = conn.execute(
        """
        SELECT recorder_id, category, status, reason, recorded_at
        FROM category_status_history
        ORDER BY recorder_id, category, recorded_at ASC
        """
    ).fetchall()
    fetch_elapsed = time.perf_counter() - t0
    reporter.info(
        f"SQL: {len(rows)} записей за {fetch_elapsed:.3f} с",
        indent=1,
    )

    reporter.stage_start("Группировка потоков", detail="category_status_history")
    streams: dict[tuple[str, str], list[HistoryRow]] = defaultdict(list)
    for idx, row in enumerate(rows, start=1):
        key = (row["recorder_id"], row["category"])
        streams[key].append(
            HistoryRow(
                status=row["status"],
                recorded_at=_parse_iso(row["recorded_at"])
                or datetime.now(timezone.utc),
                reason=row["reason"],
            )
        )
        if idx % 5000 == 0:
            reporter.info(f".. сгруппировано {idx}/{len(rows)} записей", indent=1)
    reporter.stage_done(f"{len(streams)} потоков из {len(rows)} записей")
    return streams


def _fetch_status_streams(
    conn: sqlite3.Connection,
    reporter: ProgressReporter,
) -> dict[tuple[str, str], list[HistoryRow]]:
    reporter.stage_start("Получение данных", detail="status_history")
    t0 = time.perf_counter()
    rows = conn.execute(
        """
        SELECT entity_type, entity_id, status, reason, recorded_at
        FROM status_history
        ORDER BY entity_type, entity_id, recorded_at ASC
        """
    ).fetchall()
    fetch_elapsed = time.perf_counter() - t0
    reporter.info(
        f"SQL: {len(rows)} записей за {fetch_elapsed:.3f} с",
        indent=1,
    )

    reporter.stage_start("Группировка потоков", detail="status_history")
    streams: dict[tuple[str, str], list[HistoryRow]] = defaultdict(list)
    for idx, row in enumerate(rows, start=1):
        key = (row["entity_type"], row["entity_id"])
        streams[key].append(
            HistoryRow(
                status=row["status"],
                recorded_at=_parse_iso(row["recorded_at"])
                or datetime.now(timezone.utc),
                reason=row["reason"],
            )
        )
        if idx % 5000 == 0:
            reporter.info(f".. сгруппировано {idx}/{len(rows)} записей", indent=1)
    reporter.stage_done(f"{len(streams)} потоков из {len(rows)} записей")
    return streams


def load_category_incidents(
    conn: sqlite3.Connection,
    names: dict[str, str],
    reporter: ProgressReporter,
    *,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
) -> tuple[list[ResolvedIncident], int]:
    streams = _fetch_category_streams(conn, reporter)
    reporter.stage_start(
        "Обработка данных",
        detail="поиск устранённых эпизодов в category_status_history",
    )
    incidents: list[ResolvedIncident] = []
    active = 0
    total = len(streams)
    for idx, ((recorder_id, category), rows) in enumerate(streams.items(), start=1):
        active += count_active_episodes(
            rows,
            problem_statuses=DEFAULT_PROBLEM_STATUSES,
            transparent_statuses=DEFAULT_TRANSPARENT_STATUSES,
        )
        label = CATEGORY_LABELS.get(category, category)  # type: ignore[arg-type]
        event_type = f"[Категория] {label}"
        device_label = _recorder_label(recorder_id, names)
        for ep in parse_resolved_episodes(rows):
            for filtered in filter_episodes_by_resolved_at([ep], since=since, until=until):
                incidents.append(
                    ResolvedIncident(
                        source="category",
                        event_type=event_type,
                        device_id=recorder_id,
                        device_label=device_label,
                        severity_peak=filtered.severity_peak,
                        started_at=filtered.started_at,
                        resolved_at=filtered.resolved_at,
                        reason=filtered.reason,
                    )
                )
        reporter.progress(idx, total, label="потоки категорий")
    reporter.stage_done(
        f"{len(incidents)} устранённых, {active} активных эпизодов"
    )
    return incidents, active


def load_status_incidents(
    conn: sqlite3.Connection,
    names: dict[str, str],
    channel_names: dict[tuple[str, int], str],
    reporter: ProgressReporter,
    *,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
) -> tuple[list[ResolvedIncident], int]:
    streams = _fetch_status_streams(conn, reporter)
    reporter.stage_start(
        "Обработка данных",
        detail="поиск устранённых эпизодов в status_history",
    )
    incidents: list[ResolvedIncident] = []
    active = 0
    total = len(streams)
    for idx, ((entity_type, entity_id), rows) in enumerate(streams.items(), start=1):
        problem_statuses = (
            RECORDER_PROBLEM_STATUSES
            if entity_type == "recorder"
            else DEFAULT_PROBLEM_STATUSES
        )
        active += count_active_episodes(
            rows,
            problem_statuses=problem_statuses,
            transparent_statuses=DEFAULT_TRANSPARENT_STATUSES,
        )
        if entity_type == "channel":
            device_id, device_label = _channel_label(entity_id, names, channel_names)
            prefix = "[Канал]"
        else:
            device_id = entity_id
            device_label = _recorder_label(entity_id, names)
            prefix = "[Регистратор]"
        for ep in parse_resolved_episodes(
            rows,
            problem_statuses=problem_statuses,
        ):
            reason_text = ep.reason or "Без указания причины"
            event_type = f"{prefix} {reason_text}"
            for filtered in filter_episodes_by_resolved_at([ep], since=since, until=until):
                incidents.append(
                    ResolvedIncident(
                        source="status",
                        event_type=event_type,
                        device_id=device_id,
                        device_label=device_label,
                        severity_peak=filtered.severity_peak,
                        started_at=filtered.started_at,
                        resolved_at=filtered.resolved_at,
                        reason=filtered.reason,
                    )
                )
        reporter.progress(idx, total, label="потоки статусов")
    reporter.stage_done(
        f"{len(incidents)} устранённых, {active} активных эпизодов"
    )
    return incidents, active


def build_summary_rows(incidents: list[ResolvedIncident]) -> list[SummaryRow]:
    groups: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for inc in incidents:
        source_label = "Категория" if inc.source == "category" else "Статус"
        groups[(normalize_event_group(inc.event_type), inc.device_label, source_label)].append(inc.duration_hours)
    rows: list[SummaryRow] = []
    for (event_type, device_label, source_label), durations in groups.items():
        rows.append(
            SummaryRow(
                event_type=event_type,
                device_label=device_label,
                source=source_label,
                count=len(durations),
                avg_duration_hours=sum(durations) / len(durations),
            )
        )
    rows.sort(key=lambda r: (-r.count, r.event_type, r.device_label))
    return rows


def build_report_context(
    incidents: list[ResolvedIncident],
    *,
    active_problems: int,
    since: Optional[datetime],
    until: Optional[datetime],
    db_path: Path,
    sources: list[str],
) -> ReportContext:
    summary_rows = build_summary_rows(incidents)
    totals_by_type: Counter[str] = Counter()
    totals_by_device: Counter[str] = Counter()
    totals_by_severity: Counter[str] = Counter()
    monthly: Counter[str] = Counter()
    durations: list[float] = []

    for inc in incidents:
        group = normalize_event_group(inc.event_type)
        totals_by_type[group] += 1
        totals_by_device[inc.device_label] += 1
        totals_by_severity[inc.severity_peak] += 1
        durations.append(inc.duration_hours)
        month_key = format_for_display(inc.resolved_at, "%Y-%m")
        monthly[month_key] += 1

    chronic_types = [(t, c) for t, c in totals_by_type.most_common() if c >= 2]
    chronic_devices = [(d, c) for d, c in totals_by_device.most_common() if c >= 2]

    avg_mttr = statistics.mean(durations) if durations else None
    median_mttr = statistics.median(durations) if durations else None

    return ReportContext(
        incidents=sorted(incidents, key=lambda i: i.resolved_at, reverse=True),
        summary_rows=summary_rows,
        totals_by_type=totals_by_type,
        totals_by_device=totals_by_device,
        totals_by_severity=totals_by_severity,
        monthly_counts=sorted(monthly.items()),
        active_problems=active_problems,
        unique_devices=len({i.device_label for i in incidents}),
        avg_mttr_hours=avg_mttr,
        median_mttr_hours=median_mttr,
        top_types=totals_by_type.most_common(10),
        top_devices=totals_by_device.most_common(10),
        chronic_types=chronic_types[:5],
        chronic_devices=chronic_devices[:5],
        since=since,
        until=until,
        db_path=db_path,
        generated_at=datetime.now(timezone.utc),
        sources=sources,
    )


def _format_duration_hours(hours: float) -> str:
    if hours < 1:
        return "менее 1 ч."
    if hours < 24:
        return f"{hours:.1f} ч."
    days = int(hours // 24)
    rem = int(hours % 24)
    if rem > 0:
        return f"{days} сут. {rem} ч."
    return f"{days} сут."


def _top_n_with_other(
    items: list[tuple[str, int]], top_n: int
) -> tuple[list[str], list[int]]:
    if not items:
        return [], []
    head = items[:top_n]
    tail = items[top_n:]
    labels = [x[0] for x in head]
    values = [x[1] for x in head]
    if tail:
        labels.append("Прочие")
        values.append(sum(v for _, v in tail))
    return labels, values


def _period_label(ctx: ReportContext) -> str:
    if ctx.since and ctx.until:
        return (
            f"{format_for_display(ctx.since, '%d.%m.%Y')} — "
            f"{format_for_display(ctx.until, '%d.%m.%Y')}"
        )
    if ctx.since:
        return f"с {format_for_display(ctx.since, '%d.%m.%Y')}"
    if ctx.until:
        return f"по {format_for_display(ctx.until, '%d.%m.%Y')}"
    return "за всё время наблюдения"


def build_effectiveness_text(ctx: ReportContext) -> str:
    total = len(ctx.incidents)
    if total == 0:
        return (
            "За выбранный период устранённых инцидентов не зафиксировано. "
            "Это может означать стабильную работу оборудования либо недостаточную "
            "глубину истории в базе данных."
        )

    parts: list[str] = []
    parts.append(
        f"За период {_period_label(ctx).lower()} система мониторинга зафиксировала "
        f"<strong>{total}</strong> устранённых эпизодов деградации или неисправности "
        f"на <strong>{ctx.unique_devices}</strong> устройствах."
    )

    if ctx.avg_mttr_hours is not None:
        parts.append(
            f"Среднее время устранения (MTTR): <strong>{_format_duration_hours(ctx.avg_mttr_hours)}</strong> "
            f"(медиана: {_format_duration_hours(ctx.median_mttr_hours or 0)})."
        )

    if ctx.top_types:
        t0, c0 = ctx.top_types[0]
        parts.append(
            f"Наиболее частый тип: <strong>{html.escape(t0)}</strong> ({c0} случ.)."
        )

    chronic_type_count = sum(1 for _, c in ctx.totals_by_type.items() if c >= 2)
    chronic_ratio = chronic_type_count / max(len(ctx.totals_by_type), 1) * 100
    parts.append(
        f"Повторяющиеся типы (≥2 инцидента): <strong>{chronic_type_count}</strong> "
        f"из {len(ctx.totals_by_type)} ({chronic_ratio:.0f}%) — "
        + (
            "есть признаки хронических проблем, требующих профилактики."
            if chronic_ratio >= 30
            else "большинство сбоев носят разовый характер."
        )
    )

    if ctx.active_problems > 0:
        parts.append(
            f"На момент отчёта ещё <strong>{ctx.active_problems}</strong> активных "
            f"эпизодов warn/error не завершены переходом в ok."
        )
    else:
        parts.append(
            "На момент отчёта активных незакрытых эпизодов в истории не обнаружено."
        )

    parts.append(
        "<em>Ограничения:</em> данные восстановлены из журналов смены статуса; "
        "одна физическая проблема может отражаться и в категории NVR, и в статусе канала. "
        "Глубина истории ограничена сроком работы мониторинга и не удаляется при очистке "
        "регистратора из конфигурации."
    )
    return " ".join(parts)


def _html_css() -> str:
    return """
<style>
:root {
  --bg: #ffffff; --card-bg: #f8fafc; --text: #1f2937; --muted: #6b7280;
  --primary: #0ea5e9; --success: #10b981; --warn: #f59e0b; --danger: #ef4444; --border: #e5e7eb;
}
html, body { background: var(--bg); color: var(--text); margin: 0;
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; }
.container { max-width: 1320px; margin: 0 auto; padding: 18px 18px 28px; }
h1 { font-size: 22px; margin: 12px 0 10px; }
h2 { font-size: 18px; margin: 18px 0 8px; }
.muted { color: var(--muted); font-size: 13px; }
.section { margin: 18px 0 26px; padding: 14px; background: #fff;
  border: 1px solid var(--border); border-radius: 12px; }
.section h2 { margin-top: 0; }
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 12px 0; }
.kpi-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 14px; }
.kpi-card .value { font-size: 26px; font-weight: 700; line-height: 1.2; }
.kpi-card .label { font-size: 12px; color: var(--muted); margin-top: 4px; }
.grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 14px; }
.chart-box { background: #fff; border: 1px dashed var(--border); border-radius: 8px; padding: 10px; min-height: 280px; }
table { border-collapse: collapse; width: 100%; }
th, td { padding: 8px 10px; border-bottom: 1px solid var(--border); font-size: 13px; }
th { text-align: left; background: #fafafa; }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
tr:hover { background: #f9fafb; }
.narrative { line-height: 1.55; font-size: 14px; }
.narrative p { margin: 0 0 10px; }
.collapsible { margin-top: 16px; }
.collapsible-trigger {
  display: flex; justify-content: space-between; align-items: center; cursor: pointer;
  padding: 10px 14px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px;
}
.collapsible-content { display: none; padding: 12px; border: 1px solid var(--border); border-top: none;
  border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; }
.collapsible.is-open .collapsible-content { display: block; }
.collapsible.is-open .collapsible-trigger { border-bottom-left-radius: 0; border-bottom-right-radius: 0; }
.footer { color: var(--muted); font-size: 12px; margin-top: 16px; }
.filter-panel { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 12px; }
.filter-tools { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 10px; }
.filter-tools input[type="text"] {
  padding: 6px 10px; border: 1px solid var(--border); border-radius: 8px; font-size: 13px; min-width: 220px;
}
.filter-tools button {
  padding: 6px 12px; border: 1px solid var(--border); border-radius: 8px; background: #fff;
  font-size: 13px; cursor: pointer;
}
.filter-tools button:hover { border-color: var(--primary); color: var(--primary); }
.type-filters {
  max-height: 360px; overflow: auto; padding: 4px 2px;
}
.filter-section { margin-bottom: 12px; }
.filter-section h3 { font-size: 14px; margin: 0 0 6px; color: var(--muted); }
.filter-section .type-filters {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 6px 12px;
  max-height: none; overflow: visible;
}
.type-filters label {
  display: flex; align-items: flex-start; gap: 8px; font-size: 13px; cursor: pointer;
}
.type-filters input { margin-top: 3px; }
.excluded-note { margin-top: 8px; font-size: 12px; color: var(--muted); }
</style>
"""


def _interactive_report_js() -> str:
    return r"""
const reportState = {
  charts: {},
  topN: 12,
};

function formatDurationHours(hours) {
  if (hours < 1) return 'менее 1 ч.';
  if (hours < 24) return hours.toFixed(1) + ' ч.';
  const days = Math.floor(hours / 24);
  const rem = Math.floor(hours % 24);
  if (rem > 0) return days + ' сут. ' + rem + ' ч.';
  return days + ' сут.';
}

function selectedGroups() {
  return new Set(
    Array.from(document.querySelectorAll('.group-filter-cb:checked')).map(el => el.value)
  );
}

function visibleIncidents() {
  const allowed = selectedGroups();
  if (allowed.size === 0) return [];
  return reportData.incidents.filter(row => allowed.has(row.eventGroup));
}

function aggregateSummary(rows) {
  const map = new Map();
  for (const row of rows) {
    const key = row.eventGroup + '\0' + row.deviceLabel + '\0' + row.source;
    if (!map.has(key)) {
      map.set(key, { eventGroup: row.eventGroup, deviceLabel: row.deviceLabel, source: row.source, durations: [] });
    }
    map.get(key).durations.push(row.durationHours);
  }
  return Array.from(map.values()).map(item => ({
    eventGroup: item.eventGroup,
    deviceLabel: item.deviceLabel,
    source: item.source,
    count: item.durations.length,
    avgHours: item.durations.reduce((a, b) => a + b, 0) / item.durations.length,
  })).sort((a, b) => b.count - a.count || a.eventGroup.localeCompare(b.eventGroup));
}

function topNWithOther(items, n) {
  if (!items.length) return { labels: [], values: [] };
  const head = items.slice(0, n);
  const tail = items.slice(n);
  const labels = head.map(x => x.label);
  const values = head.map(x => x.value);
  if (tail.length) {
    labels.push('Прочие');
    values.push(tail.reduce((s, x) => s + x.value, 0));
  }
  return { labels, values };
}

function destroyCharts() {
  Object.values(reportState.charts).forEach(ch => { try { ch.destroy(); } catch (e) {} });
  reportState.charts = {};
}

function renderCharts(rows) {
  if (!window.Chart || document.getElementById('chartTypes') == null) return;
  destroyCharts();
  const byType = new Map();
  const byDevice = new Map();
  const bySeverity = new Map();
  const byMonth = new Map();
  for (const row of rows) {
    byType.set(row.eventGroup, (byType.get(row.eventGroup) || 0) + 1);
    byDevice.set(row.deviceLabel, (byDevice.get(row.deviceLabel) || 0) + 1);
    bySeverity.set(row.severity, (bySeverity.get(row.severity) || 0) + 1);
    byMonth.set(row.month, (byMonth.get(row.month) || 0) + 1);
  }
  const typeItems = Array.from(byType.entries()).map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value);
  const deviceItems = Array.from(byDevice.entries()).map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value);
  const types = topNWithOther(typeItems, reportState.topN);
  const devices = topNWithOther(deviceItems, reportState.topN);
  function horizBar(id, title, labels, values, color) {
    const el = document.getElementById(id);
    if (!el) return;
    reportState.charts[id] = new Chart(el, {
      type: 'bar',
      data: { labels, datasets: [{ label: title, data: values, backgroundColor: color }] },
      options: {
        indexAxis: 'y', responsive: true,
        plugins: { legend: { display: false }, title: { display: true, text: title } },
        scales: { x: { beginAtZero: true, ticks: { precision: 0 } } },
      },
    });
  }
  horizBar('chartTypes', 'По группам событий', types.labels, types.values, '#0ea5e9');
  horizBar('chartDevices', 'По устройствам', devices.labels, devices.values, '#10b981');
  const sevEl = document.getElementById('chartSeverity');
  if (sevEl) {
    const sevLabels = Array.from(bySeverity.keys());
    const sevValues = sevLabels.map(k => bySeverity.get(k));
    reportState.charts.chartSeverity = new Chart(sevEl, {
      type: 'doughnut',
      data: {
        labels: sevLabels,
        datasets: [{ data: sevValues, backgroundColor: ['#f59e0b', '#ef4444', '#6b7280', '#0ea5e9'] }],
      },
      options: { responsive: true, plugins: { title: { display: true, text: 'По тяжести (peak)' } } },
    });
  }
  const monthBox = document.getElementById('monthlyChartBox');
  const monthEl = document.getElementById('chartMonthly');
  const monthLabels = Array.from(byMonth.keys()).sort();
  if (monthBox && monthEl && monthLabels.length > 1) {
    monthBox.style.display = '';
    const monthValues = monthLabels.map(m => byMonth.get(m));
    reportState.charts.chartMonthly = new Chart(monthEl, {
      type: 'line',
      data: {
        labels: monthLabels,
        datasets: [{ label: 'Устранено', data: monthValues, borderColor: '#0ea5e9', tension: 0.2, fill: false }],
      },
      options: {
        responsive: true,
        plugins: { title: { display: true, text: 'Устранения по месяцам' } },
        scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
      },
    });
  } else if (monthBox) {
    monthBox.innerHTML = '<p class="muted" style="padding:20px">Недостаточно данных для помесячного графика</p>';
  }
}

function updateKpis(rows) {
  const totalEl = document.getElementById('kpiTotal');
  const mttrEl = document.getElementById('kpiMttr');
  const devEl = document.getElementById('kpiDevices');
  const detailTitle = document.getElementById('detailCount');
  if (!totalEl) return;
  totalEl.textContent = String(rows.length);
  if (detailTitle) detailTitle.textContent = String(rows.length);
  if (rows.length === 0) {
    mttrEl.textContent = '—';
    devEl.textContent = '0';
    return;
  }
  const durations = rows.map(r => r.durationHours);
  const avg = durations.reduce((a, b) => a + b, 0) / durations.length;
  mttrEl.textContent = formatDurationHours(avg);
  devEl.textContent = String(new Set(rows.map(r => r.deviceLabel)).size);
}

function updateSummaryTable(rows) {
  const tbody = document.getElementById('summaryBody');
  if (!tbody) return;
  const summary = aggregateSummary(rows);
  if (!summary.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="muted">Нет данных для выбранных групп</td></tr>';
    return;
  }
  tbody.innerHTML = summary.map(row => (
    '<tr>'
    + '<td>' + escapeHtml(row.eventGroup) + '</td>'
    + '<td>' + escapeHtml(row.deviceLabel) + '</td>'
    + '<td>' + escapeHtml(row.source) + '</td>'
    + '<td class="num">' + row.count + '</td>'
    + '<td class="num">' + formatDurationHours(row.avgHours) + '</td>'
    + '</tr>'
  )).join('');
}

function updateDetailTable(rows) {
  const tbody = document.getElementById('detailBody');
  if (!tbody) return;
  const sorted = rows.slice().sort((a, b) => b.resolvedAt.localeCompare(a.resolvedAt));
  if (!sorted.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="muted">Нет данных для выбранных групп</td></tr>';
    return;
  }
  tbody.innerHTML = sorted.map(row => (
    '<tr>'
    + '<td title="' + escapeHtml(row.eventType) + '">' + escapeHtml(row.eventGroup) + '</td>'
    + '<td>' + escapeHtml(row.deviceLabel) + '</td>'
    + '<td>' + escapeHtml(row.severity) + '</td>'
    + '<td>' + escapeHtml(row.startedAt) + '</td>'
    + '<td>' + escapeHtml(row.resolvedAt) + '</td>'
    + '<td class="num">' + formatDurationHours(row.durationHours) + '</td>'
    + '</tr>'
  )).join('');
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function refreshReport() {
  const rows = visibleIncidents();
  updateKpis(rows);
  updateSummaryTable(rows);
  updateDetailTable(rows);
  renderCharts(rows);
  const status = document.getElementById('filterStatus');
  if (status) {
    const catalog = reportData.groupCatalog || [];
    const selected = selectedGroups().size;
    status.textContent = 'Показано ' + rows.length + ' из ' + reportData.incidents.length
      + ' эпизодов · выбрано групп: ' + selected + ' / ' + catalog.length;
  }
}

function sectionForGroup(group) {
  if (group.startsWith('[Канал]')) return 'Каналы';
  if (group.startsWith('[Категория]')) return 'Категории NVR';
  if (group.startsWith('[Регистратор]')) return 'Регистраторы';
  return 'Прочее';
}

function initTypeFilters() {
  const container = document.getElementById('typeFilters');
  if (!container) return;
  const catalog = reportData.groupCatalog || [];
  const bySection = new Map();
  for (const item of catalog) {
    const section = sectionForGroup(item.group);
    if (!bySection.has(section)) bySection.set(section, []);
    bySection.get(section).push(item);
  }
  const sectionOrder = ['Каналы', 'Категории NVR', 'Регистраторы', 'Прочее'];
  let html = '';
  for (const section of sectionOrder) {
    const items = bySection.get(section);
    if (!items || !items.length) continue;
    html += '<div class="filter-section"><h3>' + escapeHtml(section) + '</h3><div class="type-filters">';
    for (const item of items) {
      html += '<label data-group="' + escapeHtml(item.group) + '">'
        + '<input type="checkbox" class="group-filter-cb" value="' + escapeHtml(item.group) + '" checked>'
        + '<span>' + escapeHtml(item.group) + ' <span class="muted">(' + item.count + ')</span></span></label>';
    }
    html += '</div></div>';
  }
  container.innerHTML = html;
  container.querySelectorAll('.group-filter-cb').forEach(cb => {
    cb.addEventListener('change', refreshReport);
  });
}

function filterTypeList(query) {
  const q = query.trim().toLowerCase();
  document.querySelectorAll('#typeFilters label[data-group]').forEach(label => {
    const text = label.getAttribute('data-group') || '';
    label.style.display = !q || text.toLowerCase().includes(q) ? '' : 'none';
  });
}

function setAllTypes(checked) {
  document.querySelectorAll('.group-filter-cb').forEach(cb => { cb.checked = checked; });
  refreshReport();
}

document.addEventListener('DOMContentLoaded', () => {
  reportState.topN = reportData.meta.topN || 12;
  initTypeFilters();
  const search = document.getElementById('typeSearch');
  if (search) search.addEventListener('input', () => filterTypeList(search.value));
  const btnAll = document.getElementById('btnSelectAll');
  const btnNone = document.getElementById('btnSelectNone');
  if (btnAll) btnAll.addEventListener('click', () => setAllTypes(true));
  if (btnNone) btnNone.addEventListener('click', () => setAllTypes(false));
  document.querySelectorAll('.collapsible-trigger').forEach(trigger => {
    trigger.addEventListener('click', () => trigger.closest('.collapsible')?.classList.toggle('is-open'));
  });
  refreshReport();
});
"""


def render_html_report(
    ctx: ReportContext,
    *,
    top_n: int = 12,
    static_charts: bool = False,
    excluded_patterns: Optional[list[str]] = None,
    excluded_count: int = 0,
) -> str:
    sources_text = ", ".join(ctx.sources)
    excluded_patterns = excluded_patterns or []
    report_payload = {
        "incidents": serialize_incidents_for_js(ctx.incidents),
        "groupCatalog": build_group_catalog(ctx.incidents),
        "meta": {
            "topN": top_n,
            "activeProblems": ctx.active_problems,
            "excludedPatterns": excluded_patterns,
            "excludedCount": excluded_count,
        },
    }
    payload_json = json.dumps(report_payload, ensure_ascii=False)

    excluded_note = ""
    if excluded_patterns:
        patterns_text = html.escape(", ".join(excluded_patterns))
        excluded_note = (
            f'<p class="excluded-note">Исключено при формировании отчёта: '
            f"<strong>{excluded_count}</strong> эпизодов по шаблонам: {patterns_text}</p>"
        )

    static_charts_block = ""
    if static_charts:
        try:
            static_charts_block = _render_static_charts(ctx, top_n=top_n)
            static_charts_block += (
                '<p class="muted">Статические графики отражают все данные отчёта; '
                "таблицы и KPI обновляются по фильтру типов.</p>"
            )
        except Exception as exc:
            static_charts_block = (
                f"<p class='muted'>Статические графики недоступны: {html.escape(str(exc))}</p>"
            )

    chart_section = static_charts_block or """
<div class="grid-2">
  <div class="chart-box"><canvas id="chartTypes"></canvas></div>
  <div class="chart-box"><canvas id="chartDevices"></canvas></div>
  <div class="chart-box"><canvas id="chartSeverity"></canvas></div>
  <div class="chart-box" id="monthlyChartBox"><canvas id="chartMonthly"></canvas></div>
</div>
"""

    chart_js = ""
    if not static_charts:
        chart_js = """
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
"""

    return f"""<!doctype html>
<html lang="ru"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Устранённые инциденты мониторинга</title>
{_html_css()}
</head><body>
<div class="container">
<h1>Отчёт по устранённым инцидентам мониторинга</h1>
<p class="muted">Период: {_period_label(ctx)} · Источники: {html.escape(sources_text)} ·
  БД: {html.escape(str(ctx.db_path))} · Сформирован:
  {format_for_display(ctx.generated_at, '%d.%m.%Y %H:%M')}</p>
{excluded_note}

<div class="section">
  <h2>Фильтр групп событий</h2>
  <p class="muted">Похожие причины сведены в группы (без точных секунд и диапазонов архива). Детальная таблица показывает полный текст при наведении на группу.</p>
  <div class="filter-panel">
    <div class="filter-tools">
      <input type="text" id="typeSearch" placeholder="Поиск группы..."/>
      <button type="button" id="btnSelectAll">Выбрать все</button>
      <button type="button" id="btnSelectNone">Снять все</button>
    </div>
    <div class="type-filters" id="typeFilters"></div>
    <p class="excluded-note" id="filterStatus"></p>
  </div>
</div>

<div class="kpi-grid">
  <div class="kpi-card"><div class="value" id="kpiTotal">0</div><div class="label">Устранено инцидентов</div></div>
  <div class="kpi-card"><div class="value" id="kpiMttr">—</div><div class="label">Средний MTTR</div></div>
  <div class="kpi-card"><div class="value">{ctx.active_problems}</div><div class="label">Активных эпизодов сейчас</div></div>
  <div class="kpi-card"><div class="value" id="kpiDevices">0</div><div class="label">Уникальных устройств</div></div>
</div>

<div class="section narrative">
  <h2>Эффективность мониторинга</h2>
  <p>{build_effectiveness_text(ctx)}</p>
  <p class="muted">Используйте фильтр групп выше — таблицы и графики обновляются без перезагрузки страницы.</p>
</div>

<div class="section">
  <h2>Визуализация</h2>
  {chart_section}
</div>

<div class="section">
  <h2>Сводка: тип × устройство</h2>
  <table>
    <thead><tr>
      <th>Группа события</th><th>Устройство</th><th>Источник</th>
      <th>Кол-во</th><th>Ср. длительность</th>
    </tr></thead>
    <tbody id="summaryBody"><tr><td colspan="5" class="muted">Загрузка...</td></tr></tbody>
  </table>
</div>

<div class="section collapsible">
  <div class="collapsible-trigger">
    <h2>Детальный список эпизодов (<span id="detailCount">0</span>)</h2>
    <span>+</span>
  </div>
  <div class="collapsible-content">
    <table>
      <thead><tr>
        <th>Группа</th><th>Устройство</th><th>Тяжесть</th>
        <th>Начало</th><th>Устранено</th><th>Длительность</th>
      </tr></thead>
      <tbody id="detailBody"><tr><td colspan="6" class="muted">Загрузка...</td></tr></tbody>
    </table>
  </div>
</div>

<p class="footer">Wisenet Диагностика · отчёт сгенерирован автоматически из monitoring.db</p>
</div>
<script>const reportData = {payload_json};</script>
{chart_js}
<script>{_interactive_report_js()}</script>
</body></html>
"""


def _render_static_charts(ctx: ReportContext, *, top_n: int) -> str:
    import base64
    from io import BytesIO

    import matplotlib.pyplot as plt

    type_labels, type_values = _top_n_with_other(ctx.top_types, top_n)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].barh(type_labels[::-1], type_values[::-1], color="#0ea5e9")
    axes[0].set_title("По типам событий")
    dev_labels, dev_values = _top_n_with_other(ctx.top_devices, top_n)
    axes[1].barh(dev_labels[::-1], dev_values[::-1], color="#10b981")
    axes[1].set_title("По устройствам")
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    return f'<div class="chart-box"><img src="{uri}" alt="charts" style="max-width:100%"/></div>'


def parse_sources_arg(raw: str) -> list[str]:
    value = raw.strip().lower()
    if value in ("all", ""):
        return ["category", "status"]
    parts = [p.strip() for p in value.split(",") if p.strip()]
    valid = {"category", "status"}
    unknown = set(parts) - valid
    if unknown:
        raise ValueError(f"Неизвестные источники: {', '.join(sorted(unknown))}")
    return parts or ["category", "status"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="HTML-отчёт по устранённым инцидентам мониторинга"
    )
    parser.add_argument("--db", type=Path, default=STATE_DB_PATH, help="Путь к monitoring.db")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="config.json")
    parser.add_argument("--since", help="Начало периода (ISO), фильтр по дате устранения")
    parser.add_argument("--until", help="Конец периода (ISO), фильтр по дате устранения")
    parser.add_argument(
        "--sources",
        default="all",
        help="Источники: all | category | status | category,status",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Путь к HTML-файлу")
    parser.add_argument("--top-n", type=int, default=12, help="Топ N на графиках")
    parser.add_argument(
        "--static-charts",
        action="store_true",
        help="Встроить PNG-графики (matplotlib) вместо Chart.js",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Минимальный вывод (только итоговая строка)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help="Доп. шаблон исключения (подстрока в типе/причине); можно указать несколько раз",
    )
    parser.add_argument(
        "--no-default-excludes",
        action="store_true",
        help="Не исключать AuthFail и PoE выключен на канале по умолчанию",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    reporter = ProgressReporter(enabled=not args.quiet)
    reporter.info("Запуск формирования отчёта по устранённым инцидентам")

    since = _parse_iso(args.since) if args.since else None
    until = _parse_iso(args.until) if args.until else None

    try:
        sources = parse_sources_arg(args.sources)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    period_parts: list[str] = []
    if since:
        period_parts.append(f"с {format_for_display(since, '%d.%m.%Y')}")
    if until:
        period_parts.append(f"по {format_for_display(until, '%d.%m.%Y')}")
    period_text = ", ".join(period_parts) if period_parts else "за всё время"
    reporter.info(
        f"Параметры: БД={args.db.resolve()}, источники={','.join(sources)}, "
        f"период={period_text}, выход={args.output.resolve()}"
    )

    try:
        conn = _connect(args.db, reporter)
    except (FileNotFoundError, RuntimeError) as exc:
        reporter.warn(str(exc))
        return 1

    names = load_recorder_names(args.config, reporter)
    channel_names = _channel_names(conn, reporter)

    incidents: list[ResolvedIncident] = []
    active_total = 0

    if "category" in sources:
        cat_inc, cat_active = load_category_incidents(
            conn, names, reporter, since=since, until=until
        )
        incidents.extend(cat_inc)
        active_total += cat_active

    if "status" in sources:
        st_inc, st_active = load_status_incidents(
            conn, names, channel_names, reporter, since=since, until=until
        )
        incidents.extend(st_inc)
        active_total += st_active

    conn.close()
    reporter.info("Соединение с базой данных закрыто", indent=1)

    exclude_patterns = parse_exclude_patterns(
        args.exclude,
        use_defaults=not args.no_default_excludes,
    )
    if exclude_patterns:
        reporter.stage_start(
            "Фильтрация исключённых типов",
            detail=", ".join(exclude_patterns),
        )
        incidents, excluded_count = apply_incident_exclusions(incidents, exclude_patterns)
        reporter.stage_done(
            f"в отчёт: {len(incidents)}, исключено: {excluded_count}"
        )
    else:
        excluded_count = 0

    reporter.stage_start("Агрегация и расчёт показателей")
    ctx = build_report_context(
        incidents,
        active_problems=active_total,
        since=since,
        until=until,
        db_path=args.db.resolve(),
        sources=sources,
    )
    reporter.stage_done(
        f"{len(ctx.summary_rows)} строк сводки, {len(ctx.incidents)} эпизодов"
    )

    reporter.stage_start(
        "Генерация HTML",
        detail="Chart.js" if not args.static_charts else "matplotlib PNG",
    )
    html_content = render_html_report(
        ctx,
        top_n=args.top_n,
        static_charts=args.static_charts,
        excluded_patterns=exclude_patterns,
        excluded_count=excluded_count,
    )
    reporter.stage_done(f"{len(html_content):,} символов".replace(",", " "))

    reporter.stage_start("Запись файла", detail=str(args.output))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html_content, encoding="utf-8")
    out_size = args.output.stat().st_size
    reporter.stage_done(_format_bytes(out_size))

    reporter.run_summary(
        output_path=args.output.resolve(),
        incident_count=len(incidents),
        active_count=active_total,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
