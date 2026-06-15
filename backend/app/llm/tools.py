from __future__ import annotations

import json
from typing import Any, Optional

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "run_sql",
            "description": (
                "Выполнить read-only SELECT по SQLite БД мониторинга и вернуть строки."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Один SELECT-запрос SQLite",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "make_chart",
            "description": (
                "Построить график по данным из последнего run_sql. "
                "Укажи имена колонок из результата запроса."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "enum": ["bar", "line", "pie"],
                    },
                    "x": {
                        "type": "string",
                        "description": "Колонка для оси X или категорий (pie)",
                    },
                    "y": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Числовые колонки для серий данных",
                    },
                    "title": {"type": "string"},
                },
                "required": ["chart_type", "x", "y"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recorder_health",
            "description": "Получить текущие метрики и статус здоровья регистратора по recorder_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recorder_id": {
                        "type": "string",
                        "description": "ID регистратора из config.json",
                    }
                },
                "required": ["recorder_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "count_problems_by_kind",
            "description": (
                "Подсчитать регистраторы с проблемами (warn/error/offline) "
                "по видам систем: tsv, skud, bio, sots."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def build_echarts_option(
    args: dict[str, Any],
    table: Optional[dict[str, Any]],
) -> dict[str, Any]:
    if not table or not table.get("rows"):
        return {}

    rows = table["rows"]
    x_field = args.get("x", "")
    y_fields: list[str] = args.get("y") or []
    chart_type = args.get("chart_type", "bar")
    title = args.get("title", "")

    if chart_type == "pie" and y_fields:
        value_field = y_fields[0]
        data = [
            {"name": str(row.get(x_field, "")), "value": row.get(value_field)}
            for row in rows
        ]
        return {
            "title": {"text": title, "left": "center"},
            "tooltip": {"trigger": "item"},
            "series": [
                {
                    "name": title or value_field,
                    "type": "pie",
                    "radius": "60%",
                    "data": data,
                }
            ],
        }

    categories = [str(row.get(x_field, "")) for row in rows]
    series = [
        {
            "name": y,
            "type": chart_type,
            "data": [row.get(y) for row in rows],
        }
        for y in y_fields
    ]
    return {
        "title": {"text": title},
        "tooltip": {"trigger": "axis"},
        "legend": {"data": y_fields},
        "xAxis": {"type": "category", "data": categories},
        "yAxis": {"type": "value"},
        "series": series,
    }


def table_for_llm(
    columns: list[str],
    rows: list[dict[str, Any]],
    *,
    sample_rows: int,
    truncated: bool,
) -> str:
    payload = {
        "columns": columns,
        "rows": rows[:sample_rows],
        "row_count": len(rows),
        "truncated": truncated,
    }
    return json.dumps(payload, ensure_ascii=False, default=str)
