# Сервисы проекта Wisenet Диагностика

В проекте нет отдельного каталога `services/`: бизнес-логика сосредоточена в модулях `backend/app/`. Ниже — сервисный слой по зонам ответственности: что делает каждый модуль, какие данные принимает и возвращает, как вызывается из приложения.

Модули `backend/app/ui/` и `backend/app/web/` — представление и HTTP; в этом документе не описываются.

---

## Общая схема вызовов

1. **Планировщик** (`MonitoringScheduler`) или **ручной опрос** (`PollJobManager`) запускает цикл.
2. **Мониторинг** (`monitoring`) для каждого регистратора вызывает **SUNAPI** (`sunapi_extended.poll_recorder`).
3. Результат оценивается правилами здоровья и сохраняется: **StateStore** (метрики, каналы, история), **ConfigStore** (краткий статус доступности в `config.json`).
4. Быстрая проверка одного устройства без полного опроса — `sunapi.check_recorder` (только `deviceinfo`).

Переменные окружения: `CONFIG_PATH` (путь к `config.json`), `STATE_DB_PATH` (SQLite, по умолчанию `data/monitoring.db`).

---

## SUNAPI: транспорт и опрос устройств

### `sunapi.py` — базовая доступность

**Назначение:** минимальная проверка NVR по CGI `system.cgi?msubmenu=deviceinfo&action=view` (Digest-аутентификация, `httpx`, таймаут по умолчанию 15 с).

| Функция | Вход | Выход |
|---------|------|--------|
| `check_recorder(recorder, credentials, timeout=15.0)` | `Recorder`, `Credentials` | `SunapiCheckOutcome`: `status` (`CheckStatus`), `checked_at`, `error`, `device` (`DeviceInfo`) |
| `build_deviceinfo_url(recorder)` | `Recorder` | URL строка |
| `parse_deviceinfo_response(text)` | тело ответа | `DeviceInfo` (model, firmware_version, device_type, cgi_version) |

**Бизнес-логика:** отключённые регистраторы (`enabled=False`) → `DISABLED` без HTTP; пустые credentials → `OFFLINE` с текстом ошибки; успех — наличие `Model` или `DeviceType` в ответе. Используется для кнопки «проверить» без записи полных метрик в БД (через web/routes при необходимости с обновлением конфига).

### `sunapi_extended.py` — полный опрос и NTP

**Назначение:** последовательные HTTP-запросы к SUNAPI, парсинг, профиль возможностей по модели/CGI (`NvrApiProfile`).

**Главная точка входа:**

```text
poll_recorder(recorder, credentials, *, include_inventory=True, timeout=20.0) → RecorderPollData
```

| Поле `RecorderPollData` | Содержание |
|-------------------------|------------|
| `online`, `error`, `device` | доступность и deviceinfo |
| `channels`, `channels_polled` | список каналов (только при `include_inventory=True`) |
| `storage` | `StorageInfo`: диски, %, worst_status, температура (через diskutility при поддержке) |
| `date_time` | `DateTimeInfo`: local/utc, NTP, skew_seconds |
| `recording_period`, `channel_recording_periods` | глубина архива (глобально и по каналам) |
| `events`, `system_events` | `eventstatus.cgi` — VideoLoss, connected, системные флаги |

**Запросы при опросе (после успешного deviceinfo):**

- `include_inventory=True`: `media.cgi` — `cameraregister`, `videosource`; слияние каналов `merge_channels`.
- Всегда: `storageinfo`, `date`, `searchrecordingperiod`, `eventstatus` (action=check); при наличии каналов — периоды записи по каналам (`fetch_channel_recording_periods`, детализация архива зависит от `include_inventory`).

**NTP:**

```text
enable_recorder_ntp(recorder, credentials, ntp_server, *, posix_timezone, ...) → EnableNtpResult
```

Включает NTP на устройстве (`monitoring.ntp_server`, `ntp_posix_timezone` из конфига). При большом skew — запрос времени с NTP-сервера (UDP) и ручная установка через SUNAPI, затем повторное включение NTP. Успех: `success=True`, `SyncType=NTP` в `date_time`.

