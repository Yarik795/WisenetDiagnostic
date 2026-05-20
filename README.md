# Wisenet Диагностика

Платформа мониторинга исправности видеонаблюдения Wisenet (этап 0).

## Требования

- Python 3.11+

## Быстрый старт

Подробная инструкция (любая папка проекта, Windows/Linux): **[docs/ЗАПУСК.md](docs/ЗАПУСК.md)**

Кратко: из **корня проекта** — `config.json` → `uvicorn` на `:8000` → браузер [http://127.0.0.1:8000/objects](http://127.0.0.1:8000/objects).

## Тесты

```bash
cd backend
pytest
```

## Документация

- [Запуск проекта](docs/ЗАПУСК.md)
- [Бизнес-требования](docs/BUSINESS_REQUIREMENTS.md)
- [UI-требования](docs/UI_REQUIREMENTS.md)
