from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator, Optional

from ..config_store import ConfigStore
from ..device_kinds import ALL_DEVICE_KINDS, SYSTEM_KIND_LABELS, recorder_device_kind
from ..exclusions import excluded_ids_set
from ..models import LLMSettings
from ..state_store import DEFAULT_DB_PATH, StateStore
from .client import LLMClient
from .schema_context import build_system_prompt
from .sql_guard import run_readonly
from .tools import TOOLS, build_echarts_option, table_for_llm


@dataclass
class ChatResult:
    text: str = ""
    sql: Optional[str] = None
    table: Optional[dict[str, Any]] = None
    chart_option: Optional[dict[str, Any]] = None
    tool_calls_log: list[str] = field(default_factory=list)


def _chunk_text(text: str, size: int = 24) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)] or [""]


class ChatOrchestrator:
    def __init__(
        self,
        *,
        state_store: Optional[StateStore] = None,
        config_store: Optional[ConfigStore] = None,
        db_path: Optional[Path] = None,
        settings: Optional[LLMSettings] = None,
    ) -> None:
        self.state_store = state_store or StateStore()
        self.config_store = config_store or ConfigStore()
        self.db_path = db_path or self.state_store.path or DEFAULT_DB_PATH
        self.settings = settings or self.config_store.load().llm
        self.llm = LLMClient(self.settings)

    def _execute_tool(
        self,
        name: str,
        args: dict[str, Any],
        *,
        last_table: Optional[dict[str, Any]],
    ) -> tuple[str, Optional[dict[str, Any]], Optional[dict[str, Any]], Optional[str]]:
        if name == "run_sql":
            query = args.get("query", "")
            columns, rows, row_count, truncated = run_readonly(
                self.db_path,
                query,
                max_rows=self.settings.max_rows,
            )
            table = {
                "columns": columns,
                "rows": rows,
                "row_count": row_count,
                "truncated": truncated,
            }
            return (
                table_for_llm(
                    columns,
                    rows,
                    sample_rows=self.settings.llm_result_sample_rows,
                    truncated=truncated,
                ),
                table,
                None,
                query,
            )

        if name == "make_chart":
            if not last_table:
                return (
                    "Нет данных для графика. Сначала выполни run_sql.",
                    None,
                    None,
                    None,
                )
            option = build_echarts_option(args, last_table)
            if not option:
                return (
                    "Не удалось построить график: проверь имена колонок.",
                    None,
                    None,
                    None,
                )
            return (
                json.dumps({"status": "chart_ready"}, ensure_ascii=False),
                None,
                option,
                None,
            )

        if name == "get_recorder_health":
            recorder_id = args.get("recorder_id", "")
            metrics = self.state_store.get_recorder_metrics(recorder_id)
            if metrics is None:
                return (
                    json.dumps(
                        {"error": f"Регистратор {recorder_id!r} не найден в БД"},
                        ensure_ascii=False,
                    ),
                    None,
                    None,
                    None,
                )
            data = {
                "recorder_id": metrics.recorder_id,
                "model": metrics.model,
                "device_online": metrics.device_online,
                "health_status": metrics.health_status,
                "health_reason": metrics.health_reason,
                "ntp_status": metrics.ntp_status,
                "time_skew_seconds": metrics.time_skew_seconds,
                "storage_used_percent": metrics.storage_used_percent,
                "archive_days": metrics.archive_days,
                "channel_count": metrics.channel_count,
                "channels_ok": metrics.channels_ok,
                "channels_warn": metrics.channels_warn,
                "channels_error": metrics.channels_error,
                "last_polled_at": (
                    metrics.last_polled_at.isoformat()
                    if metrics.last_polled_at
                    else None
                ),
            }
            return json.dumps(data, ensure_ascii=False, default=str), None, None, None

        if name == "count_problems_by_kind":
            config = self.config_store.load()
            excluded = excluded_ids_set(config)
            metrics_by_id = {
                m.recorder_id: m for m in self.state_store.list_recorder_metrics()
            }
            result: dict[str, dict[str, int | str]] = {}
            for kind in ALL_DEVICE_KINDS:
                total = 0
                problems = 0
                for rec in config.recorders:
                    if rec.id in excluded:
                        continue
                    if recorder_device_kind(rec) != kind:
                        continue
                    total += 1
                    m = metrics_by_id.get(rec.id)
                    if m is None:
                        continue
                    if not m.device_online or m.health_status in ("warn", "error"):
                        problems += 1
                result[kind] = {
                    "label": SYSTEM_KIND_LABELS[kind],
                    "total": total,
                    "problems": problems,
                }
            return json.dumps(result, ensure_ascii=False), None, None, None

        return (
            json.dumps({"error": f"Неизвестный инструмент: {name}"}),
            None,
            None,
            None,
        )

    def _build_messages(
        self,
        history: list[dict[str, str]],
        user_text: str,
    ) -> list[dict[str, Any]]:
        system_prompt = build_system_prompt(self.db_path)
        return [
            {"role": "system", "content": system_prompt},
            *[{"role": m["role"], "content": m["content"]} for m in history],
            {"role": "user", "content": user_text},
        ]

    def _config_error(self) -> Optional[ChatResult]:
        if not self.settings.enabled:
            return ChatResult(
                text="Чат с AI отключён в настройках (llm.enabled = false)."
            )
        if not self.settings.api_key:
            return ChatResult(
                text="Не задан API-ключ LLM. Укажите llm.api_key в config.json."
            )
        return None

    def _run_loop(
        self,
        messages: list[dict[str, Any]],
        *,
        on_tool: Optional[Any] = None,
    ) -> ChatResult:
        result = ChatResult()
        last_table: Optional[dict[str, Any]] = None

        for _ in range(self.settings.max_iterations):
            response = self.llm.chat(messages, tools=TOOLS, stream=False)
            msg = response.choices[0].message

            if not msg.tool_calls:
                result.text = msg.content or ""
                result.table = last_table
                return result

            messages.append(msg.model_dump(exclude_none=True))

            for call in msg.tool_calls:
                fn = call.function
                tool_name = fn.name
                if on_tool:
                    on_tool(tool_name)
                result.tool_calls_log.append(tool_name)
                try:
                    tool_args = json.loads(fn.arguments or "{}")
                except json.JSONDecodeError:
                    tool_args = {}

                tool_result, table, chart, sql = self._execute_tool(
                    tool_name,
                    tool_args,
                    last_table=last_table,
                )
                if table is not None:
                    last_table = table
                    result.table = table
                if chart is not None:
                    result.chart_option = chart
                if sql:
                    result.sql = sql

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": tool_result,
                    }
                )

        result.text = "Не удалось завершить запрос за отведённое число шагов."
        result.table = last_table
        return result

    def run(self, history: list[dict[str, str]], user_text: str) -> ChatResult:
        err = self._config_error()
        if err:
            return err
        messages = self._build_messages(history, user_text)
        return self._run_loop(messages)

    def run_stream(
        self,
        history: list[dict[str, str]],
        user_text: str,
    ) -> Iterator[dict[str, Any]]:
        err = self._config_error()
        if err:
            yield {"type": "done", "data": {"text": err.text}}
            return

        messages = self._build_messages(history, user_text)

        def on_tool(name: str) -> None:
            pass

        tool_events: list[dict[str, Any]] = []

        def capture_tool(name: str) -> None:
            tool_events.append({"type": "tool", "data": {"name": name}})

        result = self._run_loop(messages, on_tool=capture_tool)

        for event in tool_events:
            yield event

        for chunk in _chunk_text(result.text):
            yield {"type": "delta", "data": chunk}

        yield {
            "type": "done",
            "data": {
                "text": result.text,
                "sql": result.sql,
                "table": result.table,
                "chart": result.chart_option,
            },
        }