Вспомогательные экспорты для мониторинга: `normalize_register_status`, `is_register_status_error`, парсеры тел ответов (`parse_storage`, `parse_eventstatus`, …).

### `sunapi_parsing.py` — разбор тел SUNAPI

**Назначение:** общие парсеры без HTTP — key=value, индексированные поля (`Channel.0.Name`), JSON, даты. Используется `sunapi_extended` и тестами. Публичный API: `parse_key_value_body`, `parse_channel_indexed`, `parse_storage_indexed`, `try_parse_json`, `parse_datetime_local`.

---

## Оценка здоровья

### `health.py`

Перечисление `HealthStatus`: `ok`, `warn`, `error`, `unknown`. Функция `worst_status(*statuses)` — агрегация «худшего» статуса по шкале серьёзности. Словари `HEALTH_LABELS`, `HEALTH_SEVERITY` — для UI.

### `monitoring.py` — правила и циклы опроса

**Оценка канала** — `evaluate_channel_health(ch, event, settings) → (status: str, reason: str)`:

- `source_state`: deactive → unknown; off/covert → warn.
- События: `video_loss` → error; `connected=False` → error.
- `register_status`: ошибочные значения при `on` → error; иные не success/ok → warn.
- Активный канал с IP → ok.

**Оценка регистратора** — `evaluate_recorder_health(poll, channel_statuses, settings, archive_min/max) → (status, reason)`:

Пороги из `MonitoringSettings` в `config.json`: температура HDD, skew времени, глубина архива, системные события (через `ui.metrics_helpers.active_system_event_labels`), статус дисков, худший статус каналов.

**Сохранение результата опроса:**

```text
apply_poll_result(store, state, recorder, poll, settings, polled_at, *, update_config=True)
  → Optional[RecorderStatusUpdate]
```

- Обновляет каналы в SQLite (или только события по существующим каналам, если `channels_polled=False`).
- `upsert_recorder_metrics`, `record_history` для recorder и channel.
- При `update_config=True` — пакетное обновление `last_status` / `last_check_at` / `last_error`.

| Функция | Назначение |
|---------|------------|
| `poll_single_recorder(config_store, state_store, recorder, *, include_inventory=True, update_config=True)` | Один регистратор: `poll_recorder` + `apply_poll_result` |
| `run_poll_cycle(..., include_inventory=False, tracker=None)` | Все `enabled` регистраторы параллельно (`Semaphore` из `max_concurrent_polls`), батч-обновление статусов в конфиге |
| `run_inventory_cycle(...)` | То же с `include_inventory=True` (полный список каналов + детальный архив) |
| `run_ntp_fix_all(...)` | `NtpFixAllResult` — NTP на устройствах с кнопкой исправления в UI, затем короткий опрос |

`RecorderStatusUpdate`: `recorder_id`, `status` (`CheckStatus`), `checked_at`, `error`.

---

## Хранение данных

### `config_store.py` — `ConfigStore`

Файл `config.json` (потокобезопасное чтение/запись, атомарная замена через временный файл).

| Метод | Вход / выход |
|-------|----------------|
| `load()` | → `AppConfig` |
| `save(config)` | `AppConfig` → void |
| `list_recorders()` / `get_recorder(id)` | → `Recorder` |
| `create_recorder(RecorderCreate)` | → новый `Recorder` с id `nvr-{uuid8}` |
| `update_recorder` / `delete_recorder` | CRUD |
| `update_recorder_status` / `update_recorder_statuses` | список `RecorderStatusUpdate` |
| `get_credentials` / `update_credentials` | → `Credentials` |

В `Recorder` помимо полей устройства хранятся поля последней проверки: `last_status`, `last_check_at`, `last_error`.

### `state_store.py` — `StateStore`

SQLite: таблицы `channels`, `recorder_metrics`, `status_history`.

| Метод | Назначение |
|-------|------------|
| `init_db()` | создание схемы и миграции колонок |
| `upsert_channel` / `list_channels` / `get_channel` / `remove_channels_not_in` | каналы и здоровье |
| `upsert_recorder_metrics` / `get_recorder_metrics` / `list_recorder_metrics` | агрегат по NVR (`RecorderMetricsRow`) |
| `record_history` / `list_history` | история смены статуса (запись только при изменении status) |
| `delete_recorder_data` | очистка при удалении регистратора из конфига |

