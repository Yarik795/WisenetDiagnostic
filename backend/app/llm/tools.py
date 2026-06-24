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

_PIE_MAX_SLICES = 10
_DATAZOOM_THRESHOLD = 12


def _table_columns(table: dict[str, Any]) -> list[str]:
    if table.get("columns"):
        return list(table["columns"])
    rows = table.get("rows") or []
    if rows:
        return list(rows[0].keys())
    return []


def _is_numeric(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _validate_chart_args(
    args: dict[str, Any],
    table: dict[str, Any],
) -> Optional[str]:
    columns = _table_columns(table)
    if not columns:
        return "нет колонок в таблице"

    x_field = args.get("x", "")
    y_fields: list[str] = args.get("y") or []
    if x_field not in columns:
        return f"колонка x={x_field!r} не найдена; доступны: {', '.join(columns)}"
    for y in y_fields:
        if y not in columns:
            return f"колонка y={y!r} не найдена; доступны: {', '.join(columns)}"

    rows = table.get("rows") or []
    has_value = False
    for row in rows:
        for y in y_fields:
            val = _to_float(row.get(y))
            if val is not None and val != 0:
                has_value = True
                break
        if has_value:
            break
    if not has_value:
        return "нет числовых значений в выбранных колонках y"
    return None


def _aggregate_pie_rows(
    rows: list[dict[str, Any]],
    x_field: str,
    value_field: str,
) -> list[dict[str, Any]]:
    if len(rows) <= _PIE_MAX_SLICES:
        return rows
    sorted_rows = sorted(
        rows,
        key=lambda r: _to_float(r.get(value_field)) or 0,
        reverse=True,
    )
    head = sorted_rows[: _PIE_MAX_SLICES - 1]
    tail = sorted_rows[_PIE_MAX_SLICES - 1 :]
    other_sum = sum(_to_float(r.get(value_field)) or 0 for r in tail)
    return head + [{"__pie_other__": True, x_field: "Прочие", value_field: other_sum}]


def build_echarts_option(
    args: dict[str, Any],
    table: Optional[dict[str, Any]],
) -> dict[str, Any]:
    if not table or not table.get("rows"):
        return {}

    err = _validate_chart_args(args, table)
    if err:
        return {}

    rows = list(table["rows"])
    x_field = args.get("x", "")
    y_fields: list[str] = args.get("y") or []
    chart_type = args.get("chart_type", "bar")
    title = args.get("title", "")

    if chart_type == "pie" and y_fields:
        value_field = y_fields[0]
        pie_rows = _aggregate_pie_rows(rows, x_field, value_field)
        data = [
            {
                "name": str(
                    row.get(x_field, "") if not row.get("__pie_other__") else "Прочие"
                ),
                "value": row.get(value_field),
            }
            for row in pie_rows
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
    option: dict[str, Any] = {
        "title": {"text": title},
        "tooltip": {"trigger": "axis"},
        "legend": {"data": y_fields},
        "xAxis": {
            "type": "category",
            "data": categories,
            "axisLabel": {"rotate": 35 if len(categories) > 6 else 0},
        },
        "yAxis": {"type": "value"},
        "series": series,
    }
    if len(categories) > _DATAZOOM_THRESHOLD:
        option["dataZoom"] = [
            {"type": "inside", "start": 0, "end": min(100, 100 * 12 / len(categories))},
            {"type": "slider", "start": 0, "end": min(100, 100 * 12 / len(categories))},
        ]
    return option


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
