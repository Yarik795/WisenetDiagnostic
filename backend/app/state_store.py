from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "monitoring.db"


@dataclass
class ChannelRow:
    id: int
    recorder_id: str
    channel_no: int
    name: Optional[str]
    camera_ip: Optional[str]
    camera_model: Optional[str]
    source_state: Optional[str]
    health_status: str
    health_reason: Optional[str]
    video_loss: Optional[bool]
    last_polled_at: Optional[datetime]
    archive_start: Optional[str] = None
    archive_end: Optional[str] = None
    archive_days: Optional[float] = None
    data_rate: Optional[float] = None
    cpu_usage: Optional[float] = None
    poe_status: Optional[bool] = None


@dataclass
class RecorderMetricsRow:
    recorder_id: str
    model: Optional[str]
    firmware_version: Optional[str]
    device_online: bool
    health_status: str
    health_reason: Optional[str]
    ntp_status: Optional[str]
    time_skew_seconds: Optional[float]
    storage_used_percent: Optional[float]
    storage_status: Optional[str]
    archive_start: Optional[str]
    archive_end: Optional[str]
    archive_days: Optional[float]
    channel_count: int
    channels_ok: int
    channels_warn: int
    channels_error: int
    channels_unknown: int
    last_polled_at: Optional[datetime]
    local_time: Optional[str] = None
    utc_time: Optional[str] = None
    sync_type: Optional[str] = None
    storage_used_mb: Optional[float] = None
    storage_total_mb: Optional[float] = None
    disks_json: Optional[str] = None
    system_events_json: Optional[str] = None
    system_event_times_json: Optional[str] = None
    archive_min_days: Optional[float] = None
    archive_max_days: Optional[float] = None
    storageinfo_ok: bool = False
    archive_poll_error: Optional[str] = None
    recording_storage_enable: Optional[bool] = None
    recording_storage_overwrite: Optional[bool] = None
    cpu_usage_max: Optional[float] = None
    cpu_usage_avg: Optional[float] = None
    data_rate_total_mbps: Optional[float] = None
    channels_zero_bitrate: Optional[int] = None
    channels_poe_off: Optional[int] = None
    serial_number: Optional[str] = None
    manufacture_date: Optional[str] = None
    last_poll_job_id: Optional[str] = None
    last_poll_attempts: Optional[int] = None
    last_poll_success_attempt: Optional[int] = None
    last_poll_first_try_ok: Optional[bool] = None


@dataclass
class RecorderPollAttemptRow:
    id: int
    job_id: str
    recorder_id: str
    attempt: int
    outcome: str
    online: bool
    error: Optional[str]
    duration_ms: Optional[int]
    recorded_at: datetime


@dataclass
class HistoryRow:
    id: int
    entity_type: str
    entity_id: str
    status: str
    reason: Optional[str]
    recorded_at: datetime


@dataclass
class CategoryStatusHistoryRow:
    id: int
    recorder_id: str
    category: str
    status: str
    reason: Optional[str]
    recorded_at: datetime


@dataclass
class SourceImportRow:
    id: int
    source_key: str
    filename: Optional[str]
    imported_at: datetime
    record_count: int
    status: str
    message: Optional[str]


@dataclass(frozen=True)
class NaumenRecordRow:
    external_id: str
    number: str
    cost: float
    sberdrug_number: str
    description: str
    source_row: int


@dataclass(frozen=True)
class PPRequestRow:
    request_number: str
    status: str
    drug_number: str
    created_at: Optional[str]
    completed_at: Optional[str]
    customer_fio: str
    tb: str
    work_type: str
    act_status: str
    amount_vat: float
    warranty: str
    address: str
    security_system_type: str
    in_limit: str
    raw_json: str
    source_row: int


@dataclass(frozen=True)
class ArsenalAnalyticsRow:
    passport_number: str
    tb: str
    gosb: str
    status: str
    object_type: str
    subtype: str
    object_name: str
    address: str
    fill_total: float
    fill_sections: dict[str, float]
    errors_total: int
    errors_sections: dict[str, int]
    fill_project_docs: float
    docs: dict[str, str]
    has_photos: str
    source_row: int


@dataclass(frozen=True)
class ArsenalSystemRow:
    passport_number: str
    tb: str
    gosb: str
    object_type: str
    subtype: str
    system_type: str
    manufacturer: str
    year: Optional[int]
    present: bool
    source_row: int


@dataclass
class ArsenalAnalyticsDbRow:
    passport_number: str
    tb: str
    gosb: str
    status: str
    object_type: str
    subtype: str
    object_name: str
    address: str
    fill_total: float
    fill_sections_json: str
    errors_total: int
    errors_sections_json: str
    fill_project_docs: float
    docs_json: str
    has_photos: str
    imported_at: datetime


@dataclass
class ArsenalSystemDbRow:
    id: int
    passport_number: str
    tb: str
    gosb: str
    object_type: str
    subtype: str
    system_type: str
    manufacturer: str
    year: Optional[int]
    present: bool
    imported_at: datetime


class NaumenReplaceSession:
    def __init__(self, conn: sqlite3.Connection, imported_at: str) -> None:
        self._conn = conn
        self._imported_at = imported_at
        self.count = 0

    def write_batch(self, rows: list[Any]) -> None:
        if not rows:
            return
        conn = self._conn
        imported_at = self._imported_at
        conn.executemany(
            """
            INSERT INTO naumen_records (
                external_id, number, cost, sberdrug_number,
                description, source_row, imported_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row.external_id,
                    row.number,
                    row.cost,
                    row.sberdrug_number,
                    row.description,
                    row.source_row,
                    imported_at,
                )
                for row in rows
            ],
        )
        self.count += len(rows)


class PPReplaceSession:
    def __init__(self, conn: sqlite3.Connection, imported_at: str) -> None:
        self._conn = conn
        self._imported_at = imported_at
        self.count = 0

    def write_batch(self, rows: list[Any]) -> None:
        if not rows:
            return
        conn = self._conn
        imported_at = self._imported_at
        conn.executemany(
            """
            INSERT OR REPLACE INTO pp_requests (
                request_number, status, drug_number, created_at, completed_at,
                customer_fio, tb, work_type, act_status, amount_vat, warranty,
                address, security_system_type, in_limit, raw_json, source_row,
                imported_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row.request_number,
                    row.status,
                    row.drug_number,
                    row.created_at,
                    row.completed_at,
                    row.customer_fio,
                    row.tb,
                    row.work_type,
                    row.act_status,
                    row.amount_vat,
                    row.warranty,
                    row.address,
                    row.security_system_type,
                    row.in_limit,
                    row.raw_json,
                    row.source_row,
                    imported_at,
                )
                for row in rows
            ],
        )
        self.count += len(rows)