Типы строк: `ChannelRow`, `RecorderMetricsRow`, `HistoryRow` (dataclass). Диски и системные события в метриках — JSON в полях `disks_json`, `system_events_json`.

---

## Оркестрация опроса

### `poll_jobs.py` — `PollJobManager`

**Назначение:** единая блокировка цикла опроса (`asyncio.Lock`), фоновые задачи для UI, прогресс.

| Метод | Поведение |
|-------|-----------|
| `start_manual_poll(config_store, state_store, *, include_inventory, refresh_url)` | новый `PollJob` или возврат активного; `SHORT` / `INVENTORY` |
| `try_run_scheduled(..., include_inventory)` | для планировщика; `False` если цикл уже идёт |
| `get_job` / `get_active_job` | статус для HTMX-панели |

`PollJob`: `job_id`, `kind`, `status`, `total`/`done`/`success`/`failed`, `running_names`, `recent_results`, `percent`, `refresh_url`.

`PollJobTracker` передаётся в `run_poll_cycle` для обновления прогресса по регистраторам.

### `scheduler.py` — `MonitoringScheduler`

**Назначение:** фоновый asyncio-цикл с интервалом `monitoring.poll_interval_minutes`.

По умолчанию `_auto_paused=True`: плановый опрос не запускается, пока пользователь не включит **Автообновление** (`POST /monitoring/auto-poll/resume`). Пауза — `POST /monitoring/auto-poll/stop`. Состояние только в памяти процесса.

На каждом тике (если автообновление включено):

1. Раз в 24 ч — inventory (`include_inventory=True`).
2. Иначе — короткий опрос; полный inventory по каналам/архиву — если прошло `full_poll_interval_minutes` с последнего полного.

Рассылка email (`ReportDeliveryService.tick_sync`) выполняется и при паузе автоопроса.

Создаётся в `main.py` lifespan вместе с `PollJobManager`; останавливается при shutdown.

---

## Модели конфигурации (`models.py`)

Используются всеми сервисами (Pydantic):

- `Recorder`, `RecorderCreate`, `RecorderUpdate` — устройство в инвентаре.
- `Credentials`, `AppConfig`, `MonitoringSettings` — учётные данные и пороги мониторинга.
- `LLMSettings` — настройки чата с AI (`enabled`, `api_key`, `base_url`, `model`, лимиты SQL/итераций).
- `LLMSettings` — настройки чата с AI (`llm` в `config.json`: `enabled`, `api_key`, `base_url`, `model`, лимиты SQL/итераций).
- `CheckStatus` — online / offline / unknown / disabled (доступность в конфиге).
- `CheckResult`, `RecorderCheckResponse` — ответы API/UI для быстрой проверки.

Ключевые поля `MonitoringSettings`: интервалы опроса, `max_concurrent_polls`, пороги архива (`archive_days_required`, `archive_days_error_threshold`), времени (`time_skew_*`), температуры HDD, `ntp_server`, `ntp_posix_timezone`.

---

## Email-отчёты (`report_delivery.py`, `email_sender.py`)

Плановая рассылка: планировщик (`scheduler.py`) вызывает `ReportDeliveryService.tick_sync()` по `email_report.send_time` и `catchup_after_hours`. Настройки SMTP и получатели — секция `email_report` в `config.json` (см. `config.example.json`).

| Часть письма | Содержание |
|--------------|------------|
| Тело (HTML) | KPI, тренд за `email_trend_days` (по умолчанию 7) из `data/report_delivery_history.json`, изменения по категориям |
| Вложение | Тот же HTML, что `GET /objects/export/errors.html` — текущие проблемы |

Ручная отправка: кнопка с иконкой почты на странице **Объекты** → `POST /objects/report/email`, `trigger=manual`. Успешная ручная отправка **не блокирует** плановую в тот же день (учитываются только `scheduled` / `catchup`).

