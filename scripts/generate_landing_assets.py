#!/usr/bin/env python3
"""Генерация демо-HTML и PNG/GIF для лендинга (скриншоты через headless Chrome)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
LANDING = ROOT / "landing"
DEMO = LANDING / "demo"
SCREENS = LANDING / "assets" / "screens"

sys.path.insert(0, str(BACKEND))

from app.models import MonitoringSettings  # noqa: E402
from app.state_store import RecorderMetricsRow  # noqa: E402
from app.ui.error_report import build_error_report_context  # noqa: E402
from app.ui.error_report_render import render_error_report_html  # noqa: E402
from app.ui.health_dashboard import fleet_overview_context  # noqa: E402


def _rec(**kwargs):
    base = dict(
        id="nvr-1",
        object_name="ВСП Северный · ул. Ленина, 12",
        name="XRN-3210B2",
        host="10.12.40.101",
        port=80,
        use_https=False,
        device_kind="nvr",
        enabled=True,
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def _metrics(**kwargs) -> RecorderMetricsRow:
    polled = datetime(2026, 7, 10, 9, 0, tzinfo=timezone.utc)
    base = dict(
        recorder_id="nvr-1",
        model="XRN-3210B2",
        firmware_version="2.26.02",
        device_online=True,
        health_status="ok",
        health_reason=None,
        ntp_status="Success",
        time_skew_seconds=2.0,
        storage_used_percent=62.0,
        storage_status="Normal",
        archive_start=None,
        archive_end=None,
        archive_days=31.0,
        channel_count=16,
        channels_ok=16,
        channels_warn=0,
        channels_error=0,
        channels_unknown=0,
        last_polled_at=polled,
        disks_json=json.dumps(
            [
                {"TemperatureCelsius": 42, "Status": "Normal"},
                {"TemperatureCelsius": 44, "Status": "Normal"},
            ]
        ),
        system_events_json=json.dumps({"CPUFanError": False}),
        archive_min_days=28.0,
        archive_max_days=31.0,
        storageinfo_ok=True,
        archive_poll_error=None,
        recording_storage_enable=True,
    )
    base.update(kwargs)
    return RecorderMetricsRow(**base)


def demo_dataset():
    polled = datetime(2026, 7, 10, 9, 0, tzinfo=timezone.utc)
    since_temp = polled - timedelta(days=2, hours=5)
    since_archive = polled - timedelta(hours=18)
    since_skud = polled - timedelta(days=1)

    recorders = [
        _rec(id="nvr-1", object_name="ВСП Северный · ул. Ленина, 12"),
        _rec(
            id="nvr-2",
            object_name="ВСП Центральный · пр. Мира, 8",
            name="XRN-6410B2",
            host="10.12.40.102",
        ),
        _rec(
            id="nvr-3",
            object_name="Офис ТБ · Красный пр., 45",
            name="HRX-1634",
            host="10.12.40.103",
        ),
        _rec(
            id="nvr-4",
            object_name="КИЦ · наб. реки, 3",
            name="XRN-2010",
            host="10.12.40.104",
        ),
        _rec(
            id="skud-1",
            object_name="ВСП Северный · ул. Ленина, 12",
            name="СКУД-контроллер",
            host="10.12.50.11",
            device_kind="skud",
        ),
        _rec(
            id="bio-1",
            object_name="ВСП Центральный · пр. Мира, 8",
            name="BioStation-2",
            host="10.12.50.21",
            device_kind="bio",
        ),
        _rec(
            id="bio-2",
            object_name="Офис ТБ · Красный пр., 45",
            name="BioEntry-W2",
            host="10.12.50.22",
            device_kind="bio",
        ),
    ]

    metrics = {
        "nvr-1": _metrics(recorder_id="nvr-1"),
        "nvr-2": _metrics(
            recorder_id="nvr-2",
            health_status="warn",
            time_skew_seconds=95.0,
            disks_json=json.dumps([{"TemperatureCelsius": 56, "Status": "Normal"}]),
            channels_ok=14,
            channels_warn=2,
        ),
        "nvr-3": _metrics(
            recorder_id="nvr-3",
            health_status="error",
            device_online=True,
            archive_days=4.0,
            archive_min_days=4.0,
            archive_max_days=6.0,
            disks_json=json.dumps([{"TemperatureCelsius": 63, "Status": "Warning"}]),
            channels_ok=10,
            channels_error=3,
            channels_unknown=5,
            storage_used_percent=None,
            storage_status=None,
            system_events_json=json.dumps({"HDDNone": True}),
        ),
        "nvr-4": _metrics(
            recorder_id="nvr-4",
            health_status="ok",
            channels_ok=8,
            channel_count=8,
        ),
        "skud-1": _metrics(
            recorder_id="skud-1",
            device_online=False,
            health_status="error",
            health_reason="(100% потерь)",
            ntp_status=None,
            time_skew_seconds=None,
            storage_used_percent=None,
            storage_status=None,
            archive_days=None,
            channel_count=0,
            channels_ok=0,
            disks_json="[]",
        ),
        "bio-1": _metrics(
            recorder_id="bio-1",
            device_online=True,
            health_status="ok",
            ntp_status=None,
            channel_count=0,
            channels_ok=0,
            disks_json="[]",
        ),
        "bio-2": _metrics(
            recorder_id="bio-2",
            device_online=False,
            health_status="error",
            health_reason="(100% потерь)",
            ntp_status=None,
            channel_count=0,
            channels_ok=0,
            disks_json="[]",
        ),
    }

    settings = MonitoringSettings(
        hdd_temperature_warn_celsius=50,
        hdd_temperature_error_celsius=60,
        archive_days_error_threshold=7,
    )

    problem_since = {
        ("nvr-2", "temperature"): since_temp,
        ("nvr-3", "archive"): since_archive,
        ("nvr-3", "temperature"): since_temp,
    }
    recorder_since = {"skud-1": since_skud, "bio-2": since_skud}

    return recorders, metrics, settings, problem_since, recorder_since, polled


APP_CSS = """
:root{--bg-base:#0b0e14;--bg-surface:#12161f;--bg-elevated:#1a2030;--border-subtle:#2a3348;--text-primary:#e8ecf4;--text-secondary:#8b95a8;--text-muted:#5c6678;--accent:#3b82f6;--status-ok:#22c55e;--status-warn:#eab308;--status-error:#ef4444;--status-unknown:#6b7280;--sidebar-width:220px}
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,sans-serif;font-size:14px;line-height:1.5;color:var(--text-primary);background:var(--bg-base)}
.app-shell{display:flex;min-height:100vh}.sidebar{width:var(--sidebar-width);background:#0d1119;border-right:1px solid var(--border-subtle);padding:20px 12px}
.sidebar-brand{font-size:14px;font-weight:600;margin-bottom:20px;padding:0 8px}.sidebar-nav a{display:block;padding:8px 10px;border-radius:8px;color:var(--text-secondary);text-decoration:none;margin-bottom:2px}
.sidebar-nav a.active,.sidebar-nav a:hover{background:var(--bg-elevated);color:var(--text-primary)}
.main{flex:1;padding:24px 28px;overflow:auto}.page-title{font-size:22px;font-weight:600;margin:0 0 4px}.page-lead{color:var(--text-secondary);margin:0 0 20px}
.card{background:var(--bg-surface);border:1px solid var(--border-subtle);border-radius:10px;padding:16px 18px;margin-bottom:16px}
.kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px}
.kpi{padding:14px;border:1px solid var(--border-subtle);border-radius:8px;background:var(--bg-elevated)}
.kpi .v{font-size:22px;font-weight:700}.kpi .l{font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:.04em}
.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:8px 10px;border-bottom:1px solid var(--border-subtle);text-align:left}
th{color:var(--text-muted);font-weight:500;font-size:11px;text-transform:uppercase;letter-spacing:.04em}
.matrix-col-narrow{width:52px;text-align:center}
.matrix-cell{display:inline-flex;align-items:center;justify-content:center;min-width:32px;height:28px;border-radius:6px;border:1px solid;font-size:12px;font-weight:600}
.matrix-cell--ok{background:rgba(34,197,94,.12);border-color:rgba(34,197,94,.3);color:var(--status-ok)}
.matrix-cell--warn{background:rgba(234,179,8,.12);border-color:rgba(234,179,8,.35);color:var(--status-warn)}
.matrix-cell--error,.matrix-cell--offline{background:rgba(239,68,68,.12);border-color:rgba(239,68,68,.35);color:var(--status-error)}
.object-matrix-object a{color:var(--text-primary);text-decoration:none;font-weight:500}
.object-matrix-problems{font-size:11px;color:var(--text-muted);display:block}
.chart-bar{height:8px;border-radius:4px;background:var(--bg-elevated);overflow:hidden;margin-top:6px}
.chart-bar span{display:block;height:100%;border-radius:4px}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600}
.badge--confirmed{background:rgba(239,68,68,.15);color:#f87171}
.badge--suspect{background:rgba(234,179,8,.15);color:#fbbf24}
.chat{display:flex;flex-direction:column;gap:12px}.bubble{padding:12px 14px;border-radius:10px;max-width:85%}
.bubble--user{align-self:flex-end;background:#1e3a5f;border:1px solid #2563eb}
.bubble--ai{align-self:flex-start;background:var(--bg-elevated);border:1px solid var(--border-subtle)}
.sql{font-family:ui-monospace,monospace;font-size:12px;background:#0d1119;padding:10px;border-radius:6px;color:#93c5fd;margin-top:8px}
"""


def _matrix_html(rows_html: str) -> str:
    headers = ["Объект", "ТСВ", "Время", "Диски", "Темп.", "Каналы", "Архив", "СКУД", "Био"]
    th = "".join(f"<th scope='col' class='matrix-col-narrow'>{h}</th>" for h in headers[1:])
    return f"""
    <section class="card">
      <h2 style="margin:0 0 6px;font-size:16px">Проблемы по объектам</h2>
      <p style="margin:0 0 12px;color:var(--text-secondary);font-size:12px">ТСВ, СКУД и биотерминалы на одном экране</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>{headers[0]}</th>{th}</tr></thead>
          <tbody>{rows_html}</tbody>
        </table>
      </div>
    </section>"""


def _shell(title: str, nav_active: str, body: str) -> str:
    nav = [
        ("summary", "Сводка"),
        ("objects", "Объекты"),
        ("payments", "Статус оплаты"),
        ("rvr", "Повторные РВР"),
        ("ai", "Чат с AI"),
    ]
    links = "".join(
        f"<a href='#' class='{'active' if k == nav_active else ''}'>{label}</a>"
        for k, label in nav
    )
    return f"""<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">
    <title>{title}</title><style>{APP_CSS}</style></head><body>
    <div class="app-shell"><aside class="sidebar"><div class="sidebar-brand">Дашборд руководителя ТСО</div>
    <nav class="sidebar-nav">{links}</nav></aside>
    <main class="main">{body}</main></div></body></html>"""


def build_dashboard_html(ctx: dict) -> str:
    rows = []
    for row in ctx["object_matrix_rows"]:
        cells = "".join(
            f"<td><span class='matrix-cell matrix-cell--{c.status}' title='{c.title}'>"
            f"{'✓' if c.status == 'ok' and c.problem_count == 0 else (c.problem_count or '—')}</span></td>"
            for c in row.cells
        )
        prob = (
            f"<span class='object-matrix-problems'>{row.problem_nvr_count}/{row.nvr_count}</span>"
            if row.problem_nvr_count
            else f"<span class='object-matrix-problems'>{row.nvr_count} ТСВ</span>"
        )
        rows.append(
            f"<tr><th scope='row' class='object-matrix-object'><a href='#'>{row.object_name}</a>{prob}</th>{cells}</tr>"
        )
    kpis = f"""
    <div class="kpi-row">
      <div class="kpi"><div class="v">{ctx['fleet_object_count']}</div><div class="l">Объектов</div></div>
      <div class="kpi"><div class="v">{ctx['fleet_enabled_count']}</div><div class="l">Устройств в опросе</div></div>
      <div class="kpi"><div class="v" style="color:var(--status-error)">{ctx['fleet_critical_count']}</div><div class="l">Критичных</div></div>
      <div class="kpi"><div class="v" style="color:var(--status-warn)">{ctx['fleet_warn_count']}</div><div class="l">Предупреждений</div></div>
    </div>"""
    body = f"""<h1 class="page-title">Сводка</h1>
    <p class="page-lead">Единый дашборд: ТСВ, СКУД и биотерминалы · обновлено 10.07.2026 12:00</p>
    {kpis}{_matrix_html("".join(rows))}"""
    return _shell("Сводка", "summary", body)


def build_payments_html() -> str:
    body = """<h1 class="page-title">Статус оплаты</h1>
    <p class="page-lead">Заявки Портала Поставщика: модернизация и РВР</p>
    <div class="kpi-row">
      <div class="kpi"><div class="v">186</div><div class="l">Заявок всего</div></div>
      <div class="kpi"><div class="v" style="color:var(--status-warn)">23</div><div class="l">Ожидают оплаты</div></div>
      <div class="kpi"><div class="v" style="color:var(--status-error)">7</div><div class="l">Просрочено</div></div>
      <div class="kpi"><div class="v" style="color:var(--status-ok)">156</div><div class="l">Оплачено</div></div>
    </div>
    <section class="card"><h2 style="margin:0 0 12px;font-size:15px">Модернизация · по ТБ</h2>
    <div style="display:grid;gap:10px">
      <div><span style="color:var(--text-secondary)">ТБ Москва</span><div class="chart-bar"><span style="width:72%;background:var(--status-ok)"></span></div></div>
      <div><span style="color:var(--text-secondary)">ТБ Северо-Запад</span><div class="chart-bar"><span style="width:58%;background:var(--status-warn)"></span></div></div>
      <div><span style="color:var(--text-secondary)">ТБ Урал</span><div class="chart-bar"><span style="width:91%;background:var(--status-ok)"></span></div></div>
    </div></section>
  <section class="card"><h2 style="margin:0 0 12px;font-size:15px">РВР · повторные заявки</h2>
  <table><thead><tr><th>Объект</th><th>Заявок</th><th>Статус оплаты</th></tr></thead>
  <tbody>
    <tr><td>ВСП Центральный</td><td>4</td><td><span class="badge badge--suspect">На согласовании</span></td></tr>
    <tr><td>Офис ТБ</td><td>2</td><td><span class="badge badge--confirmed">Просрочено</span></td></tr>
    <tr><td>КИЦ наб. реки</td><td>1</td><td>Оплачено</td></tr>
  </tbody></table></section>"""
    return _shell("Статус оплаты", "payments", body)


def build_rvr_html() -> str:
    body = """<h1 class="page-title">Анализ повторных РВР</h1>
    <p class="page-lead">LLM-вердикты и свод проблем по объектам</p>
    <section class="card"><table><thead><tr><th>Объект</th><th>РВР</th><th>AI-вердикт</th><th>Свод проблем</th></tr></thead>
    <tbody>
      <tr><td>Офис ТБ · Красный пр.</td><td>5</td><td><span class="badge badge--confirmed">confirmed</span></td><td>Повторный отказ HDD, некачественное устранение</td></tr>
      <tr><td>ВСП Центральный</td><td>3</td><td><span class="badge badge--suspect">suspect</span></td><td>Расхождение времени, повтор канала 7</td></tr>
      <tr><td>ВСП Северный</td><td>2</td><td><span class="badge badge--possible" style="background:rgba(107,114,128,.15);color:#9ca3af">possible</span></td><td>Схожие формулировки в заявках</td></tr>
    </tbody></table></section>"""
    return _shell("Повторные РВР", "rvr", body)


def build_ai_chat_html() -> str:
    body = """<h1 class="page-title">Чат с AI</h1>
    <p class="page-lead">Запросы на естественном языке → SQL → таблица и график</p>
    <section class="card chat">
      <div class="bubble bubble--user">Сколько объектов с неисправными каналами за последний месяц?</div>
      <div class="bubble bubble--ai">Нашёл <strong>12 объектов</strong> с хотя бы одним каналом в статусе error за 30 дней.
        <div class="sql">SELECT object_name, COUNT(*) AS bad_channels
FROM channels c JOIN recorders r ...
WHERE c.status = 'error' AND c.updated_at &gt;= date('now', '-30 days')
GROUP BY object_name ORDER BY bad_channels DESC LIMIT 10;</div>
      </div>
      <div class="bubble bubble--ai"><table style="width:100%;margin-top:8px"><tr><th>Объект</th><th>Каналов error</th></tr>
        <tr><td>Офис ТБ</td><td>3</td></tr><tr><td>ВСП Центральный</td><td>2</td></tr></table></div>
    </section>"""
    return _shell("Чат с AI", "ai", body)


def screenshot(html_path: Path, png_path: Path, width: int = 1440, height: int = 900) -> None:
    from playwright.sync_api import sync_playwright

    url = html_path.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(url, wait_until="networkidle")
        page.screenshot(path=str(png_path), full_page=True)
        browser.close()


def make_gif(frames: list[Path], out: Path) -> None:
    if len(frames) < 2:
        return
    from playwright.sync_api import sync_playwright

    # Собираем GIF через playwright screenshots + ffmpeg (надёжнее concat)
    list_file = out.with_suffix(".txt")
    lines = [f"file '{f}'\nduration 2.5" for f in frames]
    lines.append(f"file '{frames[-1]}'")
    list_file.write_text("\n".join(lines), encoding="utf-8")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-vf",
            "fps=2,scale=1280:-1:flags=lanczos",
            str(out),
        ],
        check=True,
        capture_output=True,
    )
    list_file.unlink(missing_ok=True)


def main() -> None:
    DEMO.mkdir(parents=True, exist_ok=True)
    SCREENS.mkdir(parents=True, exist_ok=True)

    recorders, metrics, settings, problem_since, recorder_since, polled = demo_dataset()
    ctx = fleet_overview_context(
        recorders,
        metrics,
        settings,
        excluded_ids=set(),
        include_kind_columns=True,
    )

    error_ctx = build_error_report_context(
        recorders,
        metrics,
        settings,
        problem_since_map=problem_since,
        recorder_problem_since_map=recorder_since,
        report_at=polled,
    )

    demos = {
        "dashboard.html": build_dashboard_html(ctx),
        "payments.html": build_payments_html(),
        "rvr-repeat.html": build_rvr_html(),
        "ai-chat.html": build_ai_chat_html(),
        "error-report.html": render_error_report_html(error_ctx),
    }
    for name, html in demos.items():
        (DEMO / name).write_text(html, encoding="utf-8")

    shots = [
        ("dashboard.html", "dashboard-summary.png", 1440, 920),
        ("payments.html", "payments.png", 1440, 900),
        ("rvr-repeat.html", "report-rvr.png", 1440, 720),
        ("ai-chat.html", "ai-chat.png", 1440, 720),
    ]
    for html_name, png_name, w, h in shots:
        screenshot(DEMO / html_name, SCREENS / png_name, w, h)
        print(f"screenshot: {png_name}")

    hero = SCREENS / "hero-dashboard.png"
    screenshot(DEMO / "dashboard.html", hero, 1600, 1000)
    make_gif(
        [SCREENS / "dashboard-summary.png", SCREENS / "payments.png", SCREENS / "report-rvr.png"],
        SCREENS / "hero-demo.gif",
    )
    print("done:", SCREENS)


if __name__ == "__main__":
    main()