class ArsenalReplaceSession:
    def __init__(self, conn: sqlite3.Connection, imported_at: str) -> None:
        self._conn = conn
        self._imported_at = imported_at
        self.analytics_count = 0
        self.systems_count = 0

    def write_analytics_batch(self, rows: list[Any]) -> None:
        if not rows:
            return
        conn = self._conn
        imported_at = self._imported_at
        conn.executemany(
            """
            INSERT INTO arsenal_analytics (
                passport_number, tb, gosb, status, object_type, subtype,
                object_name, address, fill_total, fill_sections_json, errors_total,
                errors_sections_json, fill_project_docs, docs_json, has_photos,
                source_row, imported_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row.passport_number,
                    row.tb,
                    row.gosb,
                    row.status,
                    row.object_type,
                    row.subtype,
                    row.object_name,
                    row.address,
                    row.fill_total,
                    json.dumps(row.fill_sections, ensure_ascii=False),
                    row.errors_total,
                    json.dumps(row.errors_sections, ensure_ascii=False),
                    row.fill_project_docs,
                    json.dumps(row.docs, ensure_ascii=False),
                    row.has_photos,
                    row.source_row,
                    imported_at,
                )
                for row in rows
            ],
        )
        self.analytics_count += len(rows)

    def write_systems_batch(self, rows: list[Any]) -> None:
        if not rows:
            return
        conn = self._conn
        imported_at = self._imported_at
        conn.executemany(
            """
            INSERT INTO arsenal_systems (
                passport_number, tb, gosb, object_type, subtype,
                system_type, manufacturer, year, present, source_row, imported_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row.passport_number,
                    row.tb,
                    row.gosb,
                    row.object_type,
                    row.subtype,
                    row.system_type,
                    row.manufacturer,
                    row.year,
                    1 if row.present else 0,
                    row.source_row,
                    imported_at,
                )
                for row in rows
            ],
        )
        self.systems_count += len(rows)


_CATEGORY_PROBLEM_STATUSES = frozenset({"warn", "error"})
_RECORDER_PROBLEM_STATUSES = frozenset({"warn", "error", "offline"})
# unknown между warn/error не завершает эпизод (пропуск опроса, нет метрик).
_TRANSPARENT_GAP_STATUSES = frozenset({"unknown"})


