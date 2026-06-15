from __future__ import annotations

from typing import Any, Iterator, Optional

import httpx
from openai import OpenAI

from ..config_store import ConfigStore
from ..models import LLMSettings


class LLMClient:
    def __init__(self, settings: Optional[LLMSettings] = None) -> None:
        self.settings = settings or ConfigStore().load().llm
        self._client = OpenAI(
            api_key=self.settings.api_key,
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
    ) -> Any:
        kwargs: dict[str, Any] = {
            "model": self.settings.model,
            "messages": messages,
            "stream": stream,
        }
        if tools:
            kwargs["tools"] = tools
        return self._client.chat.completions.create(**kwargs)

    def chat_stream(
        self,
        messages: list[dict[str, Any]],
    ) -> Iterator[Any]:
        return self.chat(messages, stream=True)
