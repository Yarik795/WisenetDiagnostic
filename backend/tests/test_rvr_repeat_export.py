"""Тесты HTML-экспорта отчёта «Анализ повторных РВР»."""

from __future__ import annotations

from app.ui.rvr_repeat_export import (
    build_rvr_repeat_export_context,
    render_rvr_repeat_export_html,
    render_rvr_repeat_email_body_html,
)


def _sample_page_ctx() -> dict:
    return {
        "rvr_threshold": 2,
        "rvr_filters_text": "Период: Q1 2026",
        "rvr_latest_import": None,
        "rvr_latest_naumen_import": None,
        "rvr_kpi": {
            "groups_total": 1,
            "repeats_total": 2,
            "requests_total": 3,
            "top_object": "ул. Ленина, 1",
        },
        "rvr_matrix_rows": [
            {
                "row_id": "rvr-test-1",
                "address": "ул. Ленина, 1",
                "object_type": "ВСП",
                "repeat_count": 2,
                "aggregate_status": "warn",
                "ai_verdict": None,
                "ai_checked": False,
                "ai_stale": False,
                "analysis": None,
                "description": "описание",
                "cells": [
                    {
                        "kind": "СОТС",
                        "count": 2,
                        "status": "warn",
                        "title": "2 заявки",
                        "entries": [
                            {"num": "1001", "date": "01.01.2026", "desc": "проблема"},
                            {"num": "1002", "date": "02.01.2026", "desc": "ещё"},
                        ],
                    },
                    {
                        "kind": "ТСВ",
                        "count": 0,
                        "status": "na",
                        "title": "",
                        "entries": [],
                    },
                ],
            }
        ],
        "rvr_kinds": ["СОТС", "ТСВ"],
        "rvr_report": {
            "period": {"label": "Q1 2026", "from": "2026-01-01", "to": "2026-03-31"},
            "kpi": {
                "groups_total": 1,
                "repeats_total": 2,
                "requests_total": 3,
                "top_object": "ул. Ленина, 1",
            },
            "groups_ge2": [{"ai_verdict": "confirmed"}],
            "generated_at": "2026-03-15T12:00:00+00:00",
        },
    }


def test_build_rvr_repeat_export_context() -> None:
    ctx = build_rvr_repeat_export_context(_sample_page_ctx())
    assert ctx["export"]["title"] == "Анализ повторных РВР"
    assert ctx["export"]["period_label"] == "Q1 2026"
    assert ctx["export"]["threshold_label"] == "Сводка (≥2)"
    assert len(ctx["rvr_matrix_rows"]) == 1


def test_render_rvr_repeat_export_html() -> None:
    export_ctx = build_rvr_repeat_export_context(_sample_page_ctx())
    html = render_rvr_repeat_export_html(export_ctx)
    assert "Анализ повторных РВР" in html
    assert "data-rvr-cell-toggle" in html
    assert "openRvrRepeatDetail" in html
    assert "ул. Ленина, 1" in html
    assert "№ 1001" in html


def test_render_rvr_repeat_email_body_html() -> None:
    report = _sample_page_ctx()["rvr_report"]
    body = render_rvr_repeat_email_body_html(report)
    assert "HTML-отчёт" in body
    assert "Q1 2026" in body
