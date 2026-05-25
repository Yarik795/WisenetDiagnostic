# Базовая структура проекта Wisenet Диагностика

Платформа мониторинга исправности видеонаблюдения Hanwha Wisenet (NVR). Backend на Python (FastAPI), веб-интерфейс — серверный рендеринг (Jinja2 + HTMX), опрос устройств по протоколу SUNAPI (HTTP CGI).

---

## Корень репозитория

| Файл / каталог | Назначение |
|----------------|------------|
| `README.md` | Краткое описание проекта, ссылки на документацию |
| `config.example.json` | Шаблон конфигурации: учётные данные, параметры мониторинга, список регистраторов |
| `config.json` | Рабочий конфиг (создаётся вручную; не коммитится при наличии секретов) |
| `backend/` | Приложение: API, логика опроса, UI |
| `scripts/` | Утилиты обслуживания (импорт из CMDB) |
| `docs/` | Требования, инструкция запуска, справочники SUNAPI/Open Platform |
| `ai-docs/` | Документация для разработки и ИИ-ассистентов |
| `create-project-archive.ps1` | Создание ZIP-архива проекта (Windows) |

**Runtime-артефакты** (создаются при работе, в `.gitignore`):

- `data/monitoring.db` — SQLite с метриками каналов, историей опросов
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
| `main.py` | FastAPI-приложение: lifespan (планировщик, менеджер задач опроса), HTTP-middleware логирования, монтирование `/static`, подключение веб-роутера |
| `models.py` | Pydantic-модели: `Recorder`, `AppConfig`, `MonitoringSettings`, статусы проверки |
| `config_store.py` | Чтение/запись `config.json` с блокировкой и атомарной заменой файла; CRUD регистраторов и учётных данных |
| `state_store.py` | SQLite: каналы, агрегированные метрики регистраторов, история опросов |
| `logging_config.py` | JSON-логи в `logs/wisenet.log`, фабрика `get_logger` |

#### Опрос и мониторинг

| Модуль | Назначение |
|--------|------------|
| `sunapi.py` | Базовая проверка доступности: `deviceinfo` через HTTP, разбор ответа, `check_recorder` |
| `sunapi_extended.py` | Полный опрос NVR: каналы, диски, архив, NTP, события; `poll_recorder`, включение NTP |
| `sunapi_parsing.py` | Парсинг тел SUNAPI (key=value, индексированные поля, JSON, даты) |
| `monitoring.py` | Оценка здоровья каналов и регистраторов, сохранение результатов в БД, циклы `run_poll_cycle` / `run_inventory_cycle`, NTP fix |
| `health.py` | Перечисление `HealthStatus`, агрегация «худшего» статуса |
| `scheduler.py` | Фоновый asyncio-цикл: периодический короткий/полный опрос по интервалам из конфига, суточный inventory |
| `poll_jobs.py` | Менеджер фоновых задач опроса (ручной и по расписанию), статус для UI |

#### Веб-слой (`backend/app/web/`)

| Модуль | Назначение |
|--------|------------|
| `routes.py` | HTML-страницы и HTMX-partials: объекты, регистраторы, каналы, время, статус, настройки, опрос, NTP |
| `templates_env.py` | Jinja2Templates и регистрация глобальных функций форматирования для шаблонов |
| `validation.py` | Разбор и валидация форм регистраторов |

Основные маршруты UI: `/objects` (группы или `?view=table`), `/status` (сводка дашбордов), `/channels`, `/history`, `/settings`; редиректы `/recorders` → `/objects?view=table`, `/time` → `/status?category=time`; действия — `POST /monitoring/poll-all`, `inventory-all`, `ntp-fix-all`, проверка и NTP по одному регистратору.

#### Логика представления (`backend/app/ui/`)

Модули без HTTP — подготовка контекста для шаблонов и классификация проблем:

| Модуль | Назначение |
|--------|------------|
| `dependencies.py` | FastAPI Depends: синглтоны `ConfigStore`, `StateStore`, `PollJobManager` |
| `grouping.py` | Группировка регистраторов по `object_name`, сортировка, подсчёт проблем |
| `health_classifiers.py` | Категории здоровья (температура, диски, каналы, архив, время) |
| `health_dashboard.py` | Контекст дашборда исправности по категориям |
| `time_dashboard.py` | Контекст дашборда синхронизации времени / NTP |
| `metrics_helpers.py` | Форматирование метрик (диски, архив, skew, события) |
| `error_report.py` | Сводный отчёт об ошибках для экспорта HTML |
| `helpers.py` | Имена, URL веб-интерфейса устройства, формат дат |

#### Шаблоны и статика

`backend/app/templates/` — Jinja2:

- `layout.html`, `base.html` — каркас страниц
- Страницы: `objects.html`, `recorders.html`, `channels.html`, `time.html`, `status.html`, `settings.html`, `history.html`
- `partials/` — фрагменты для HTMX (дашборды, строки таблиц, формы, панель опроса)
- `exports/error_report.html` — печатный/экспортный отчёт

`backend/app/static/`:

- `css/app.css` — стили
- `js/app.js` — сворачивание групп, обновление дашбордов, взаимодействие с HTMX

---

## Скрипты (`scripts/`)

| Файл | Назначение |
|------|------------|
| `cmdb_reader.py` | Чтение `cmdb.xlsx`: фильтр по типу «Видеорегистраторы», слияние с существующими записями в конфиге |
| `sync_config_from_cmdb.py` | CLI: обновление списка `recorders` в `config.json` из CMDB с резервной копией |

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
```

Версия API в `main.py`: 0.3.0; описание этапа — мониторинг регистраторов и каналов по SUNAPI.
