"""AI-анализ повторных РВР через VseLLM."""

from __future__ import annotations

import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from .llm.client import LLMClient
from .models import LLMSettings

AiVerdict = Literal["confirmed", "suspect", "possible", "none"]
VALID_VERDICTS: frozenset[str] = frozenset({"confirmed", "suspect", "possible", "none"})
# Легаси: старый кэш и ответы модели с verdict "repeat" трактуются как suspect.
LEGACY_VERDICT_ALIASES: dict[str, AiVerdict] = {"repeat": "suspect"}

VERDICT_LABELS: dict[str, str] = {
    "confirmed": "Повтор",
    "suspect": "Подозрение на повтор",
    "possible": "Возможен повтор",
    "none": "Нет повтора",
    "repeat": "Подозрение на повтор",
}

DEFAULT_BATCH_SIZE = 20
DEFAULT_MAX_CHARS = 30_000
DEFAULT_MAX_CONCURRENCY = 4

_SYSTEM_PROMPT = """Ты аналитик заявок на ремонт систем технических средств охраны (САПС, СКУД, СОТС, СОУЭ, ТСВ и др.).

Для каждого объекта (адреса) в рамках ТОЛЬКО этого адреса оцени, есть ли повторяющиеся обращения по одному узлу (устройство, зона, шлейф, камера, контроллер) и признаки неполного устранения при прошлом выезде.

Верни строго JSON-массив без markdown и пояснений:
[{"i": 0, "verdict": "confirmed|suspect|possible|none", "analysis": "...", "description": "..."}]

Поля:
- i — индекс объекта из входных данных (целое число).
- verdict — уровень уверенности в повторе (выбирай САМЫЙ НИЗКИЙ уровень, который подтверждается данными; при сомнении понижай категорию):
  - "confirmed" — ПОВТОР ПОДТВЕРЖДЁН: тот же узел/зона/шлейф/камера/контроллер с тем же смыслом неисправности, И (а) явный признак, что прошлый ремонт не удержался (те же симптомы вскоре после закрытия заявки), ИЛИ (б) 3+ однотипных обращения по одному узлу. Только при однозначных данных.
  - "suspect" — ПОДОЗРЕНИЕ НА ПОВТОР: 2+ схожих обращения по одному узлу/симптому, но связь не стопроцентная (разные формулировки, нет прямого подтверждения неполного устранения, нет точного совпадения узла).
  - "possible" — ВОЗМОЖЕН ПОВТОР: слабые или косвенные признаки (близкие даты, соседние зоны, общий тип системы без совпадения узла), данных недостаточно для уверенного вывода.
  - "none" — НЕТ ПОВТОРА: заявки разовые или не связаны по узлу/симптому; при нехватке данных склоняйся сюда, а не завышай категорию.
- analysis — колонка «Анализ заявок / подозрение на повтор»: кратко — сколько заявок, по каким узлам, были ли повторы, даты. Начинай с ярлыка вердикта: «Повтор», «Подозрение на повтор», «Возможен повтор» или «Повторов не выявлено».
- description — колонка «Описание проблем на объекте»: какие устройства/узлы чаще ломались, типы неисправностей, закономерности простым языком.

Строгие правила (анти-завышение):
- Не помечай "confirmed" или "suspect", если совпадение только по адресу или только по виду системы (САПС, СКУД и т.д.) без совпадения конкретного узла/симптома.
- Метрика «Количество повторов» в данных — вспомогательная; verdict определяй по содержанию описаний заявок.
- Не выдумывай факты, которых нет в данных.
- Анализируй только в рамках одного адреса.
- Пиши кратко, делово, на русском, пригодно для Excel.
"""


def verdict_label(verdict: Optional[str]) -> str:
    """Человекочитаемый ярлык вердикта для UI и экспорта."""
    if not verdict:
        return ""
    raw = str(verdict).strip().lower()
    if raw in LEGACY_VERDICT_ALIASES:
        raw = LEGACY_VERDICT_ALIASES[raw]
    return VERDICT_LABELS.get(raw, "")


def matrix_row_id(address: str, object_type: str) -> str:
    raw = f"{address}\0{object_type}".encode("utf-8")
    return "rvr-" + hashlib.sha256(raw).hexdigest()[:12]


def group_fingerprint(group: dict[str, Any]) -> str:
    """Стабильный отпечаток набора заявок объекта для проверки актуальности кэша."""
    by_kind = group.get("by_kind") or {}
    parts: list[str] = []
    for kind in sorted(by_kind):
        for entry in by_kind[kind]:
            parts.append(
                f"{kind}|{entry.get('num', '')}|{entry.get('date', '')}|{entry.get('desc', '')}"
            )
    payload = "\n".join(parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _format_group_for_prompt(index: int, group: dict[str, Any]) -> str:
    lines = [
        f"### Объект i={index}",
        f"Адрес: {group.get('address', '')}",
        f"Тип объекта: {group.get('object_type', '')}",
        f"Количество повторов (метрика отчёта): {group.get('repeat_count', 0)}",
        "Заявки:",
    ]
    by_kind = group.get("by_kind") or {}
    for kind in sorted(by_kind):
        entries = by_kind[kind]
        if not entries:
            continue
        lines.append(f"  [{kind}]")
        for entry in entries:
            num = entry.get("num", "")
            date_s = entry.get("date", "")
            desc = entry.get("desc", "") or "—"
            lines.append(f"    - №{num}, {date_s}: {desc}")
    return "\n".join(lines)


def build_batch_prompt(groups_chunk: list[dict[str, Any]]) -> list[dict[str, str]]:
    user_parts = [
        f"Проанализируй {len(groups_chunk)} объект(ов). Верни JSON-массив с элементами для каждого i.",
        "",
    ]
    for i, group in enumerate(groups_chunk):
        user_parts.append(_format_group_for_prompt(i, group))
        user_parts.append("")
    return [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": "\n".join(user_parts).strip()},
    ]


def _extract_json_array(text: str) -> Any:
    cleaned = (text or "").strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned, re.IGNORECASE)
    if fence:
        cleaned = fence.group(1).strip()
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start >= 0 and end > start:
        cleaned = cleaned[start : end + 1]
    return json.loads(cleaned)


