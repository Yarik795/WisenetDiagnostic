# Wisenet Диагностика — карта проекта для агента

Платформа мониторинга исправности видеонаблюдения Hanwha Wisenet (NVR) и смежных систем (СКУД, биотерминалы, СОТС). Версия 0.4.0 — «Дашборд руководителя ТСО».

Стек: Python 3.11, FastAPI + Jinja2 + HTMX, SQLite, опрос устройств по SUNAPI (HTTP CGI), ICMP ping для не-NVR устройств.

Запуск: `uvicorn app.main:app` из `backend/` (подробно — `docs/ЗАПУСК.md`). Тесты: `cd backend && pytest`.

## Маршрутизация задач

Сначала найди тип задачи в таблице и читай только указанные файлы. Не исследуй кодовую базу с нуля.

| Задача касается… | Смотри сначала | Подробности |
|---|---|---|
| Опрос NVR, SUNAPI-запросы, парсинг ответов | `backend/app/sunapi_extended.py`, `sunapi_parsing.py`, `sunapi.py` | `ai-docs/services.md` §SUNAPI |
| Правила здоровья, пороги, статусы | `backend/app/monitoring.py`, `health.py`, `models.py` (`MonitoringSettings`) | `ai-docs/services.md` §Оценка здоровья |
| Ping-доступность СКУД/биотерминалов | `backend/app/ping_check.py`, `device_kinds.py` | — |
| Страницы UI, HTMX, маршруты, формы | `backend/app/web/routes.py`, `web/validation.py`, `templates/`, `ui/*` | `ai-docs/basic-structure.md` §Веб-слой |
| Дашборды (сводка, по видам систем, время) | `backend/app/ui/summary_dashboard.py`, `kind_dashboard.py`, `health_dashboard.py`, `time_dashboard.py` | — |
| Схема БД, метрики, история статусов | `backend/app/state_store.py` | `ai-docs/monitoring-db.md` |
| Конфиг, реестр устройств, credentials, исключения | `backend/app/config_store.py`, `models.py`, `exclusions.py` | — |
| Email-сводка, SMTP, расписание рассылки | `backend/app/report_delivery.py`, `email_sender.py`, `report_delivery_history.py`, `ui/email_charts.py`, `ui/email_history_series.py` | `ai-docs/services.md` §Email |
| Отчёт «Статус оплаты», импорт Excel, экспорт/email | `backend/app/cashflow_report.py`, `pp_import.py`, `data_sources.py`, `report_jobs.py`, `ui/payments.py`, `ui/payments_export.py`, `ui/source_imports.py` | `ai-docs/monitoring-db.md` §pp_requests, §naumen_records |
| Отчёт «Анализ повторных РВР», период, XLSX/HTML/email, AI-проверка | `backend/app/rvr_repeat_report.py`, `rvr_ai_analysis.py`, `ui/rvr_repeat_dashboard.py`, `ui/rvr_repeat_export.py`, `state_store.py` | `ai-docs/monitoring-db.md` §pp_requests, §naumen_records, §rvr_ai_analysis |
| Импорт заявок ПП (файл с «заявки») | `backend/app/pp_import.py`, `data_sources.py`, `state_store.py` | `ai-docs/monitoring-db.md` §pp_requests |
| Импорт Naumen (`naumen_all.xlsx`) | `backend/app/naumen_import.py`, `data_sources.py`, `state_store.py` | `ai-docs/monitoring-db.md` §naumen_records |
| Отчёт «Регистраторы по времени», дата пр-ва NVR, drill-down по объектам | `backend/app/ui/equipment_timeline.py`, `ui/recorder_age_dashboard.py`, `ui/recorder_age_export.py` | `ai-docs/monitoring-db.md` §recorder_metrics (`manufacture_date`) |
| Отчёт «Диски по времени», наработка HDD, drill-down по объектам | `backend/app/ui/equipment_timeline.py`, `ui/disk_wear_dashboard.py`, `ui/disk_wear_export.py` | `ai-docs/monitoring-db.md` §recorder_metrics (`disks_json`) |
| Отчёт «Устройства на объекте», реальные NVR/камеры vs CMDB, ping зомби, HTML-экспорт/email | `backend/app/ui/site_inventory.py`, `ui/site_inventory_export.py`, `ping_jobs.py`, `state_store.py` | `ai-docs/monitoring-db.md` §channels, §recorder_metrics, §cmdb_records |
| Импорт АС Арсенал (файл с «паспортам») | `backend/app/arsenal_import.py`, `data_sources.py`, `state_store.py`, `ui/arsenal_dashboard.py`, `ui/arsenal_export.py` | `ai-docs/monitoring-db.md` §arsenal_* |
| Планировщик, фоновые задачи опроса | `backend/app/scheduler.py`, `poll_jobs.py` | — |
| Импорт из CMDB | `backend/app/cmdb_sync.py`, `cmdb_import.py`, `scripts/sync_config_from_cmdb.py`, `scripts/cmdb_reader.py` | `ai-docs/monitoring-db.md` §cmdb_records |
| Отчёт об ошибках (HTML-экспорт) | `backend/app/ui/error_report.py`, `error_report_render.py` | — |
| Аналитика устранённых инцидентов (HTML-отчёт) | `scripts/resolved_incidents_report.py`, `scripts/episode_parser.py` | `ai-docs/monitoring-db.md` §4–§5 (`status_history`, `category_status_history`) |
| Чат с AI, LLM, SQL-agent, история диалогов | `backend/app/llm/`, `chat_store.py`, `web/ai_chat.py` | `ai-docs/services.md` §Чат с AI |
| Бизнес-смысл, термины, scope этапов | — | `ai-docs/business-logic.md` |
| Структура проекта целиком | — | `ai-docs/basic-structure.md` |
| Запланированные функции, перспективы разработки | — | `ai-docs/roadmap.md` |

