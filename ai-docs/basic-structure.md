# Базовая структура проекта Wisenet Диагностика

> Актуально на версию 0.4.0 («Дашборд руководителя ТСО»), июнь 2026.

Платформа мониторинга исправности видеонаблюдения Hanwha Wisenet (NVR) и смежных систем (СКУД, биотерминалы, СОТС). Backend на Python (FastAPI), веб-интерфейс — серверный рендеринг (Jinja2 + HTMX), опрос NVR по протоколу SUNAPI (HTTP CGI), прочие устройства — ICMP ping. Email-сводки и отчёт «Статус оплаты» из Excel-выгрузок.

---

## Корень репозитория

| Файл / каталог | Назначение |
|----------------|------------|
| `README.md` | Краткое описание проекта, ссылки на документацию |
| `AGENTS.md` | Карта проекта для ИИ-агента: маршрутизация задач, инварианты |
| `config.example.json` | Шаблон конфигурации: учётные данные, параметры мониторинга, список регистраторов |
| `config.json` | Рабочий конфиг (создаётся вручную; не коммитится при наличии секретов) |
| `backend/` | Приложение: API, логика опроса, UI |
| `scripts/` | Утилиты обслуживания и диагностики (CMDB, дампы SUNAPI, тест SMTP) |
| `docs/` | Требования, инструкция запуска, справочники SUNAPI/Open Platform |
| `ai-docs/` | Документация для разработки и ИИ-ассистентов |
| `ai-docs/deploy-linux.md` | Запуск на Linux без venv, systemd, ICMP ping |
| `ai-docs/roadmap.md` | Перспективы разработки: запланированные, но не реализованные функции |
| `.cursor/rules/` | Правила для ИИ-агента (поддержание документации) |
| `create-project-archive.ps1` | Создание ZIP-архива проекта (Windows) |

**Runtime-артефакты** (создаются при работе, в `.gitignore`):

- `data/monitoring.db` — SQLite с метриками каналов, историей опросов
- `data/report_delivery_history.json` — журнал отправок email-сводки
- `data/uploads/`, `data/reports/` — загруженные Excel-файлы и собранные отчёты
- `inputData/` — исходные Excel-файлы (CMDB, заявки, `naumen_all.xlsx`, выгрузка паспортов Арсенал)
- `logs/wisenet.log` — структурированный JSON-лог

Переменные окружения: `CONFIG_PATH` — путь к `config.json`; путь к БД задаётся в `StateStore` (по умолчанию `data/monitoring.db` от корня проекта).

---

## Backend (`backend/`)

Точка входа: `uvicorn app.main:app` из каталога `backend` (см. `docs/ЗАПУСК.md`).

| Файл | Назначение |
|------|------------|
| `requirements.txt` | Зависимости: FastAPI, uvicorn, pydantic, httpx, jinja2, openpyxl (для CMDB-скриптов) |
| `pytest.ini` | Настройки pytest |

### Пакет `backend/app/`

#### Ядро приложения

| Модуль | Назначение |
|--------|------------|
| `main.py` | FastAPI-приложение: lifespan (планировщик, менеджеры задач опроса и отчётов), HTTP-middleware логирования, монтирование `/static`, подключение веб-роутера |
| `models.py` | Pydantic-модели: `Recorder`, `AppConfig`, `MonitoringSettings`, `EmailReportSettings`, статусы проверки |
| `config_store.py` | Чтение/запись `config.json` с блокировкой и атомарной заменой файла; CRUD регистраторов и учётных данных |
| `state_store.py` | SQLite: каналы, агрегированные метрики регистраторов, история опросов, журнал попыток, импорты источников |
| `logging_config.py` | JSON-логи в `logs/wisenet.log`, фабрика `get_logger` |
| `display_time.py` | Отображаемый часовой пояс (по умолчанию Europe/Moscow), конвертация UTC → локальное для UI и писем |
| `device_kinds.py` | Виды систем устройств (`tsv`/`skud`/`bio`/`sots`), метки и определение вида по записи `Recorder` |
| `exclusions.py` | Исключения регистраторов из опроса и статистики (`config.exclusions`), фильтр `pollable_recorders` |

