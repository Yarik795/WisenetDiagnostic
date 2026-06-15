from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.cashflow_report import SECTION_SPECS
from app.main import app
from app.ui.payments_export import (
    build_payments_export_context,
    render_payments_bar_svg,
    render_payments_donut_svg,
    render_payments_export_html,
)


def _sample_report() -> dict:
    section = {
        "key": "az_mb",
        "title": "АЗ МБ",
        "kpi": {
            "total_count": 2,
            "total_sum": "10 000,00 руб.",
            "oldest_date": "2026-01",
            "largest_amount": "7 000,00 руб.",
        },
        "series": {
            "months": ["2026-01", "2026-02"],
            "parties": ["Войнов", "ЦС"],
            "matrix": {
                "Войнов": [1000.0, 0.0],
                "ЦС": [0.0, 2000.0],
            },
            "party_totals": {"Войнов": 1000.0, "ЦС": 2000.0},
            "count_matrix": {
                "Войнов": [1, 0],
                "ЦС": [0, 1],
            },
            "count_totals": {"Войнов": 1, "ЦС": 1},
            "approved": {
                "amount": [5000.0, 0.0],
                "count": [1, 0],
                "total_amount": 5000.0,
                "total_count": 1,
            },
            "colors": {
                "Войнов": "#38bdf8",
                "ЦС": "#fb923c",
                "Согласовано": "#34d399",
            },
        },
        "rows": [
            {
                "month": "2026-01",
                "status": {"text": "Войнов", "class": "status-otso"},
                "request_number": "123",
                "request_url": "https://example.test/123",
                "amount": "1 000,00",
                "amount_value": 1000.0,
                "status_raw": "На согласовании",
                "act_status": "Проект",
            }
        ],
    }
    empty_sections = [
        {**section, "key": key, "title": title, "rows": [], "kpi": section["kpi"]}
        if key != "az_mb"
        else section
        for key, title in SECTION_SPECS
    ]
    return {
        "generated_at": "2026-06-15T12:00:00+00:00",
        "source_file": "requests.xlsx",
        "reports": {
            "modern": {
                "title": "Отчет по статусу согласования заявок на модернизацию",
                "sections": empty_sections,
            },
            "rvr": {
                "title": "Отчет РВР",
                "sections": empty_sections,
            },
        },
    }


def test_render_payments_bar_svg_includes_approved() -> None:
    series = _sample_report()["reports"]["modern"]["sections"][0]["series"]
    svg = render_payments_bar_svg(series, "amount")
    assert svg.startswith("<svg")
    assert "Согласовано" in svg or "#34d399" in svg


def test_render_payments_donut_svg_non_empty() -> None:
    series = _sample_report()["reports"]["modern"]["sections"][0]["series"]
    svg = render_payments_donut_svg(series, "count")
    assert svg.startswith("<svg")
    assert "#38bdf8" in svg
    assert "Итого" in svg
    assert "Войнов" not in svg


def test_render_payments_bar_svg_axis_abbreviated() -> None:
    series = {
        "months": ["2026-01"],
        "parties": ["Войнов"],
        "matrix": {"Войнов": [37_383_213.99]},
        "party_totals": {"Войнов": 37_383_213.99},
        "count_matrix": {"Войнов": [1]},
        "count_totals": {"Войнов": 1},
        "approved": {"amount": [0.0], "count": [0]},
        "colors": {"Войнов": "#38bdf8"},
    }
    svg = render_payments_bar_svg(series, "amount")
    assert "37,4 млн" in svg
    assert "37 383 213,99 руб." not in svg


def test_build_payments_export_context_party_totals_fmt() -> None:
    report = _sample_report()
    context = build_payments_export_context(report, "modern", {"az_mb": "amount"})
    az = next(s for s in context["sections"] if s["key"] == "az_mb")
    assert len(az["party_totals_fmt"]) == 2
    first = az["party_totals_fmt"][0]
    assert first["party"] == "Войнов"
    assert "pct" in first
    assert "color" in first
    assert first["color"] == "#38bdf8"


def test_build_payments_export_context_metric_amount_vs_count() -> None:
    report = _sample_report()
    amount_ctx = build_payments_export_context(report, "modern", {"az_mb": "amount"})
    count_ctx = build_payments_export_context(report, "modern", {"az_mb": "count"})
    az_amount = next(s for s in amount_ctx["sections"] if s["key"] == "az_mb")
    az_count = next(s for s in count_ctx["sections"] if s["key"] == "az_mb")
    assert az_amount["metric"] == "amount"
    assert az_count["metric"] == "count"
    assert "1 000,00" in az_amount["party_totals_fmt"][0]["value"]
    assert "заяв" in az_count["party_totals_fmt"][0]["value"]


def test_render_payments_export_html_contains_sections() -> None:
    report = _sample_report()
    context = build_payments_export_context(report, "modern")
    html = render_payments_export_html(context)
    assert "<!DOCTYPE html>" in html
    assert "АЗ МБ" in html
    assert "123" in html


@pytest.fixture
def client(tmp_path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    from app.config_store import ConfigStore
    from app.ui.dependencies import get_store

    artifact = tmp_path / "cashflow_report.json"
    artifact.write_text(json.dumps(_sample_report()), encoding="utf-8")
    monkeypatch.setattr("app.web.routes.load_report_artifact", lambda: _sample_report())
    monkeypatch.setattr("app.cashflow_report.REPORT_ARTIFACT", artifact)

    config_path = tmp_path / "config.json"
    store = ConfigStore(path=config_path)

    def override_store() -> ConfigStore:
        return store

    app.dependency_overrides[get_store] = override_store
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_payments_export_route_returns_attachment(client: TestClient) -> None:
    response = client.get("/payments/export.html?kind=modern&m_az_mb=amount")
    assert response.status_code == 200
    assert "attachment" in response.headers.get("content-disposition", "")
    assert "АЗ МБ" in response.text


def test_payments_email_route_requires_smtp_config(client: TestClient) -> None:
    response = client.post("/payments/report/email?kind=modern")
    assert response.status_code == 400
    payload = response.json()
    assert payload["ok"] is False
    assert "email_report" in payload["message"]


def test_payments_email_route_sends_when_configured(client: TestClient) -> None:
    from app.models import EmailReportSettings
    from app.ui.dependencies import get_store

    store = app.dependency_overrides[get_store]()
    config = store.load()
    config.email_report = EmailReportSettings(
        from_email="sender@test",
        to_emails=["recipient@test"],
        smtp_host="smtp.test",
    )
    store.save(config)

    with patch("app.email_sender.send_report_email") as send_mock:
        response = client.post("/payments/report/email?kind=modern&m_az_mb=count")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    send_mock.assert_called_once()
