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
| `.cursor/rules/` | Правила для ИИ-агента (поддержание документации) |
| `create-project-archive.ps1` | Создание ZIP-архива проекта (Windows) |

**Runtime-артефакты** (создаются при работе, в `.gitignore`):

- `data/monitoring.db` — SQLite с метриками каналов, историей опросов
- `data/report_delivery_history.json` — журнал отправок email-сводки
- `data/uploads/`, `data/reports/` — загруженные Excel-файлы и собранные отчёты
- `inputData/` — исходные данные (cmdb.xlsx, выгрузки заявок, `naumen_all.xlsx`)
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
| `sunapi_parsing.py` | Парсинг тел SUNAPI (key=value, индексированные поля, JSON, даты) |
| `ping_check.py` | ICMP ping для устройств СКУД и биотерминалов (без SUNAPI) |
| `monitoring.py` | Оценка здоровья каналов и регистраторов, сохранение результатов в БД, циклы `run_poll_cycle` / `run_inventory_cycle`, NTP fix |
| `health.py` | Перечисление `HealthStatus`, агрегация «худшего» статуса |
| `scheduler.py` | Фоновый asyncio-цикл: периодический короткий/полный опрос по интервалам из конфига, суточный inventory, тик плановой email-рассылки |
| `poll_jobs.py` | Менеджер фоновых задач опроса (ручной и по расписанию), статус для UI |
| `serial_manufacture_date.py` | Дата производства устройства по серийному номеру Samsung/Hanwha |

#### Отчёты и рассылка

| Модуль | Назначение |
|--------|------------|
| `report_delivery.py` | Плановая отправка email-сводки: расписание `email_report.send_time`, catchup, сборка письма |
| `report_delivery_history.py` | Журнал отправок (`data/report_delivery_history.json`): триггеры scheduled/catchup/manual |
| `email_sender.py` | SMTP-отправка письма (HTML-тело + вложение), настройки из `EmailReportSettings` |
| `cashflow_report.py` | Отчёт «Статус оплаты» из Excel-выгрузки заявок: разбор, JSON-артефакт `data/reports/cashflow_report.json` с `series` (сумма по месяцам × ответственный) для интерактивных графиков ECharts на `/payments` |
| `report_jobs.py` | Менеджер фоновых задач построения отчётов и импорта источников (прогресс для UI) |

#### Источники данных и CMDB

| Модуль | Назначение |
|--------|------------|
| `data_sources.py` | Единый реестр исходных файлов `inputData/` (CMDB, заявки, Naumen): спецификации, загрузка, импорт |
| `cmdb_sync.py` | Синхронизация устройств в `config.json` из `cmdb.xlsx` (с резервной копией конфига) |
| `naumen_import.py` | Импорт выгрузки Naumen (`naumen_all.xlsx`) в SQLite (`naumen_records`) |

#### Веб-слой (`backend/app/web/`)

| Модуль | Назначение |
|--------|------------|
| `routes.py` | HTML-страницы и HTMX-partials: сводка, мониторинг ТСВ, СКУД/био, источники, оплата, настройки, опрос, NTP, email-отчёты |
| `templates_env.py` | Jinja2Templates и регистрация глобальных функций форматирования для шаблонов |
| `validation.py` | Разбор и валидация форм регистраторов |

Основные маршруты UI: `/` → редирект на `/summary` (сводка по видам систем); `/monitoring` — ТСВ (дашборды исправности/времени, группы и таблица NVR); `/skud`, `/bio` — устройства СКУД и биотерминалы (ping); `/sources` — источники данных `inputData/`; `/payments` — отчёт «Статус оплаты»; `/settings`, `/settings/exclusions`. Legacy-редиректы: `/objects`, `/recorders`, `/time`, `/status`. Действия: `POST /monitoring/poll-all`, отмена/пауза автоопроса, проверка и NTP по регистратору, отправка email-сводки (`POST .../report/email`), `POST /objects/sync-cmdb`, экспорт отчёта об ошибках (`.../export/errors.html`).

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
| `source_imports.py` | Контекст страницы источников данных (импорты `inputData/`) |
| `helpers.py` | Имена, URL веб-интерфейса устройства, формат дат |

#### Шаблоны и статика

`backend/app/templates/` — Jinja2:

- `layout.html`, `base.html` — каркас страниц
- Страницы: `objects.html`, `recorders.html`, `monitoring.html`, `summary.html`, `kind_section.html`, `time.html`, `status.html`, `sources.html`, `payments.html`, `settings.html`, `settings_exclusions.html`, `placeholder_section.html`
- `partials/` — фрагменты для HTMX (дашборды, строки таблиц, формы, панель опроса)
- `exports/` — печатные/экспортные отчёты (отчёт об ошибках)

`backend/app/static/`:

- `css/app.css` — стили
- `js/app.js` — сворачивание групп, обновление дашбордов, взаимодействие с HTMX

---

## Скрипты (`scripts/`)

| Файл | Назначение |
|------|------------|
| `cmdb_reader.py` | Чтение `cmdb.xlsx`: фильтр по типу «Видеорегистраторы», слияние с существующими записями в конфиге |
| `sync_config_from_cmdb.py` | CLI: обновление списка `recorders` в `config.json` из CMDB с резервной копией |
| `cashflow.py` | CLI-сборка отчёта «Статус оплаты» из Excel-выгрузки |
| `send_test_email.py` | Проверка SMTP-настроек без UI |
| `dump_nvr_api_samples.py` | Дамп сырых ответов SUNAPI с реального NVR (для `docs/nvr-samples/`) |
| `dump_authfail_comparison.py` | Диагностика ошибок аутентификации на устройствах |
| `diagnose_problem_duration.py` | Диагностика длительности проблем по истории БД |
| `export_recorders_serial.py` | Выгрузка серийных номеров регистраторов |
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

web/routes.py → report_jobs → data_sources → cashflow_report / cmdb_sync
```

Версия API в `main.py`: 0.4.0; заголовок — «Дашборд руководителя ТСО».