#### Опрос и мониторинг

| Модуль | Назначение |
|--------|------------|
| `sunapi.py` | Базовая проверка доступности: `deviceinfo` через HTTP, разбор ответа, `check_recorder` |
| `sunapi_extended.py` | Полный опрос NVR: каналы, диски, архив, NTP, события; `poll_recorder`, включение NTP |
| `config_backup.py` | Выгрузка конфигурации устройства через SUNAPI `configbackup` (binary GET, ZIP по объекту) |
| `sunapi_parsing.py` | Парсинг тел SUNAPI (key=value, индексированные поля, JSON, даты) |
| `ping_check.py` | ICMP ping для устройств СКУД и биотерминалов (без SUNAPI) |
| `monitoring.py` | Оценка здоровья каналов и регистраторов, сохранение результатов в БД, циклы `run_poll_cycle` / `run_inventory_cycle`, NTP fix |
| `health.py` | Перечисление `HealthStatus`, агрегация «худшего» статуса |
| `scheduler.py` | Фоновый asyncio-цикл: периодический короткий/полный опрос по интервалам из конфига, суточный inventory, тик плановой email-рассылки |
| `poll_jobs.py` | Менеджер фоновых задач опроса (ручной и по расписанию), статус для UI |
| `ping_jobs.py` | Фоновый ICMP-ping «зомби»-устройств (CMDB без опроса) для отчёта «Устройства на объекте», прогресс для UI |
| `serial_manufacture_date.py` | Дата производства устройства по серийному номеру Samsung/Hanwha |
| `dahua_cgi.py` | HTTP CGI Dahua (magicBox): vendor, S/N, firmware build |
| `onvif_deviceinfo.py` | ONVIF GetDeviceInformation для идентификации камеры |
| `hanwha_camera.py` | Прямой опрос камеры Hanwha/Samsung по SUNAPI deviceinfo |
| `camera_manufacturer_lookup.py` | Справочник производителя камеры по модели NVR; признак аналогового канала для отчёта «Камеры по времени» |
| `camera_inventory.py` | Оркестрация inventory-опроса IP-камер с каналов NVR |
| `camera_inventory_jobs.py` | Фоновый job inventory-опроса камер с прогрессом для UI |

#### Отчёты и рассылка

| Модуль | Назначение |
|--------|------------|
| `report_delivery.py` | Плановая отправка email-сводки: расписание `email_report.send_time`, catchup, сборка письма |
| `report_delivery_history.py` | Журнал отправок (`data/report_delivery_history.json`): триггеры scheduled/catchup/manual |
| `email_sender.py` | SMTP-отправка письма (HTML-тело + вложение), настройки из `EmailReportSettings` |
| `cashflow_report.py` | Отчёт «Статус оплаты» из Excel-выгрузки заявок: разбор, JSON-артефакт `data/reports/cashflow_report.json` с `series` (сумма по месяцам × ответственный) для интерактивных графиков ECharts на `/payments` |
| `rvr_repeat_report.py` | Отчёт «Анализ повторных РВР» из SQLite (`pp_requests` + `naumen_records`): фильтры, группировка по адресу и виду систем, пороги ≥2/≥3 |
| `rvr_ai_analysis.py` | AI-проверка повторных РВР через VseLLM: батчинг, парсинг JSON, fingerprint заявок, кэш в `rvr_ai_analysis` |
| `pp_import.py` | Импорт выгрузки заявок ПП (файл с «заявки» в имени) в SQLite (`pp_requests`) |
| `report_jobs.py` | Менеджер фоновых задач построения отчётов и импорта источников (прогресс для UI) |

#### Чат с AI (`backend/app/llm/`, `chat_store.py`)

| Модуль | Назначение |
|--------|------------|
| `llm/client.py` | OpenAI-совместимый клиент к `api.vsellm.ru` (настройки из `config.json` → `LLMSettings`) |
| `llm/sql_guard.py` | Валидатор read-only SQL и выполнение SELECT к `monitoring.db` |
| `llm/schema_context.py` | Системный промпт и динамическое описание схемы БД (`PRAGMA table_info`) |
| `llm/tools.py` | Function-calling: `run_sql`, `make_chart`, typed-инструменты; сборка ECharts option |
| `llm/orchestrator.py` | Цикл tool calling, SSE-стриминг финального текста |
| `chat_store.py` | История чата: `chat_sessions`, `chat_messages`; `list_sessions_with_messages`, `get_latest_session`, `delete_empty_sessions` |
| `web/ai_chat.py` | `/ai-chat` (redirect на последнюю сессию), `/ai-chat/message`, `/ai-chat/stream?message_id=…`, `/ai-chat/session` |

