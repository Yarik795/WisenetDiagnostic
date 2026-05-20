# Wisenet Диагностика

Платформа мониторинга исправности видеонаблюдения Wisenet (этап 0).

## Требования

- Python 3.11+
- Node.js 20+

## Быстрый старт

Подробная инструкция (любая папка проекта, Windows/Linux): **[docs/ЗАПУСК.md](docs/ЗАПУСК.md)**

Кратко: из **корня проекта** — `config.json` → backend на `:8000` → frontend на `:5173`.

## Тесты

```bash
cd backend
pytest
cd ../frontend
npm test
```

## Документация

- [Запуск проекта](docs/ЗАПУСК.md)
- [Бизнес-требования](docs/BUSINESS_REQUIREMENTS.md)
- [UI-требования](docs/UI_REQUIREMENTS.md)