def _normalize_verdict(value: Any) -> AiVerdict:
    raw = str(value or "").strip().lower()
    if raw in LEGACY_VERDICT_ALIASES:
        return LEGACY_VERDICT_ALIASES[raw]
    if raw in VALID_VERDICTS:
        return raw  # type: ignore[return-value]
    if "подтверж" in raw or "подтвержд" in raw:
        return "confirmed"
    if "подозрен" in raw:
        return "suspect"
    if "возмож" in raw or "признак" in raw:
        return "possible"
    if "повтор" in raw or "систем" in raw:
        return "suspect"
    return "none"


@dataclass
class AiAnalysisRecord:
    row_id: str
    address: str
    object_type: str
    fingerprint: str
    verdict: AiVerdict
    analysis: str
    description: str
    model: str
    created_at: str

    def as_store_dict(self) -> dict[str, str]:
        return {
            "row_id": self.row_id,
            "address": self.address,
            "object_type": self.object_type,
            "fingerprint": self.fingerprint,
            "verdict": self.verdict,
            "analysis": self.analysis,
            "description": self.description,
            "model": self.model,
            "created_at": self.created_at,
        }


def parse_batch_response(
    text: str,
    groups_chunk: list[dict[str, Any]],
    *,
    model: str,
) -> list[AiAnalysisRecord]:
    now = datetime.now(timezone.utc).isoformat()
    parsed = _extract_json_array(text)
    if not isinstance(parsed, list):
        raise ValueError("Ответ LLM не является JSON-массивом")

    by_index: dict[int, dict[str, Any]] = {}
    for item in parsed:
        if not isinstance(item, dict):
            continue
        try:
            idx = int(item.get("i"))
        except (TypeError, ValueError):
            continue
        by_index[idx] = item

    records: list[AiAnalysisRecord] = []
    for i, group in enumerate(groups_chunk):
        item = by_index.get(i, {})
        address = str(group.get("address") or "")
        object_type = str(group.get("object_type") or "")
        fingerprint = group_fingerprint(group)
        records.append(
            AiAnalysisRecord(
                row_id=matrix_row_id(address, object_type),
                address=address,
                object_type=object_type,
                fingerprint=fingerprint,
                verdict=_normalize_verdict(item.get("verdict")),
                analysis=str(item.get("analysis") or "").strip(),
                description=str(item.get("description") or "").strip(),
                model=model,
                created_at=now,
            )
        )
    return records


def _estimate_group_chars(group: dict[str, Any]) -> int:
    return len(_format_group_for_prompt(0, group))


def chunk_groups(
    groups: list[dict[str, Any]],
    *,
    max_items: int = DEFAULT_BATCH_SIZE,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> list[list[dict[str, Any]]]:
    if not groups:
        return []
    chunks: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    current_chars = 0
    for group in groups:
        group_chars = _estimate_group_chars(group)
        would_exceed_items = len(current) >= max_items
        would_exceed_chars = current and (current_chars + group_chars > max_chars)
        if current and (would_exceed_items or would_exceed_chars):
            chunks.append(current)
            current = []
            current_chars = 0
        current.append(group)
        current_chars += group_chars
    if current:
        chunks.append(current)
    return chunks


def _analyze_chunk(
    client: LLMClient,
    groups_chunk: list[dict[str, Any]],
    *,
    model: str,
) -> list[AiAnalysisRecord]:
    messages = build_batch_prompt(groups_chunk)
    response = client.chat(messages, model=model)
    content = response.choices[0].message.content or ""
    return parse_batch_response(content, groups_chunk, model=model)


def analyze_groups(
    groups: list[dict[str, Any]],
    client: LLMClient,
    settings: LLMSettings,
) -> dict[str, AiAnalysisRecord]:
    if not groups:
        return {}

    model = settings.analysis_model or "google/gemini-2.5-flash"
    batch_size = max(1, settings.analysis_batch_size)
    max_concurrency = max(1, settings.analysis_max_concurrency)
    chunks = chunk_groups(groups, max_items=batch_size)

    results: dict[str, AiAnalysisRecord] = {}
    with ThreadPoolExecutor(max_workers=min(max_concurrency, len(chunks))) as pool:
        futures = {
            pool.submit(_analyze_chunk, client, chunk, model=model): chunk
            for chunk in chunks
        }
        for future in as_completed(futures):
            chunk_records = future.result()
            for record in chunk_records:
                results[record.row_id] = record
    return results
