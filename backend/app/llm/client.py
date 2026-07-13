from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator, Optional

import httpx
from openai import OpenAI

from ..config_store import ConfigStore
from ..models import LLMSettings


@dataclass
class StreamedToolCall:
    id: str
    name: str
    arguments: str


class LLMClient:
    def __init__(self, settings: Optional[LLMSettings] = None) -> None:
        self.settings = settings or ConfigStore().load().llm
        self._client = OpenAI(
            api_key=self.settings.api_key or "not-configured",
            base_url=self.settings.base_url,
            http_client=httpx.Client(
                verify=self.settings.verify_ssl,
                timeout=120.0,
            ),
        )

    def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        tools: Optional[list[dict[str, Any]]] = None,
        stream: bool = False,
        model: Optional[str] = None,
    ) -> Any:
        kwargs: dict[str, Any] = {
            "model": model or self.settings.model,
            "messages": messages,
            "stream": stream,
        }
        if tools:
            kwargs["tools"] = tools
        return self._client.chat.completions.create(**kwargs)

    def iter_completion(
        self,
        messages: list[dict[str, Any]],
        *,
        tools: Optional[list[dict[str, Any]]] = None,
    ) -> Iterator[str | StreamedToolCall]:
        stream = self.chat(messages, tools=tools, stream=True)
        tool_calls: dict[int, StreamedToolCall] = {}
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls:
                        tool_calls[idx] = StreamedToolCall(id="", name="", arguments="")
                    entry = tool_calls[idx]
                    if tc.id:
                        entry.id = tc.id
                    if tc.function:
                        if tc.function.name:
                            entry.name = tc.function.name
                        if tc.function.arguments:
                            entry.arguments += tc.function.arguments
        for idx in sorted(tool_calls):
            yield tool_calls[idx]

    def chat_stream_text(
        self,
        messages: list[dict[str, Any]],
        *,
        tools: Optional[list[dict[str, Any]]] = None,
    ) -> Iterator[str]:
        yield from (
            piece
            for piece in self.iter_completion(messages, tools=tools)
            if isinstance(piece, str)
        )

    def chat_stream(
        self,
        messages: list[dict[str, Any]],
    ) -> Iterator[Any]:
        return self.chat(messages, stream=True)