Отчёт **«Статус оплаты»** (`/payments`): «Экспорт в HTML» передаёт активную вкладку (Модернизация/РВР) и метрику графиков по разделам (`kind`, `m_<section>`). `GET /payments/export.html` — standalone HTML со встроенным CSS и inline-SVG. «Отправить на почту» (`POST /payments/report/email`) — одно письмо с **двумя** HTML-вложениями (Модернизация и РВР); метрики Модернизации берутся из UI (`m_<section>`), для РВР всегда **Количество**. Отправка через `send_report_email` на `email_report.to_emails` (в `report_delivery_history` не пишется).

Тест SMTP без UI: `python scripts/send_test_email.py`.

---

## Чат с AI (`llm/`, `chat_store.py`, `web/ai_chat.py`)

Интерактивный чат с LLM (OpenAI-совместимый API, по умолчанию `api.vsellm.ru`) для вопросов по данным `monitoring.db`. Настройки — секция `llm` в `config.json` (`LLMSettings`).

| Компонент | Роль |
|-----------|------|
| `LLMClient` | HTTP-клиент OpenAI SDK (`base_url`, `api_key`, `verify_ssl`) |
| `ChatOrchestrator` | Цикл function-calling: LLM вызывает инструменты, формирует ответ |
| `sql_guard` | Только `SELECT`/`WITH`, read-only подключение, `LIMIT`, без DDL/DML |
| `ChatStore` | Сессии и сообщения в SQLite (`chat_sessions`, `chat_messages`) |

**Инструменты LLM (function calling):**

| Имя | Назначение |
|-----|------------|
| `run_sql` | Read-only SELECT к `monitoring.db`; в LLM возвращается сэмпл строк (`llm_result_sample_rows`) |
| `make_chart` | Спецификация графика (bar/line/pie, колонки X/Y); сервер строит ECharts `option` |
| `get_recorder_health` | Метрики регистратора по `recorder_id` из `StateStore` |
| `count_problems_by_kind` | Проблемы по видам систем (tsv/skud/bio/sots) из конфига + метрик |

**Поток UI:** `POST /ai-chat/message` сохраняет реплику пользователя → `GET /ai-chat/stream` (SSE) запускает оркестратор → дельты текста и финальное событие `done` (текст, SQL, таблица, график) → `ChatStore.append_message` для ответа ассистента. Графики рисует ECharts на клиенте (`static/js/ai_chat.js`).

**Инварианты:** credentials и `config.json` в инструменты LLM не передаются; запись в БД мониторинга через чат невозможна.

---

## Скрипты вне runtime (`scripts/`)

### `cmdb_reader.py`

Чтение `cmdb.xlsx`: строки с функциональным типом «Видеорегистраторы».  
`parse_cmdb_grid(rows) → CmdbParseResult` с `CmdbRecorderRow` (`host`, `object_name`, `name`, `source_row`). Слияние с существующими записями конфига по IP — в `sync_config_from_cmdb.py`.

### `sync_config_from_cmdb.py`

CLI: обновление `recorders` в `config.json` из CMDB, резервная копия конфига. Использует `ConfigStore` и модели из `app`.

---

## Режимы опроса (краткая сводка)

| Режим | `include_inventory` | Каналы в БД | Типичный запуск |
|-------|---------------------|-------------|-----------------|
| Короткий | `False` | не перечитываются; обновляются события по известным каналам | планировщик, `poll-all` |
| Полный / inventory | `True` | полный список, периоды архива по каналам | раз в сутки, `inventory-all`, ручная инвентаризация |

После любого успешного опроса пересчитываются `recorder_metrics` и при необходимости `last_status` в конфиге.

---

## Зависимости между сервисами

```text
scheduler / poll_jobs
    → monitoring (run_poll_cycle, poll_single_recorder, run_ntp_fix_all)
        → sunapi_extended (poll_recorder, enable_recorder_ntp)
            → sunapi (deviceinfo), sunapi_parsing
        → health (worst_status)
        → config_store, state_store
        → ui.metrics_helpers (пороги событий, температура — только при оценке)
```

Для расширения логики мониторинга: правила — `monitoring.py` / `evaluate_*`; новые CGI — `sunapi_extended.py` + при необходимости парсеры в `sunapi_parsing.py`; персистентность — `state_store` / `config_store`; расписание и параллелизм — `scheduler` + `poll_jobs` + `MonitoringSettings.max_concurrent_polls`.