#### Источники данных и CMDB

| Модуль | Назначение |
|--------|------------|
| `data_sources.py` | Единый реестр исходных файлов `inputData/` (CMDB, заявки, Naumen, Арсенал): спецификации, загрузка, импорт |
| `cmdb_sync.py` | Синхронизация устройств в `config.json` из `cmdb.xlsx` (с резервной копией конфига) |
| `cmdb_import.py` | Импорт выгрузки CMDB в SQLite `cmdb_records` (полная замена при загрузке) |
| `naumen_import.py` | Импорт выгрузки Naumen (`naumen_all.xlsx`) в SQLite (`naumen_records`) |
| `arsenal_import.py` | Импорт выгрузки АС Арсенал (листы «Аналитика», «Общая информация», системные) в SQLite |

#### Веб-слой (`backend/app/web/`)

| Модуль | Назначение |
|--------|------------|
| `routes.py` | HTML-страницы и HTMX-partials: сводка, мониторинг ТСВ, СКУД/био, источники, оплата, настройки, опрос, NTP, email-отчёты |
| `ai_chat.py` | Страница `/ai-chat`: сообщения, SSE-стриминг ответа LLM, сессии диалога |
| `templates_env.py` | Jinja2Templates и регистрация глобальных функций форматирования для шаблонов |
| `validation.py` | Разбор и валидация форм регистраторов |

Основные маршруты UI: `/` → редирект на `/summary` (сводка по видам систем); `/monitoring` — ТСВ (дашборды исправности/времени, группы и таблица NVR); `/skud`, `/bio` — устройства СКУД и биотерминалы (ping); `/sources` — источники данных `inputData/`; `/arsenal` — дашборд АС Арсенал (заполнение паспортов, производители систем; `GET /arsenal/export.html`, `POST /arsenal/report/email`); `/recorders-age` — распределение NVR по дате производства (`GET /recorders-age/export.html`); `/disks-wear` — распределение HDD по наработке (`GET /disks-wear/export.html`); `/site-devices` — отчёт «Устройства на объекте»: реальные NVR/камеры vs CMDB, `POST /site-devices/ping-zombies` (`GET /site-devices/export.html`, `POST /site-devices/report/email`); `/payments` — отчёт «Статус оплаты» (`GET /payments/export.html`, `POST /payments/report/email`); `/rvr-repeat` — отчёт «Анализ повторных РВР» (`GET /rvr-repeat/export.xlsx`, `POST /rvr-repeat/report/email`); `/ai-chat` — чат с LLM по данным мониторинга (SSE, ECharts); `/settings`, `/settings/exclusions`. Legacy-редиректы: `/objects`, `/recorders`, `/time`, `/status`. Действия: `POST /monitoring/poll-all`, отмена/пауза автоопроса, проверка и NTP по регистратору, отправка email-сводки (`POST .../report/email`), `POST /objects/sync-cmdb`, экспорт отчёта об ошибках (`.../export/errors.html`).

#### Логика представления (`backend/app/ui/`)

Модули без HTTP — подготовка контекста для шаблонов и классификация проблем:

