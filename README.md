# Wisenet Диагностика

Платформа мониторинга исправности видеонаблюдения Wisenet (этап 0).

## Требования

- Python 3.11+

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

Подробная документация для разработки — в каталоге `ai-docs/`. Локальные справочники SUNAPI и утилиты — в `docs/` и `scripts/` (не публикуются в репозитории).

## Тесты

```bash
cd backend
pytest
```