## Инварианты (не нарушать)

- Список устройств, credentials и пороги — только в `config.json` (через `ConfigStore`, атомарная запись); метрики, каналы и история — только в SQLite (`StateStore`). Не смешивать.
- SUNAPI-модули (`sunapi*.py`) — только транспорт и парсинг, без бизнес-правил. Правила здоровья — только в `monitoring.py`.
- UI-слой (`ui/`, `web/`, `templates/`) не обращается к устройствам напрямую — только через `monitoring` / `poll_jobs`.
- Даты для отображения конвертируются через `display_time.py` (Europe/Moscow по умолчанию), в БД и логике — UTC.

## Чего НЕ делать

- **Не обращаться к справочникам `docs/SUNAPI_*.md`, `docs/OpenPlatform_*.md` и `docs/nvr-samples/`, если в задаче нет явного указания их прочитать.** Это большие справочные документы по протоколу; для обычных задач достаточно кода в `sunapi*.py`. Если указание есть — искать нужный CGI через grep, не читать файл целиком.
- Не сканировать и не читать `backend/.venv/`, `.venv/`, `data/`, `logs/`, `inputData/`.
- Не редактировать `config.json` напрямую из кода — только через `ConfigStore`.

## Runtime-артефакты (в .gitignore)

- `data/monitoring.db` — SQLite (метрики, каналы, история)
- `data/report_delivery_history.json` — журнал email-отправок
- `data/uploads/`, `data/reports/` — загрузки и собранные отчёты
- `inputData/` — исходные Excel-файлы (CMDB, заявки, `naumen_all.xlsx`, выгрузка паспортов Арсенал)
- `logs/wisenet.log` — JSON-лог

## После изменений

Обнови документацию по правилу `.cursor/rules/maintain-docs.mdc`: структура модулей → `ai-docs/basic-structure.md` и таблица выше; контракты сервисов → `ai-docs/services.md`; схема БД → `ai-docs/monitoring-db.md`; бизнес-правила → `ai-docs/business-logic.md`.
