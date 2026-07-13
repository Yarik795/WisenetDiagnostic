from __future__ import annotations

import sqlite3
from pathlib import Path

CHAT_TABLES = (
    "recorder_metrics",
    "channels",
    "status_history",
    "category_status_history",
    "recorder_poll_attempts",
    "naumen_records",
    "pp_requests",
    "source_imports",
)

SYSTEM_PROMPT_TEMPLATE = """Ты ассистент по системе мониторинга видеонаблюдения Hanwha Wisenet (NVR) и смежных систем.
У тебя есть read-only доступ к SQLite БД мониторинга через инструмент run_sql.

Схема БД (SQLite):
{schema}

Правила:
1. Для любых фактических данных используй run_sql (только SELECT). Не выдумывай цифры.
2. health_status: 'ok', 'warn', 'error', 'unknown'. Проблемные — warn и error.
3. device_online в recorder_metrics: 1 = online, 0 = offline.
4. Время в БД хранится как ISO-строки UTC (recorded_at, last_polled_at, imported_at).
5. recorder_id соответствует id регистратора в конфиге приложения (не путать с object_name).
6. Для больших выборок используй агрегации (COUNT, GROUP BY); не запрашивай все строки без LIMIT.
7. Если уместен график — сначала run_sql, затем make_chart с именами колонок из результата (минимум 2 шага LLM).
8. Отвечай на русском, кратко и по делу. SQL можно показать пользователю в ответе.
9. Не используй markdown-таблицы; предпочитай списки. Жирный текст — только **так**.
10. credentials и config.json недоступны — не запрашивай пароли и не выдумывай их.
"""


def build_schema_description(db_path: Path) -> str:
    lines: list[str] = []
    conn = sqlite3.connect(db_path, timeout=5)
    try:
        for table in CHAT_TABLES:
            info = conn.execute(f"PRAGMA table_info({table})").fetchall()
            if not info:
                continue
            cols = ", ".join(f"{row[1]} {row[2]}" for row in info)
            lines.append(f"- {table}({cols})")
    finally:
        conn.close()
    return "\n".join(lines) if lines else "(таблицы не найдены)"


def build_system_prompt(db_path: Path) -> str:
    schema = build_schema_description(db_path)
    return SYSTEM_PROMPT_TEMPLATE.format(schema=schema)