| Модуль | Назначение |
|--------|------------|
| `dependencies.py` | FastAPI Depends: синглтоны `ConfigStore`, `StateStore`, `PollJobManager`, `ReportJobManager` |
| `grouping.py` | Группировка регистраторов по `object_name`, сортировка, подсчёт проблем |
| `health_classifiers.py` | Категории здоровья (температура, диски, каналы, архив, время) |
| `health_dashboard.py` | Контекст дашборда исправности по категориям |
| `summary_dashboard.py` | Контекст сводной страницы `/summary`: агрегаты по видам систем |
| `kind_dashboard.py` | Дашборд по виду системы (ТСВ / СКУД / биотерминалы / СОТС) |
| `time_dashboard.py` | Контекст дашборда синхронизации времени / NTP |
| `metrics_helpers.py` | Форматирование метрик (диски, архив, skew, события) |
| `error_report.py` | Сводный отчёт об ошибках (данные) |
| `error_report_render.py` | Рендер HTML-отчёта об ошибках (экспорт и вложение письма) |
| `email_history_series.py` | Ряды данных по дням для трендов email-сводки |
| `email_charts.py` | SVG-графики/спарклайны для тела письма |
| `payments.py` | Контекст страницы отчёта «Статус оплаты» |
| `payments_export.py` | Статичный HTML-экспорт и тело письма отчёта «Статус оплаты» (inline-SVG графики) |
| `rvr_repeat_dashboard.py` | Контекст страницы «Анализ повторных РВР»: период, KPI, матрица объект×вид системы, раскрытие заявок по клику |
| `rvr_repeat_export.py` | XLSX/HTML-экспорт и тело письма отчёта «Анализ повторных РВР» (листы Данные/Сводка/Сводка 3; standalone HTML с раскрытием заявок) |
| `source_imports.py` | Контекст страницы источников данных (импорты `inputData/`) |
| `arsenal_dashboard.py` | Дашборд АС Арсенал: KPI, ECharts, drill-down и карточка паспорта |
| `arsenal_export.py` | HTML-экспорт и email текущей выборки дашборда Арсенал (inline SVG) |
| `equipment_timeline.py` | Общая агрегация для отчётов «по времени»: дата пр-ва NVR, наработка HDD, drill-down по `object_name` |
| `recorder_age_dashboard.py` | Дашборд «Регистраторы по времени»: распределение NVR по `manufacture_date`, ECharts, drill-down |
| `recorder_age_export.py` | HTML-экспорт отчёта «Регистраторы по времени» (inline SVG + таблицы объектов) |
| `recorder_inventory.py` | Отчёт «Инвентарь регистраторов»: объект, модель, MAC, серийный номер (config + `recorder_metrics`) |
| `recorder_inventory_export.py` | HTML-экспорт и email отчёта «Инвентарь регистраторов» |
| `camera_age_dashboard.py` | Дашборд «Камеры по времени»: распределение IP-камер, inventory job, drill-down |
| `camera_age_export.py` | HTML-экспорт и email отчёта «Камеры по времени» |
| `disk_wear_dashboard.py` | Дашборд «Диски по времени»: распределение HDD по `PowerOnDuration`, ECharts, drill-down |
| `disk_wear_export.py` | HTML-экспорт отчёта «Диски по времени» (inline SVG + таблицы объектов) |
| `site_inventory.py` | Отчёт «Устройства на объекте»: реальные NVR/камеры из опроса, сопоставление с CMDB, аналоговые камеры, вспомогательное оборудование, статусы ping зомби |
| `site_inventory_export.py` | HTML-экспорт и email отчёта «Устройства на объекте» для выдачи инженеру |
| `device_configs.py` | Отчёт «Конфигурации NVR/SPD»: группировка по объектам, NVR из config, SPD из CMDB, ссылки на скачивание |
| `helpers.py` | Имена, URL веб-интерфейса устройства, формат дат |

#### Шаблоны и статика

`backend/app/templates/` — Jinja2:

- `layout.html`, `base.html` — каркас страниц
- Страницы: `objects.html`, `recorders.html`, `monitoring.html`, `summary.html`, `kind_section.html`, `time.html`, `status.html`, `sources.html`, `arsenal.html`, `recorder_age.html`, `recorder_inventory.html`, `camera_age.html`, `disk_wear.html`, `site_devices.html`, `device_configs.html`, `payments.html`, `rvr_repeat.html`, `ai_chat.html`, `settings.html`, `settings_exclusions.html`, `placeholder_section.html`
- `partials/` — фрагменты для HTMX (дашборды, строки таблиц, формы, панель опроса)
- `exports/` — печатные/экспортные отчёты (ошибки, оплата, Арсенал, регистраторы/диски по времени, инвентарь регистраторов, повторные РВР)

