"""Тесты AI-анализа повторных РВР."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.models import LLMSettings
from app.rvr_ai_analysis import (
    analyze_groups,
    build_batch_prompt,
    chunk_groups,
    group_fingerprint,
    matrix_row_id,
    parse_batch_response,
)
from app.state_store import StateStore


def _sample_group() -> dict:
    return {
        "address": "г Москва, ул Тестовая, 1",
        "object_type": "АДЗ",
        "repeat_count": 2,
        "by_kind": {
            "САПС": [
                {"num": "100", "date": "01.06.2026", "desc": "неисправность датчика"},
                {"num": "101", "date": "02.06.2026", "desc": "неисправность датчика зона 5"},
            ],
            "ТСВ": [
                {"num": "200", "date": "03.06.2026", "desc": "нет изображения камеры 29"},
            ],
        },
    }


def test_matrix_row_id_stable() -> None:
    a = matrix_row_id("ул. Тест, 1", "АДЗ")
    b = matrix_row_id("ул. Тест, 1", "АДЗ")
    c = matrix_row_id("ул. Тест, 1", "ВСП")
    assert a == b
    assert a.startswith("rvr-")
    assert a != c


def test_group_fingerprint_stable_and_sensitive() -> None:
    group = _sample_group()
    fp1 = group_fingerprint(group)
    fp2 = group_fingerprint(group)
    assert fp1 == fp2

    changed = dict(group)
    changed["by_kind"] = {
        **group["by_kind"],
        "САПС": group["by_kind"]["САПС"] + [
            {"num": "102", "date": "04.06.2026", "desc": "новая заявка"},
        ],
    }
    assert group_fingerprint(changed) != fp1


def test_build_batch_prompt_contains_objects() -> None:
    group = _sample_group()
    messages = build_batch_prompt([group])
    assert messages[0]["role"] == "system"
    user = messages[1]["content"]
    assert "i=0" in user
    assert "г Москва, ул Тестовая, 1" in user
    assert "САПС" in user


def test_parse_batch_response_with_json_fence() -> None:
    group = _sample_group()
    text = """Вот результат:
```json
[
  {
    "i": 0,
    "verdict": "repeat",
    "analysis": "По адресу 3 заявки, 2 схожие по САПС.",
    "description": "Повторяются неисправности датчиков пожарной сигнализации."
  }
]
```"""
    records = parse_batch_response(text, [group], model="google/gemini-2.5-flash")
    assert len(records) == 1
    rec = records[0]
    assert rec.verdict == "repeat"
    assert "3 заявки" in rec.analysis
    assert "датчиков" in rec.description
    assert rec.row_id == matrix_row_id(group["address"], group["object_type"])


def test_parse_batch_response_defaults_when_index_missing() -> None:
    group = _sample_group()
    records = parse_batch_response("[]", [group], model="test-model")
    assert len(records) == 1
    assert records[0].verdict == "none"
    assert records[0].analysis == ""


def test_chunk_groups_respects_max_items() -> None:
    groups = [_sample_group() for _ in range(5)]
    for g in groups:
        g["address"] = f"адрес {groups.index(g)}"
    chunks = chunk_groups(groups, max_items=2, max_chars=1_000_000)
    assert len(chunks) == 3
    assert sum(len(c) for c in chunks) == 5


def test_analyze_groups_merges_chunks(monkeypatch: pytest.MonkeyPatch) -> None:
    groups = [_sample_group(), _sample_group()]
    groups[1]["address"] = "г Москва, ул Другая, 2"

    client = MagicMock()
    settings = LLMSettings(
        analysis_model="google/gemini-2.5-flash",
        analysis_batch_size=1,
        analysis_max_concurrency=2,
    )

    def fake_analyze_chunk(client_arg, chunk, *, model):
        payload = [
            {
                "i": 0,
                "verdict": "possible",
                "analysis": f"анализ {chunk[0]['address']}",
                "description": "описание",
            }
        ]
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message.content = str(payload).replace("'", '"')
        from app.rvr_ai_analysis import parse_batch_response

        return parse_batch_response(
            response.choices[0].message.content,
            chunk,
            model=model,
        )

    monkeypatch.setattr("app.rvr_ai_analysis._analyze_chunk", fake_analyze_chunk)
    results = analyze_groups(groups, client, settings)
    assert len(results) == 2
    assert all(r.verdict == "possible" for r in results.values())


def test_rvr_ai_analysis_store_roundtrip(tmp_path) -> None:
    db_path = tmp_path / "test.db"
    store = StateStore(path=db_path)
    store.init_db()

    record = {
        "row_id": "rvr-abc123",
        "address": "ул. Тест, 1",
        "object_type": "АДЗ",
        "fingerprint": "fp1",
        "verdict": "repeat",
        "analysis": "Подозрение на повтор",
        "description": "Проблемы с датчиками",
        "model": "google/gemini-2.5-flash",
        "created_at": "2026-06-01T00:00:00+00:00",
    }
    store.upsert_rvr_ai_analysis([record])
    loaded = store.get_rvr_ai_analysis(["rvr-abc123"])
    assert "rvr-abc123" in loaded
    assert loaded["rvr-abc123"]["verdict"] == "repeat"
    assert loaded["rvr-abc123"]["analysis"] == "Подозрение на повтор"

    updated = {**record, "verdict": "none", "analysis": "Обновлено"}
    store.upsert_rvr_ai_analysis([updated])
    loaded2 = store.get_rvr_ai_analysis(["rvr-abc123"])
    assert loaded2["rvr-abc123"]["verdict"] == "none"
    assert loaded2["rvr-abc123"]["analysis"] == "Обновлено"
