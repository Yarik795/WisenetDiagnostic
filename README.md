# Wisenet Диагностика

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)](https://sqlite.org/)
[![Demo](https://img.shields.io/badge/Demo-GitHub%20Pages-orange.svg)](https://yarik795.github.io/WisenetDiagnostic/)

Платформа мониторинга исправности видеонаблюдения Hanwha Wisenet (NVR) и смежных систем (СКУД, биотерминалы, СОТС).

**[Демо-лендинг](https://yarik795.github.io/WisenetDiagnostic/)** · Версия 0.4.0

## Возможности

- Автоматический опрос NVR по SUNAPI (HTTP CGI) и ping-доступность СКУД/биотерминалов
- Сводные дашборды с категориями «светофора» по объектам
- Импорт данных из CMDB, Naumen, Портала Поставщика, АС Арсенал
- Отчёты: статус оплаты, повторные РВР, инвентаризация, возраст оборудования
- LLM-модули: анализ повторных заявок, SQL-agent для запросов на естественном языке
- Email-рассылка сводок и HTML/XLSX-экспорт

## Стек

Python 3.11 · FastAPI · Jinja2 · HTMX · SQLite · OpenRouter LLM

## Быстрый старт

1. Скопируйте `config.example.json` в `config.json` и заполните список устройств.
2. Установите зависимости и запустите сервер из каталога `backend`:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

3. Откройте [http://127.0.0.1:8000/objects](http://127.0.0.1:8000/objects).

## Документация

Подробная документация для разработки — в каталоге `ai-docs/`.

## Тесты

```bash
cd backend
pytest
```