class StateStore:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or Path(os.environ.get("STATE_DB_PATH", DEFAULT_DB_PATH))

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                -- channels: текущее (последнее известное) состояние каждого
                -- видеоканала на каждом регистраторе. Одна строка = один канал.
                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,    -- суррогатный PK (автоинкремент)
                    recorder_id TEXT NOT NULL,               -- ID регистратора из config.json (recorders[].id)
                    channel_no INTEGER NOT NULL,             -- номер канала на NVR (0-based, как в SUNAPI)
                    name TEXT,                               -- отображаемое имя канала (ChannelInfo.name)
                    camera_ip TEXT,                          -- IP сетевой камеры канала (NULL для аналоговых/пустых)
                    camera_model TEXT,                       -- модель камеры из атрибутов канала
                    source_state TEXT,                       -- состояние источника с NVR: On/Off/Deactive/Covert1/Covert2 (как от API)
                    health_status TEXT NOT NULL DEFAULT 'unknown',  -- агрегированный статус канала: ok/warn/error/unknown
                    health_reason TEXT,                      -- человекочитаемое объяснение статуса (рус. текст из evaluate_channel_health)
                    video_loss INTEGER,                      -- 1=VideoLoss активен, 0=нет, NULL=событие не опрашивалось
                    last_polled_at TEXT,                     -- время последнего обновления строки (ISO 8601, UTC)
                    UNIQUE(recorder_id, channel_no)          -- один канал — одна строка; основа UPSERT
                );

                -- recorder_metrics: снимок последнего полного опроса каждого NVR.
                -- Ровно одна строка на регистратор (PK = recorder_id).
                CREATE TABLE IF NOT EXISTS recorder_metrics (
                    recorder_id TEXT PRIMARY KEY,            -- ID регистратора из config.json
                    model TEXT,                              -- модель устройства (DeviceInfo.model)
                    firmware_version TEXT,                   -- версия прошивки NVR
                    device_online INTEGER NOT NULL DEFAULT 0,  -- 1, если SUNAPI ответил в последнем опросе
                    health_status TEXT NOT NULL DEFAULT 'unknown',  -- сводный статус NVR: ok/warn/error/unknown
                    health_reason TEXT,                      -- причины статуса через "; " (evaluate_recorder_health)
                    ntp_status TEXT,                         -- статус NTP с устройства: Success/Fail/...
                    time_skew_seconds REAL,                  -- расхождение времени NVR и сервера приложения, сек
                    storage_used_percent REAL,               -- заполненность хранилища, %
                    storage_status TEXT,                     -- худший статус дисков агрегатом (Normal/error/...)
                    archive_start TEXT,                      -- начало глобального периода записи (если API вернул общий период)
                    archive_end TEXT,                        -- конец глобального периода записи
                    archive_days REAL,                       -- глубина архива в сутках (часто max по каналам / глобальное значение)
                    channel_count INTEGER NOT NULL DEFAULT 0,    -- всего учтённых каналов
                    channels_ok INTEGER NOT NULL DEFAULT 0,      -- каналов со статусом ok
                    channels_warn INTEGER NOT NULL DEFAULT 0,    -- каналов со статусом warn
                    channels_error INTEGER NOT NULL DEFAULT 0,   -- каналов со статусом error
                    channels_unknown INTEGER NOT NULL DEFAULT 0, -- каналов со статусом unknown
                    last_polled_at TEXT                      -- время последнего опроса метрик (ISO 8601, UTC)
                );

                -- status_history: журнал смены агрегированного health_status
                -- сущностей (канал/регистратор). Запись добавляется только при смене статуса.
                CREATE TABLE IF NOT EXISTS status_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,    -- PK (автоинкремент)
                    entity_type TEXT NOT NULL,               -- тип сущности: 'channel' или 'recorder'
                    entity_id TEXT NOT NULL,                 -- идентификатор: '{recorder_id}:{channel_no}' или '{recorder_id}'
                    status TEXT NOT NULL,                    -- новый статус: ok/warn/error/unknown
                    reason TEXT,                             -- текст причины на момент смены
                    recorded_at TEXT NOT NULL                -- время фиксации (ISO 8601, UTC)
                );

                CREATE INDEX IF NOT EXISTS idx_history_entity
                    ON status_history(entity_type, entity_id, recorded_at DESC);

                -- category_status_history: история смены статуса по категориям
                -- здоровья NVR (время/NTP, температура, диски, вентиляторы, каналы, архив).
                CREATE TABLE IF NOT EXISTS category_status_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,    -- PK (автоинкремент)
                    recorder_id TEXT NOT NULL,               -- ID регистратора
                    category TEXT NOT NULL,                  -- ключ категории: time/temperature/storage/fans/channels/archive
                    status TEXT NOT NULL,                    -- статус категории: ok/warn/error/unknown
                    reason TEXT,                             -- пояснение от classify_*_health()
                    recorded_at TEXT NOT NULL                -- время фиксации (ISO 8601, UTC)
                );

                CREATE INDEX IF NOT EXISTS idx_category_history_entity
                    ON category_status_history(recorder_id, category, recorded_at DESC);
                CREATE INDEX IF NOT EXISTS idx_channels_recorder
                    ON channels(recorder_id);

                -- recorder_poll_attempts: append-only журнал каждой попытки опроса
                -- регистратора в рамках массового job (планировщик/опрос всех/инвентаризация).
                CREATE TABLE IF NOT EXISTS recorder_poll_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,    -- PK (автоинкремент)
                    job_id TEXT NOT NULL,                    -- идентификатор job из PollJobManager (12 hex)
                    recorder_id TEXT NOT NULL,               -- ID регистратора
                    attempt INTEGER NOT NULL,                -- номер попытки/волны в job (1 = первый проход)
                    outcome TEXT NOT NULL,                   -- итог попытки: success/offline/error
                    online INTEGER NOT NULL DEFAULT 0,       -- 1, если NVR ответил (RecorderPollData.online)
                    error TEXT,                              -- текст ошибки подключения/исключения
                    duration_ms INTEGER,                     -- длительность попытки, мс
                    recorded_at TEXT NOT NULL                -- время попытки (ISO 8601, UTC)
                );

                CREATE INDEX IF NOT EXISTS idx_poll_attempts_recorder
                    ON recorder_poll_attempts(recorder_id, recorded_at DESC);
                CREATE INDEX IF NOT EXISTS idx_poll_attempts_job
                    ON recorder_poll_attempts(job_id, recorder_id, attempt);

                -- source_imports: журнал загрузок исходных файлов со страницы /sources
                -- (CMDB, заявки, Naumen, Арсенал).
                CREATE TABLE IF NOT EXISTS source_imports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,    -- PK (автоинкремент)
                    source_key TEXT NOT NULL,                -- ключ источника: cmdb/requests/naumen
                    filename TEXT,                           -- имя исходного файла из inputData/
                    imported_at TEXT NOT NULL,               -- время импорта (ISO 8601, UTC)
                    record_count INTEGER NOT NULL DEFAULT 0, -- число обработанных записей
                    status TEXT NOT NULL,                    -- результат импорта: ok/error
                    message TEXT                             -- текст результата/ошибки
                );

                CREATE INDEX IF NOT EXISTS idx_source_imports_key
                    ON source_imports(source_key, imported_at DESC);

                -- naumen_records: выгрузка заявок Naumen (naumen_all.xlsx).
                -- Полностью перезаписывается при каждом импорте (DELETE + batch INSERT).
                CREATE TABLE IF NOT EXISTS naumen_records (
                    external_id TEXT PRIMARY KEY,            -- "ID внешней системы" (PK)
                    number TEXT NOT NULL,                    -- "Номер" заявки
                    cost REAL NOT NULL DEFAULT 0,            -- "Стоимость" (пусто в xlsx → 0)
                    sberdrug_number TEXT,                    -- "Номер Сбердруг" (ключ подстановки суммы в отчёт оплаты)
                    description TEXT,                        -- "Описание" заявки
                    source_row INTEGER,                      -- номер строки в исходном xlsx
                    imported_at TEXT NOT NULL                -- время импорта (ISO 8601, UTC)
                );

                -- pp_requests: выгрузка заявок ПП (requests.xlsx).
                -- Полностью перезаписывается при каждом импорте (DELETE + batch INSERT OR REPLACE).
                CREATE TABLE IF NOT EXISTS pp_requests (
                    request_number TEXT PRIMARY KEY,         -- "Заявка №"
                    status TEXT,                             -- "Статус"
                    drug_number TEXT,                        -- "№ заявки ДРУГ"
                    created_at TEXT,                         -- "Дата создания (UTC)" (ISO)
                    completed_at TEXT,                       -- "Фактическая дата выполнения (UTC)" (ISO)
                    customer_fio TEXT,                       -- "ФИО заказчика"
                    tb TEXT,                                 -- "Территориальный банк"
                    work_type TEXT,                          -- "Вид работ"
                    act_status TEXT,                         -- "Статус акта"
                    amount_vat REAL NOT NULL DEFAULT 0,      -- "Сумма с НДС"
                    warranty TEXT,                           -- "Гарантийная заявка"
                    address TEXT,                            -- "Адрес"
                    security_system_type TEXT,               -- "Вид системы безопасности"
                    in_limit TEXT,                           -- "В лимите"
                    raw_json TEXT,                           -- полный исходный ряд (JSON)
                    source_row INTEGER,                      -- номер строки в исходном xlsx
                    imported_at TEXT NOT NULL                -- время импорта (ISO 8601, UTC)
                );

                CREATE INDEX IF NOT EXISTS idx_pp_requests_tb
                    ON pp_requests(tb);
                CREATE INDEX IF NOT EXISTS idx_pp_requests_drug
                    ON pp_requests(drug_number);
                CREATE INDEX IF NOT EXISTS idx_pp_requests_completed
                    ON pp_requests(completed_at);

                -- arsenal_analytics: лист «Аналитика» выгрузки АС Арсенал.
                CREATE TABLE IF NOT EXISTS arsenal_analytics (
                    passport_number TEXT PRIMARY KEY,
                    tb TEXT NOT NULL DEFAULT '',
                    gosb TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT '',
                    object_type TEXT NOT NULL DEFAULT '',
                    subtype TEXT NOT NULL DEFAULT '',
                    object_name TEXT NOT NULL DEFAULT '',
                    address TEXT NOT NULL DEFAULT '',
                    fill_total REAL NOT NULL DEFAULT 0,
                    fill_sections_json TEXT NOT NULL DEFAULT '{}',
                    errors_total INTEGER NOT NULL DEFAULT 0,
                    errors_sections_json TEXT NOT NULL DEFAULT '{}',
                    fill_project_docs REAL NOT NULL DEFAULT 0,
                    docs_json TEXT NOT NULL DEFAULT '{}',
                    has_photos TEXT NOT NULL DEFAULT '',
                    source_row INTEGER,
                    imported_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_arsenal_analytics_object_type
                    ON arsenal_analytics(object_type);

                -- arsenal_systems: системные листы (САЗ, СОУЭ, СОТС, САПС, ТСВ, СКУД).
                CREATE TABLE IF NOT EXISTS arsenal_systems (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    passport_number TEXT NOT NULL,
                    tb TEXT NOT NULL DEFAULT '',
                    gosb TEXT NOT NULL DEFAULT '',
                    object_type TEXT NOT NULL DEFAULT '',
                    subtype TEXT NOT NULL DEFAULT '',
                    system_type TEXT NOT NULL,
                    manufacturer TEXT NOT NULL DEFAULT '',
                    year INTEGER,
                    present INTEGER NOT NULL DEFAULT 1,
                    source_row INTEGER,
                    imported_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_arsenal_systems_type_object
                    ON arsenal_systems(system_type, object_type);
                """
            )
            self._migrate_schema(conn)

    def _migrate_schema(self, conn: sqlite3.Connection) -> None:
        metrics_columns = {
            row[1] for row in conn.execute("PRAGMA table_info(recorder_metrics)").fetchall()
        }
        # Колонки recorder_metrics, добавленные миграциями поверх базовой схемы.
        # Формат: (имя, тип). Комментарий справа — назначение поля.
        metrics_additions = [
            ("local_time", "TEXT"),                  # локальное время на NVR (строка с устройства)
            ("utc_time", "TEXT"),                    # UTC-время на NVR (строка с устройства)
            ("sync_type", "TEXT"),                   # режим синхронизации времени: Manual/NTP/GPS
            ("storage_used_mb", "REAL"),             # занято хранилища, МБ
            ("storage_total_mb", "REAL"),            # всего хранилища, МБ
            ("disks_json", "TEXT"),                  # JSON-массив дисков (Storage/Status/Model/Temperature/...)
            ("archive_min_days", "REAL"),            # минимальная глубина архива среди каналов, сут.
            ("archive_max_days", "REAL"),            # максимальная глубина архива среди каналов, сут.
            ("system_events_json", "TEXT"),          # JSON-объект "событие SUNAPI -> активно ли" (HDDFail, CPUFanError, ...)
            ("system_event_times_json", "TEXT"),     # JSON-объект "событие SUNAPI -> время последней записи в systemlog"
            ("storageinfo_ok", "INTEGER NOT NULL DEFAULT 0"),  # 1, если CGI хранилища вернул валидные данные (метрикам дисков можно доверять)
            ("archive_poll_error", "TEXT"),          # текст ошибки при опросе периода записи (иначе NULL)
            ("recording_storage_enable", "INTEGER"), # 1=запись на накопитель включена, 0=выключена, NULL=неизвестно
            ("last_poll_job_id", "TEXT"),            # ID последнего массового job, обновившего сводку (last_poll_*)
            ("last_poll_attempts", "INTEGER"),       # число попыток NVR в том job
            ("last_poll_success_attempt", "INTEGER"),  # номер успешной попытки (1-based); NULL, если ответа не было
            ("last_poll_first_try_ok", "INTEGER"),   # 1=ответ с первой попытки job, 0=с повтора или без ответа
            ("recording_storage_overwrite", "INTEGER"),  # 1=режим перезаписи (overwrite) при заполнении, 0=нет, NULL=неизвестно
            ("cpu_usage_max", "REAL"),               # макс. нагрузка декодирования по активным каналам, %
            ("cpu_usage_avg", "REAL"),               # средняя нагрузка декодирования по активным каналам, %
            ("data_rate_total_mbps", "REAL"),        # суммарный битрейт всех активных каналов, Мбит/с
            ("channels_zero_bitrate", "INTEGER"),    # число IP-каналов с нулевым битрейтом (без аналоговых)
            ("channels_poe_off", "INTEGER"),         # число PoE-портов без питания (резерв; сейчас не заполняется)
            ("serial_number", "TEXT"),               # серийный номер устройства
            ("manufacture_date", "TEXT"),            # дата производства, выведенная из серийника (Samsung/Hanwha date code)
        ]
        for name, col_type in metrics_additions:
            if name not in metrics_columns:
                conn.execute(
                    f"ALTER TABLE recorder_metrics ADD COLUMN {name} {col_type}"
                )

        channel_columns = {
            row[1] for row in conn.execute("PRAGMA table_info(channels)").fetchall()
        }
        # Колонки channels, добавленные миграциями поверх базовой схемы.
        channel_additions = [
            ("archive_start", "TEXT"),   # начало периода записи по каналу (строка с NVR)
            ("archive_end", "TEXT"),     # конец периода записи по каналу (строка с NVR)
            ("archive_days", "REAL"),    # глубина архива канала, сут.
            ("data_rate", "REAL"),       # битрейт потока канала, Мбит/с (DataRate из SUNAPI)
            ("cpu_usage", "REAL"),       # нагрузка декодирования на канал, %
            ("poe_status", "INTEGER"),   # 1=питание PoE-порта включено, 0=выключено, NULL=нет данных/не поддерживается
        ]
        for name, col_type in channel_additions:
            if name not in channel_columns:
                conn.execute(f"ALTER TABLE channels ADD COLUMN {name} {col_type}")

        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        if "source_imports" not in tables:
            conn.execute(
                """
                CREATE TABLE source_imports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_key TEXT NOT NULL,
                    filename TEXT,
                    imported_at TEXT NOT NULL,
                    record_count INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL,
                    message TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_source_imports_key
                    ON source_imports(source_key, imported_at DESC)
                """
            )

        if "naumen_records" not in tables:
            conn.execute(
                """
                CREATE TABLE naumen_records (
                    external_id TEXT PRIMARY KEY,
                    number TEXT NOT NULL,
                    cost REAL NOT NULL DEFAULT 0,
                    sberdrug_number TEXT,
                    description TEXT,
                    source_row INTEGER,
                    imported_at TEXT NOT NULL
                )
                """
            )

        if "pp_requests" not in tables:
            conn.execute(
                """
                CREATE TABLE pp_requests (
                    request_number TEXT PRIMARY KEY,
                    status TEXT,
                    drug_number TEXT,
                    created_at TEXT,
                    completed_at TEXT,
                    customer_fio TEXT,
                    tb TEXT,
                    work_type TEXT,
                    act_status TEXT,
                    amount_vat REAL NOT NULL DEFAULT 0,
                    warranty TEXT,
                    address TEXT,
                    security_system_type TEXT,
                    in_limit TEXT,
                    raw_json TEXT,
                    source_row INTEGER,
                    imported_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_pp_requests_tb
                    ON pp_requests(tb)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_pp_requests_drug
                    ON pp_requests(drug_number)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_pp_requests_completed
                    ON pp_requests(completed_at)
                """
            )

        if "arsenal_analytics" not in tables:
            conn.execute(
                """
                CREATE TABLE arsenal_analytics (
                    passport_number TEXT PRIMARY KEY,
                    tb TEXT NOT NULL DEFAULT '',
                    gosb TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT '',
                    object_type TEXT NOT NULL DEFAULT '',
                    subtype TEXT NOT NULL DEFAULT '',
                    object_name TEXT NOT NULL DEFAULT '',
                    address TEXT NOT NULL DEFAULT '',
                    fill_total REAL NOT NULL DEFAULT 0,
                    fill_sections_json TEXT NOT NULL DEFAULT '{}',
                    errors_total INTEGER NOT NULL DEFAULT 0,
                    errors_sections_json TEXT NOT NULL DEFAULT '{}',
                    fill_project_docs REAL NOT NULL DEFAULT 0,
                    docs_json TEXT NOT NULL DEFAULT '{}',
                    has_photos TEXT NOT NULL DEFAULT '',
                    source_row INTEGER,
                    imported_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_arsenal_analytics_object_type
                    ON arsenal_analytics(object_type)
                """
            )

        if "arsenal_systems" not in tables:
            conn.execute(
                """
                CREATE TABLE arsenal_systems (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    passport_number TEXT NOT NULL,
                    tb TEXT NOT NULL DEFAULT '',
                    gosb TEXT NOT NULL DEFAULT '',
                    object_type TEXT NOT NULL DEFAULT '',
                    subtype TEXT NOT NULL DEFAULT '',
                    system_type TEXT NOT NULL,
                    manufacturer TEXT NOT NULL DEFAULT '',
                    year INTEGER,
                    present INTEGER NOT NULL DEFAULT 1,
                    source_row INTEGER,
                    imported_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_arsenal_systems_type_object
                    ON arsenal_systems(system_type, object_type)
                """
            )

        if "arsenal_analytics" in tables:
            arsenal_columns = {
                row[1]
                for row in conn.execute(
                    "PRAGMA table_info(arsenal_analytics)"
                ).fetchall()
            }
            if "address" not in arsenal_columns:
                conn.execute(
                    "ALTER TABLE arsenal_analytics ADD COLUMN address TEXT NOT NULL DEFAULT ''"
                )

        if "arsenal_systems" in tables:
            arsenal_system_columns = {
                row[1]
                for row in conn.execute(
                    "PRAGMA table_info(arsenal_systems)"
                ).fetchall()
            }
            if "present" not in arsenal_system_columns:
                conn.execute(
                    "ALTER TABLE arsenal_systems ADD COLUMN present INTEGER NOT NULL DEFAULT 1"
                )

    @contextmanager
    def replace_naumen_records(
        self, imported_at: Optional[datetime] = None
    ) -> Iterator[NaumenReplaceSession]:
        when = _iso(imported_at or datetime.now(timezone.utc))
        with self._connect() as conn:
            conn.execute("DELETE FROM naumen_records")
            session = NaumenReplaceSession(conn, when)
            yield session

    @contextmanager
    def replace_pp_requests(
        self, imported_at: Optional[datetime] = None
    ) -> Iterator[PPReplaceSession]:
        when = _iso(imported_at or datetime.now(timezone.utc))
        with self._connect() as conn:
            conn.execute("DELETE FROM pp_requests")
            session = PPReplaceSession(conn, when)
            yield session

    def count_naumen_records(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS cnt FROM naumen_records").fetchone()
        return int(row["cnt"]) if row else 0

    def count_pp_requests(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS cnt FROM pp_requests").fetchone()
        return int(row["cnt"]) if row else 0

    def pp_requests_rows(
        self,
        *,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """Строки pp_requests для отчётов; опционально по created_at (ISO UTC)."""
        clauses: list[str] = []
        params: list[str] = []
        if created_from is not None:
            clauses.append("created_at >= ?")
            params.append(_iso(created_from))
        if created_to is not None:
            clauses.append("created_at < ?")
            params.append(_iso(created_to))
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = (
            "SELECT request_number, status, drug_number, created_at, completed_at, "
            "customer_fio, tb, work_type, act_status, amount_vat, warranty, "
            "address, security_system_type, in_limit, raw_json, source_row "
            f"FROM pp_requests{where} ORDER BY created_at, source_row"
        )
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def naumen_description_by_sberdrug(self) -> dict[str, str]:
        """Карта «Номер Сбердруг» -> первая непустая «Описание» (по source_row)."""
        result: dict[str, str] = {}
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT sberdrug_number, description FROM naumen_records "
                "WHERE sberdrug_number IS NOT NULL AND sberdrug_number != '' "
                "ORDER BY source_row"
            ).fetchall()
        for row in rows:
            key = str(row["sberdrug_number"]).strip()
            desc = (row["description"] or "").strip()
            if key and desc and key not in result:
                result[key] = desc
        return result

    @contextmanager
    def replace_arsenal_data(
        self, imported_at: Optional[datetime] = None
    ) -> Iterator[ArsenalReplaceSession]:
        when = _iso(imported_at or datetime.now(timezone.utc))
        with self._connect() as conn:
            conn.execute("DELETE FROM arsenal_systems")
            conn.execute("DELETE FROM arsenal_analytics")
            session = ArsenalReplaceSession(conn, when)
            yield session

    def count_arsenal_records(self) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM arsenal_analytics"
            ).fetchone()
        return int(row["cnt"]) if row else 0

    def arsenal_analytics_rows(self) -> list[ArsenalAnalyticsDbRow]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM arsenal_analytics
                ORDER BY object_type, passport_number
                """
            ).fetchall()
        return [_arsenal_analytics_from_row(row) for row in rows]

    def arsenal_systems_rows(self) -> list[ArsenalSystemDbRow]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM arsenal_systems
                ORDER BY system_type, object_type, manufacturer
                """
            ).fetchall()
        return [_arsenal_system_from_row(row) for row in rows]

    def get_arsenal_analytics(self, passport_number: str) -> Optional[ArsenalAnalyticsDbRow]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM arsenal_analytics WHERE passport_number = ?",
                (passport_number,),
            ).fetchone()
        if row is None:
            return None
        return _arsenal_analytics_from_row(row)

    def arsenal_systems_for_passport(
        self, passport_number: str
    ) -> list[ArsenalSystemDbRow]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM arsenal_systems
                WHERE passport_number = ?
                ORDER BY system_type, manufacturer
                """,
                (passport_number,),
            ).fetchall()
        return [_arsenal_system_from_row(row) for row in rows]

    def naumen_cost_by_sberdrug(self) -> dict[str, float]:
        """Карта «Номер Сбердруг» -> первая ненулевая «Стоимость» (по source_row)."""
        result: dict[str, float] = {}
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT sberdrug_number, cost FROM naumen_records "
                "WHERE sberdrug_number IS NOT NULL AND sberdrug_number != '' "
                "AND cost > 0 ORDER BY source_row"
            ).fetchall()
        for row in rows:
            key = str(row["sberdrug_number"]).strip()
            if key and key not in result:
                result[key] = float(row["cost"])
        return result

    def record_source_import(
        self,
        source_key: str,
        *,
        filename: Optional[str] = None,
        record_count: int = 0,
        status: str = "ok",
        message: Optional[str] = None,
        imported_at: Optional[datetime] = None,
    ) -> SourceImportRow:
        when = imported_at or datetime.now(timezone.utc)
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO source_imports (
                    source_key, filename, imported_at, record_count, status, message
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    source_key,
                    filename,
                    _iso(when),
                    record_count,
                    status,
                    message,
                ),
            )
            row_id = cur.lastrowid
        return SourceImportRow(
            id=row_id,
            source_key=source_key,
            filename=filename,
            imported_at=when,
            record_count=record_count,
            status=status,
            message=message,
        )

    def list_source_imports(self, limit: int = 50) -> list[SourceImportRow]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM source_imports
                ORDER BY imported_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [_source_import_from_row(r) for r in rows]

    def get_latest_source_import(self, source_key: str) -> Optional[SourceImportRow]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM source_imports
                WHERE source_key = ? AND status = 'ok'
                ORDER BY imported_at DESC
                LIMIT 1
                """,
                (source_key,),
            ).fetchone()
        if row is None:
            return None
        return _source_import_from_row(row)

    def upsert_channel(
        self,
        recorder_id: str,
        channel_no: int,
        *,
        name: Optional[str] = None,
        camera_ip: Optional[str] = None,
        camera_model: Optional[str] = None,
        source_state: Optional[str] = None,
        health_status: str = "unknown",
        health_reason: Optional[str] = None,
        video_loss: Optional[bool] = None,
        last_polled_at: Optional[datetime] = None,
        archive_start: Optional[str] = None,
        archive_end: Optional[str] = None,
        archive_days: Optional[float] = None,
        data_rate: Optional[float] = None,
        cpu_usage: Optional[float] = None,
        poe_status: Optional[bool] = None,
    ) -> None:
        polled = _iso(last_polled_at)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO channels (
                    recorder_id, channel_no, name, camera_ip, camera_model,
                    source_state, health_status, health_reason, video_loss, last_polled_at,
                    archive_start, archive_end, archive_days,
                    data_rate, cpu_usage, poe_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(recorder_id, channel_no) DO UPDATE SET
                    name=excluded.name,
                    camera_ip=excluded.camera_ip,
                    camera_model=excluded.camera_model,
                    source_state=excluded.source_state,
                    health_status=excluded.health_status,
                    health_reason=excluded.health_reason,
                    video_loss=excluded.video_loss,
                    last_polled_at=excluded.last_polled_at,
                    archive_start=excluded.archive_start,
                    archive_end=excluded.archive_end,
                    archive_days=excluded.archive_days,
                    data_rate=excluded.data_rate,
                    cpu_usage=excluded.cpu_usage,
                    poe_status=excluded.poe_status
                """,
                (
                    recorder_id,
                    channel_no,
                    name,
                    camera_ip,
                    camera_model,
                    source_state,
                    health_status,
                    health_reason,
                    _bool_int(video_loss),
                    polled,
                    archive_start,
                    archive_end,
                    archive_days,
                    data_rate,
                    cpu_usage,
                    _bool_int(poe_status),
                ),
            )

    def remove_channels_not_in(self, recorder_id: str, channel_nos: list[int]) -> None:
        with self._connect() as conn:
            if not channel_nos:
                conn.execute("DELETE FROM channels WHERE recorder_id = ?", (recorder_id,))
                return
            placeholders = ",".join("?" * len(channel_nos))
            conn.execute(
                f"DELETE FROM channels WHERE recorder_id = ? AND channel_no NOT IN ({placeholders})",
                (recorder_id, *channel_nos),
            )

    def list_channels(
        self,
        recorder_id: Optional[str] = None,
        health: Optional[str] = None,
    ) -> list[ChannelRow]:
        sql = "SELECT * FROM channels WHERE 1=1"
        params: list = []
        if recorder_id:
            sql += " AND recorder_id = ?"
            params.append(recorder_id)
        if health:
            sql += " AND health_status = ?"
            params.append(health)
        sql += " ORDER BY recorder_id, channel_no"
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_channel_from_row(r) for r in rows]

    def get_channel(self, recorder_id: str, channel_no: int) -> Optional[ChannelRow]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM channels WHERE recorder_id = ? AND channel_no = ?",
                (recorder_id, channel_no),
            ).fetchone()
        return _channel_from_row(row) if row else None

    def upsert_recorder_metrics(
        self,
        recorder_id: str,
        *,
        model: Optional[str] = None,
        firmware_version: Optional[str] = None,
        device_online: bool = False,
        health_status: str = "unknown",
        health_reason: Optional[str] = None,
        ntp_status: Optional[str] = None,
        time_skew_seconds: Optional[float] = None,
        storage_used_percent: Optional[float] = None,
        storage_status: Optional[str] = None,
        archive_start: Optional[str] = None,
        archive_end: Optional[str] = None,
        archive_days: Optional[float] = None,
        archive_min_days: Optional[float] = None,
        archive_max_days: Optional[float] = None,
        channel_count: int = 0,
        channels_ok: int = 0,
        channels_warn: int = 0,
        channels_error: int = 0,
        channels_unknown: int = 0,
        last_polled_at: Optional[datetime] = None,
        local_time: Optional[str] = None,
        utc_time: Optional[str] = None,
        sync_type: Optional[str] = None,
        storage_used_mb: Optional[float] = None,
        storage_total_mb: Optional[float] = None,
        disks: Optional[list[dict[str, Any]]] = None,
        system_events: Optional[dict[str, bool]] = None,
        system_event_times: Optional[dict[str, str]] = None,
        storageinfo_ok: bool = False,
        archive_poll_error: Optional[str] = None,
        recording_storage_enable: Optional[bool] = None,
        recording_storage_overwrite: Optional[bool] = None,
        cpu_usage_max: Optional[float] = None,
        cpu_usage_avg: Optional[float] = None,
        data_rate_total_mbps: Optional[float] = None,
        channels_zero_bitrate: Optional[int] = None,
        channels_poe_off: Optional[int] = None,
        serial_number: Optional[str] = None,
        manufacture_date: Optional[str] = None,
    ) -> None:
        disks_json = json.dumps(disks, ensure_ascii=False) if disks else None
        system_events_json = (
            json.dumps(system_events, ensure_ascii=False) if system_events else None
        )
        system_event_times_json = (
            json.dumps(system_event_times, ensure_ascii=False)
            if system_event_times
            else None
        )
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO recorder_metrics (
                    recorder_id, model, firmware_version, device_online,
                    health_status, health_reason, ntp_status, time_skew_seconds,
                    storage_used_percent, storage_status, archive_start, archive_end,
                    archive_days, archive_min_days, archive_max_days,
                    channel_count, channels_ok, channels_warn,
                    channels_error, channels_unknown, last_polled_at,
                    local_time, utc_time, sync_type,
                    storage_used_mb, storage_total_mb, disks_json, system_events_json,
                    system_event_times_json,
                    storageinfo_ok, archive_poll_error, recording_storage_enable,
                    recording_storage_overwrite, cpu_usage_max, cpu_usage_avg,
                    data_rate_total_mbps, channels_zero_bitrate, channels_poe_off,
                    serial_number, manufacture_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                          ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(recorder_id) DO UPDATE SET
                    model=excluded.model,
                    firmware_version=excluded.firmware_version,
                    device_online=excluded.device_online,
                    health_status=excluded.health_status,
                    health_reason=excluded.health_reason,
                    ntp_status=excluded.ntp_status,
                    time_skew_seconds=excluded.time_skew_seconds,
                    storage_used_percent=excluded.storage_used_percent,
                    storage_status=excluded.storage_status,
                    archive_start=excluded.archive_start,
                    archive_end=excluded.archive_end,
                    archive_days=excluded.archive_days,
                    archive_min_days=excluded.archive_min_days,
                    archive_max_days=excluded.archive_max_days,
                    channel_count=excluded.channel_count,
                    channels_ok=excluded.channels_ok,
                    channels_warn=excluded.channels_warn,
                    channels_error=excluded.channels_error,
                    channels_unknown=excluded.channels_unknown,
                    last_polled_at=excluded.last_polled_at,
                    local_time=excluded.local_time,
                    utc_time=excluded.utc_time,
                    sync_type=excluded.sync_type,
                    storage_used_mb=excluded.storage_used_mb,
                    storage_total_mb=excluded.storage_total_mb,
                    disks_json=excluded.disks_json,
                    system_events_json=excluded.system_events_json,
                    system_event_times_json=excluded.system_event_times_json,
                    storageinfo_ok=excluded.storageinfo_ok,
                    archive_poll_error=excluded.archive_poll_error,
                    recording_storage_enable=excluded.recording_storage_enable,
                    recording_storage_overwrite=excluded.recording_storage_overwrite,
                    cpu_usage_max=excluded.cpu_usage_max,
                    cpu_usage_avg=excluded.cpu_usage_avg,
                    data_rate_total_mbps=excluded.data_rate_total_mbps,
                    channels_zero_bitrate=excluded.channels_zero_bitrate,
                    channels_poe_off=excluded.channels_poe_off,
                    serial_number=excluded.serial_number,
                    manufacture_date=excluded.manufacture_date
                """,
                (
                    recorder_id,
                    model,
                    firmware_version,
                    int(device_online),
                    health_status,
                    health_reason,
                    ntp_status,
                    time_skew_seconds,
                    storage_used_percent,
                    storage_status,
                    archive_start,
                    archive_end,
                    archive_days,
                    archive_min_days,
                    archive_max_days,
                    channel_count,
                    channels_ok,
                    channels_warn,
                    channels_error,
                    channels_unknown,
                    _iso(last_polled_at),
                    local_time,
                    utc_time,
                    sync_type,
                    storage_used_mb,
                    storage_total_mb,
                    disks_json,
                    system_events_json,
                    system_event_times_json,
                    int(storageinfo_ok),
                    archive_poll_error,
                    _bool_int(recording_storage_enable),
                    _bool_int(recording_storage_overwrite),
                    cpu_usage_max,
                    cpu_usage_avg,
                    data_rate_total_mbps,
                    channels_zero_bitrate,
                    channels_poe_off,
                    serial_number,
                    manufacture_date,
                ),
            )

    def get_recorder_metrics(self, recorder_id: str) -> Optional[RecorderMetricsRow]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM recorder_metrics WHERE recorder_id = ?",
                (recorder_id,),
            ).fetchone()
        return _metrics_from_row(row) if row else None

    def list_recorder_metrics(self) -> list[RecorderMetricsRow]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM recorder_metrics ORDER BY recorder_id"
            ).fetchall()
        return [_metrics_from_row(r) for r in rows]

    def record_history(
        self,
        entity_type: str,
        entity_id: str,
        status: str,
        reason: Optional[str] = None,
        recorded_at: Optional[datetime] = None,
    ) -> None:
        ts = recorded_at or datetime.now(timezone.utc)
        with self._connect() as conn:
            last = conn.execute(
                """
                SELECT status FROM status_history
                WHERE entity_type = ? AND entity_id = ?
                ORDER BY recorded_at DESC LIMIT 1
                """,
                (entity_type, entity_id),
            ).fetchone()
            if last and last["status"] == status:
                return
            conn.execute(
                """
                INSERT INTO status_history (entity_type, entity_id, status, reason, recorded_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (entity_type, entity_id, status, reason, _iso(ts)),
            )

    def list_history(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        limit: int = 200,
    ) -> list[HistoryRow]:
        sql = "SELECT * FROM status_history WHERE 1=1"
        params: list = []
        if entity_type:
            sql += " AND entity_type = ?"
            params.append(entity_type)
        if entity_id:
            sql += " AND entity_id = ?"
            params.append(entity_id)
        sql += " ORDER BY recorded_at DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_history_from_row(r) for r in rows]

    def record_category_status(
        self,
        recorder_id: str,
        category: str,
        status: str,
        reason: Optional[str] = None,
        recorded_at: Optional[datetime] = None,
    ) -> None:
        ts = recorded_at or datetime.now(timezone.utc)
        with self._connect() as conn:
            last = conn.execute(
                """
                SELECT status FROM category_status_history
                WHERE recorder_id = ? AND category = ?
                ORDER BY recorded_at DESC LIMIT 1
                """,
                (recorder_id, category),
            ).fetchone()
            if last and last["status"] == status:
                return
            if (
                status in _TRANSPARENT_GAP_STATUSES
                and last
                and last["status"] in _CATEGORY_PROBLEM_STATUSES
            ):
                return
            conn.execute(
                """
                INSERT INTO category_status_history (
                    recorder_id, category, status, reason, recorded_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (recorder_id, category, status, reason, _iso(ts)),
            )

    def list_category_history(
        self,
        recorder_id: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 500,
    ) -> list[CategoryStatusHistoryRow]:
        sql = "SELECT * FROM category_status_history WHERE 1=1"
        params: list = []
        if recorder_id:
            sql += " AND recorder_id = ?"
            params.append(recorder_id)
        if category:
            sql += " AND category = ?"
            params.append(category)
        sql += " ORDER BY recorded_at ASC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_category_history_from_row(r) for r in rows]

    def get_category_problem_since(
        self,
        recorder_id: str,
        category: str,
    ) -> Optional[datetime]:
        rows = self.list_category_history(
            recorder_id=recorder_id,
            category=category,
        )
        return _problem_episode_start(rows)

    def category_problem_since_map(self) -> dict[tuple[str, str], datetime]:
        with self._connect() as conn:
            pairs = conn.execute(
                """
                SELECT DISTINCT recorder_id, category
                FROM category_status_history
                """
            ).fetchall()
        result: dict[tuple[str, str], datetime] = {}
        for pair in pairs:
            rid = pair["recorder_id"]
            cat = pair["category"]
            since = self.get_category_problem_since(rid, cat)
            if since is not None:
                result[(rid, cat)] = since
        return result

    def list_recorder_status_history(
        self,
        recorder_id: str,
        *,
        limit: int = 500,
    ) -> list[HistoryRow]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM status_history
                WHERE entity_type = 'recorder' AND entity_id = ?
                ORDER BY recorded_at ASC
                LIMIT ?
                """,
                (recorder_id, limit),
            ).fetchall()
        return [_history_from_row(r) for r in rows]

    def get_recorder_problem_since(self, recorder_id: str) -> Optional[datetime]:
        rows = self.list_recorder_status_history(recorder_id)
        return _recorder_problem_episode_start(rows)

    def recorder_problem_since_map(self) -> dict[str, datetime]:
        with self._connect() as conn:
            ids = conn.execute(
                """
                SELECT DISTINCT entity_id
                FROM status_history
                WHERE entity_type = 'recorder'
                """
            ).fetchall()
        result: dict[str, datetime] = {}
        for row in ids:
            rid = row["entity_id"]
            since = self.get_recorder_problem_since(rid)
            if since is not None:
                result[rid] = since
        return result

    def insert_poll_attempt(
        self,
        *,
        job_id: str,
        recorder_id: str,
        attempt: int,
        outcome: str,
        online: bool,
        error: Optional[str] = None,
        duration_ms: Optional[int] = None,
        recorded_at: Optional[datetime] = None,
    ) -> None:
        ts = recorded_at or datetime.now(timezone.utc)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO recorder_poll_attempts (
                    job_id, recorder_id, attempt, outcome, online,
                    error, duration_ms, recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    recorder_id,
                    attempt,
                    outcome,
                    int(online),
                    error,
                    duration_ms,
                    _iso(ts),
                ),
            )

    def list_poll_attempts(
        self,
        *,
        job_id: Optional[str] = None,
        recorder_id: Optional[str] = None,
        limit: int = 500,
    ) -> list[RecorderPollAttemptRow]:
        sql = "SELECT * FROM recorder_poll_attempts WHERE 1=1"
        params: list = []
        if job_id:
            sql += " AND job_id = ?"
            params.append(job_id)
        if recorder_id:
            sql += " AND recorder_id = ?"
            params.append(recorder_id)
        sql += " ORDER BY recorded_at DESC, id DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_poll_attempt_from_row(r) for r in rows]

    def update_poll_recorder_summary(
        self,
        recorder_id: str,
        *,
        job_id: str,
        attempts: int,
        success_attempt: Optional[int],
        first_try_ok: bool,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE recorder_metrics SET
                    last_poll_job_id = ?,
                    last_poll_attempts = ?,
                    last_poll_success_attempt = ?,
                    last_poll_first_try_ok = ?
                WHERE recorder_id = ?
                """,
                (
                    job_id,
                    attempts,
                    success_attempt,
                    int(first_try_ok),
                    recorder_id,
                ),
            )

    def delete_recorder_data(self, recorder_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM channels WHERE recorder_id = ?", (recorder_id,))
            conn.execute(
                "DELETE FROM recorder_metrics WHERE recorder_id = ?", (recorder_id,)
            )
            conn.execute(
                "DELETE FROM status_history WHERE entity_id LIKE ?",
                (f"{recorder_id}%",),
            )
            conn.execute(
                "DELETE FROM category_status_history WHERE recorder_id = ?",
                (recorder_id,),
            )
            conn.execute(
                "DELETE FROM recorder_poll_attempts WHERE recorder_id = ?",
                (recorder_id,),
            )


def _iso(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _bool_int(value: Optional[bool]) -> Optional[int]:
    if value is None:
        return None
    return 1 if value else 0


def _channel_from_row(row: sqlite3.Row) -> ChannelRow:
    vl = row["video_loss"]
    return ChannelRow(
        id=row["id"],
        recorder_id=row["recorder_id"],
        channel_no=row["channel_no"],
        name=row["name"],
        camera_ip=row["camera_ip"],
        camera_model=row["camera_model"],
        source_state=row["source_state"],
        health_status=row["health_status"],
        health_reason=row["health_reason"],
        video_loss=None if vl is None else bool(vl),
        last_polled_at=_parse_iso(row["last_polled_at"]),
        archive_start=row["archive_start"] if "archive_start" in row.keys() else None,
        archive_end=row["archive_end"] if "archive_end" in row.keys() else None,
        archive_days=row["archive_days"] if "archive_days" in row.keys() else None,
        data_rate=row["data_rate"] if "data_rate" in row.keys() else None,
        cpu_usage=row["cpu_usage"] if "cpu_usage" in row.keys() else None,
        poe_status=(
            None
            if "poe_status" not in row.keys() or row["poe_status"] is None
            else bool(row["poe_status"])
        ),
    )


def _metrics_from_row(row: sqlite3.Row) -> RecorderMetricsRow:
    return RecorderMetricsRow(
        recorder_id=row["recorder_id"],
        model=row["model"],
        firmware_version=row["firmware_version"],
        device_online=bool(row["device_online"]),
        health_status=row["health_status"],
        health_reason=row["health_reason"],
        ntp_status=row["ntp_status"],
        time_skew_seconds=row["time_skew_seconds"],
        storage_used_percent=row["storage_used_percent"],
        storage_status=row["storage_status"],
        archive_start=row["archive_start"],
        archive_end=row["archive_end"],
        archive_days=row["archive_days"],
        archive_min_days=row["archive_min_days"] if "archive_min_days" in row.keys() else None,
        archive_max_days=row["archive_max_days"] if "archive_max_days" in row.keys() else None,
        channel_count=row["channel_count"],
        channels_ok=row["channels_ok"],
        channels_warn=row["channels_warn"],
        channels_error=row["channels_error"],
        channels_unknown=row["channels_unknown"],
        last_polled_at=_parse_iso(row["last_polled_at"]),
        local_time=row["local_time"] if "local_time" in row.keys() else None,
        utc_time=row["utc_time"] if "utc_time" in row.keys() else None,
        sync_type=row["sync_type"] if "sync_type" in row.keys() else None,
        storage_used_mb=row["storage_used_mb"] if "storage_used_mb" in row.keys() else None,
        storage_total_mb=row["storage_total_mb"] if "storage_total_mb" in row.keys() else None,
        disks_json=row["disks_json"] if "disks_json" in row.keys() else None,
        system_events_json=(
            row["system_events_json"] if "system_events_json" in row.keys() else None
        ),
        system_event_times_json=(
            row["system_event_times_json"]
            if "system_event_times_json" in row.keys()
            else None
        ),
        storageinfo_ok=bool(row["storageinfo_ok"]) if "storageinfo_ok" in row.keys() else False,
        archive_poll_error=(
            row["archive_poll_error"] if "archive_poll_error" in row.keys() else None
        ),
        recording_storage_enable=(
            None
            if "recording_storage_enable" not in row.keys()
            or row["recording_storage_enable"] is None
            else bool(row["recording_storage_enable"])
        ),
        recording_storage_overwrite=(
            None
            if "recording_storage_overwrite" not in row.keys()
            or row["recording_storage_overwrite"] is None
            else bool(row["recording_storage_overwrite"])
        ),
        cpu_usage_max=row["cpu_usage_max"] if "cpu_usage_max" in row.keys() else None,
        cpu_usage_avg=row["cpu_usage_avg"] if "cpu_usage_avg" in row.keys() else None,
        data_rate_total_mbps=(
            row["data_rate_total_mbps"]
            if "data_rate_total_mbps" in row.keys()
            else None
        ),
        channels_zero_bitrate=(
            row["channels_zero_bitrate"]
            if "channels_zero_bitrate" in row.keys()
            else None
        ),
        channels_poe_off=(
            row["channels_poe_off"] if "channels_poe_off" in row.keys() else None
        ),
        serial_number=row["serial_number"] if "serial_number" in row.keys() else None,
        manufacture_date=(
            row["manufacture_date"] if "manufacture_date" in row.keys() else None
        ),
        last_poll_job_id=(
            row["last_poll_job_id"] if "last_poll_job_id" in row.keys() else None
        ),
        last_poll_attempts=(
            row["last_poll_attempts"] if "last_poll_attempts" in row.keys() else None
        ),
        last_poll_success_attempt=(
            row["last_poll_success_attempt"]
            if "last_poll_success_attempt" in row.keys()
            else None
        ),
        last_poll_first_try_ok=(
            None
            if "last_poll_first_try_ok" not in row.keys()
            or row["last_poll_first_try_ok"] is None
            else bool(row["last_poll_first_try_ok"])
        ),
    )


def _poll_attempt_from_row(row: sqlite3.Row) -> RecorderPollAttemptRow:
    return RecorderPollAttemptRow(
        id=row["id"],
        job_id=row["job_id"],
        recorder_id=row["recorder_id"],
        attempt=row["attempt"],
        outcome=row["outcome"],
        online=bool(row["online"]),
        error=row["error"],
        duration_ms=row["duration_ms"],
        recorded_at=_parse_iso(row["recorded_at"]) or datetime.now(timezone.utc),
    )


def _history_from_row(row: sqlite3.Row) -> HistoryRow:
    return HistoryRow(
        id=row["id"],
        entity_type=row["entity_type"],
        entity_id=row["entity_id"],
        status=row["status"],
        reason=row["reason"],
        recorded_at=_parse_iso(row["recorded_at"]) or datetime.now(timezone.utc),
    )


def _arsenal_analytics_from_row(row: sqlite3.Row) -> ArsenalAnalyticsDbRow:
    return ArsenalAnalyticsDbRow(
        passport_number=row["passport_number"],
        tb=row["tb"],
        gosb=row["gosb"],
        status=row["status"],
        object_type=row["object_type"],
        subtype=row["subtype"],
        object_name=row["object_name"],
        address=row["address"] if "address" in row.keys() else "",
        fill_total=float(row["fill_total"] or 0),
        fill_sections_json=row["fill_sections_json"] or "{}",
        errors_total=int(row["errors_total"] or 0),
        errors_sections_json=row["errors_sections_json"] or "{}",
        fill_project_docs=float(row["fill_project_docs"] or 0),
        docs_json=row["docs_json"] or "{}",
        has_photos=row["has_photos"] or "",
        imported_at=_parse_iso(row["imported_at"]) or datetime.now(timezone.utc),
    )


def _arsenal_system_from_row(row: sqlite3.Row) -> ArsenalSystemDbRow:
    year_raw = row["year"]
    present_raw = row["present"] if "present" in row.keys() else 1
    return ArsenalSystemDbRow(
        id=row["id"],
        passport_number=row["passport_number"],
        tb=row["tb"],
        gosb=row["gosb"],
        object_type=row["object_type"],
        subtype=row["subtype"],
        system_type=row["system_type"],
        manufacturer=row["manufacturer"] or "",
        year=int(year_raw) if year_raw is not None else None,
        present=bool(present_raw),
        imported_at=_parse_iso(row["imported_at"]) or datetime.now(timezone.utc),
    )


def _source_import_from_row(row: sqlite3.Row) -> SourceImportRow:
    return SourceImportRow(
        id=row["id"],
        source_key=row["source_key"],
        filename=row["filename"],
        imported_at=_parse_iso(row["imported_at"]) or datetime.now(timezone.utc),
        record_count=row["record_count"],
        status=row["status"],
        message=row["message"],
    )


def _category_history_from_row(row: sqlite3.Row) -> CategoryStatusHistoryRow:
    return CategoryStatusHistoryRow(
        id=row["id"],
        recorder_id=row["recorder_id"],
        category=row["category"],
        status=row["status"],
        reason=row["reason"],
        recorded_at=_parse_iso(row["recorded_at"]) or datetime.now(timezone.utc),
    )


def _problem_episode_start(
    rows: list[CategoryStatusHistoryRow],
) -> Optional[datetime]:
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


def _recorder_problem_episode_start(rows: list[HistoryRow]) -> Optional[datetime]:
    if not rows:
        return None
    latest = rows[-1]
    if latest.status not in _RECORDER_PROBLEM_STATUSES:
        return None
    start = latest.recorded_at
    for row in reversed(rows[:-1]):
        if row.status in _RECORDER_PROBLEM_STATUSES:
            start = row.recorded_at
        elif row.status in _TRANSPARENT_GAP_STATUSES:
            continue
        else:
            break
    return start