`backend/app/static/`:

- `css/app.css` — стили
- `js/app.js` — сворачивание групп, обновление дашбордов, взаимодействие с HTMX
- `js/ai_chat.js` — SSE по `message_id`, markdown, ECharts, retry, адаптивная вёрстка

---

## Скрипты (`scripts/`)

| Файл | Назначение |
|------|------------|
| `cmdb_reader.py` | Чтение `cmdb.xlsx`: фильтр по функциональным типам и производителям, слияние с существующими записями в конфиге |
| `sync_config_from_cmdb.py` | CLI: обновление списка `recorders` в `config.json` из CMDB с резервной копией |
| `cashflow.py` | CLI-сборка отчёта «Статус оплаты» из Excel-выгрузки |
| `send_test_email.py` | Проверка SMTP-настроек без UI |
| `dump_nvr_api_samples.py` | Дамп сырых ответов SUNAPI с реального NVR (для `docs/nvr-samples/`) |
| `dump_authfail_comparison.py` | Диагностика ошибок аутентификации на устройствах |
| `diagnose_problem_duration.py` | Диагностика длительности проблем по истории БД |
| `episode_parser.py` | Парсинг завершённых эпизодов warn/error → ok (общая логика для отчётов) |
| `event_type_groups.py` | Нормализация длинных причин в группы для фильтра HTML-отчёта |
| `resolved_incidents_report.py` | HTML-отчёт по устранённым инцидентам: выборка из `status_history` и `category_status_history`, Chart.js-графики |
| `export_recorders_serial.py` | Выгрузка серийных номеров регистраторов |
| `db_profile_export.py` | Профилирование `monitoring.db`: статистика столбцов, распределения, примеры строк (JSON/CSV для генерации тестовой БД) |
| `db_profile_import.py` | Создание тестовой `monitoring.db` из JSON-профиля; опционально `--sync-config` |
| `cleanup_empty_chat_sessions.py` | Удаление пустых сессий чата AI из `chat_sessions` |
| `probe_nvr_manufacture_date.py` | Проверка определения даты производства по серийнику |

Запуск из корня проекта; скрипты добавляют `backend` и `scripts` в `sys.path` и используют `app.config_store` / `app.models`.

---

## Документация (`docs/`)

Не является исполняемым кодом. Ключевые файлы для понимания продукта:

- `ЗАПУСК.md` — установка, конфиг, uvicorn
- `BUSINESS_REQUIREMENTS.md`, `UI_REQUIREMENTS.md` — требования
- `SUNAPI_*.md`, `OpenPlatform_*.md` — справочники API устройств

---

## Поток данных (кратко)

1. **Конфиг** (`config.json`) — список регистраторов, общие credentials, пороги мониторинга.
2. **Планировщик** / ручной опрос → `poll_jobs` → `monitoring.run_poll_cycle` → `sunapi_extended.poll_recorder`.
3. **Результаты** → `monitoring.apply_poll_result` → SQLite (`state_store`) + обновление `last_status` в конфиге (`config_store`).
4. **UI** читает конфиг и БД через `routes.py`, строит контекст в `ui/*`, отдаёт HTML/partials.

Разделение ответственности: SUNAPI — транспорт и парсинг; `monitoring` — бизнес-правила здоровья; `ui` — представление; `web` — HTTP и формы; хранение — `config_store` (персистентный список устройств) и `state_store` (оперативные метрики и история).

---

## Зависимости между слоями

```
main.py
  ├── config_store, state_store, poll_jobs, scheduler
  └── web/routes.py
        ├── monitoring, sunapi_extended
        └── ui/* + templates + static

monitoring.py
  ├── sunapi / sunapi_extended
  ├── health.py
  ├── config_store, state_store
  └── ui.metrics_helpers (пороги событий, температура дисков)

scheduler.py → poll_jobs → monitoring
scheduler.py → report_delivery → email_sender + report_delivery_history
                                  + ui.error_report_render, ui.email_charts (содержимое письма)

web/routes.py → report_jobs → data_sources → cashflow_report / cmdb_import / cmdb_sync
```

Версия API в `main.py`: 0.4.0; заголовок — «Дашборд руководителя ТСО».
