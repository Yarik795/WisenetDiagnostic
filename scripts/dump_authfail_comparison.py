#!/usr/bin/env python3
"""Снять сырые ответы SUNAPI с двух регистраторов для анализа AuthFail.

Сохраняет:
  - общий файл сравнения с разбором каналов (как в production evaluate_channel_health);
  - отдельные raw-дампы по каждому IP.

По умолчанию опрашиваются:
  100.111.2.250  — регистратор с ложной деградацией (AuthFail)
  10.89.188.193  — эталон той же модели без ошибки

Запуск (из корня проекта):

  Windows PowerShell:
    cd "D:\\Путь\\К\\Wisenet Диагностика"
    .\\backend\\.venv\\Scripts\\python.exe scripts\\dump_authfail_comparison.py

  Свои адреса:
    .\\backend\\.venv\\Scripts\\python.exe scripts\\dump_authfail_comparison.py --host 100.111.2.250 --host 10.89.188.193

  Явный config.json:
    $env:CONFIG_PATH = ".\\config.json"
    .\\backend\\.venv\\Scripts\\python.exe scripts\\dump_authfail_comparison.py

Результат: docs/nvr-samples/raw/authfail-compare/<timestamp>/
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import httpx

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.models import Credentials, MonitoringSettings, Recorder  # noqa: E402
from app.monitoring import evaluate_channel_health  # noqa: E402
from app.sunapi_extended import (  # noqa: E402
    NvrApiProfile,
    build_url,
    merge_channels,
    parse_cameraregister,
    parse_deviceinfo_response,
    parse_eventstatus,
    parse_videosource_channels,
    poll_recorder,
)

DEFAULT_CONFIG = ROOT / "config.json"
OUT_BASE = ROOT / "docs" / "nvr-samples" / "raw" / "authfail-compare"

DEFAULT_HOSTS = ("100.111.2.250", "10.89.188.193")

# Те же endpoint, что poll_recorder и dump_nvr_api_samples.py
ENDPOINTS: list[tuple[str, str, str, dict[str, str]]] = [
    ("system.cgi", "deviceinfo", "view", {}),
    ("media.cgi", "cameraregister", "view", {}),
    ("media.cgi", "videosource", "view", {}),
    ("system.cgi", "storageinfo", "view", {}),
    ("recording.cgi", "diskutility", "view", {}),
    ("system.cgi", "date", "view", {}),
    ("recording.cgi", "searchrecordingperiod", "view", {}),
    ("recording.cgi", "storage", "view", {}),
    ("eventstatus.cgi", "eventstatus", "check", {}),
]


def load_credentials(config_path: Path) -> tuple[str, str]:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    creds = data.get("credentials") or {}
    user = (creds.get("username") or "").strip()
    password = creds.get("password") or ""
    if not user:
        raise SystemExit(f"Нет credentials.username в {config_path}")
    if not password or password == "CHANGE_ME":
        raise SystemExit(
            f"Задайте реальный пароль API в {config_path} (credentials.password)"
        )
    return user, password


def make_recorder(host: str, *, port: int, use_https: bool, index: int) -> Recorder:
    return Recorder(
        id=f"probe-{index}",
        object_name="AuthFail probe",
        name=f"probe-{host}",
        host=host,
        port=port,
        use_https=use_https,
    )


def fetch(client: httpx.Client, url: str, timeout: float) -> tuple[int, str, str | None]:
    try:
        response = client.get(url, timeout=timeout)
        return response.status_code, response.text, None
    except httpx.TimeoutException:
        return 0, "", "timeout"
    except httpx.RequestError as exc:
        return 0, "", str(exc)


def fetch_all_endpoints(
    client: httpx.Client,
    recorder: Recorder,
    *,
    timeout: float,
) -> tuple[list[str], dict[str, str]]:
    """Один проход по endpoint: raw-текст для файла и тела для разбора."""
    lines: list[str] = [
        f"# SUNAPI raw dump @ {recorder.host}:{recorder.port}",
        f"# UTC {datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    bodies: dict[str, str] = {}
    for cgi, submenu, action, extra in ENDPOINTS:
        url = build_url(recorder, cgi, submenu, action=action, **extra)
        status, body, err = fetch(client, url, timeout)
        if status == 200 and not err and body.strip():
            bodies[submenu] = body
        lines.extend(
            [
                "=" * 72,
                f"{submenu} / {cgi} / action={action}",
                url,
                f"HTTP: {status}" + (f"  ERROR: {err}" if err else ""),
                "----- BODY START -----",
                body if body else "(empty)",
                "----- BODY END -----",
                "",
            ]
        )
    return lines, bodies


def _channel_dict(ch) -> dict[str, Any]:
    return {
        "channel_no": ch.channel_no,
        "name": ch.name,
        "source_state": ch.source_state,
        "video_state": ch.video_state,
        "camera_ip": ch.camera_ip,
        "camera_model": ch.camera_model,
        "register_status": ch.register_status,
        "data_rate": ch.data_rate,
        "cpu_usage": ch.cpu_usage,
        "poe_status": ch.poe_status,
    }


def analyze_host(
    recorder: Recorder,
    *,
    bodies: dict[str, str],
    settings: MonitoringSettings,
) -> dict[str, Any]:
    device_body = bodies.get("deviceinfo", "")
    device = parse_deviceinfo_response(device_body) if device_body.strip() else None
    model = device.model if device else None
    profile = NvrApiProfile.from_device(device) if device else None

    cam_channels = parse_cameraregister(bodies.get("cameraregister", ""))
    vs_channels = parse_videosource_channels(bodies.get("videosource", ""))
    channels = merge_channels(cam_channels, vs_channels)

    event_result = parse_eventstatus(bodies.get("eventstatus", ""))
    events_by_no = {e.channel_no: e for e in event_result.channels}

    channel_rows: list[dict[str, Any]] = []
    warn_channels: list[dict[str, Any]] = []
    for ch in channels:
        event = events_by_no.get(ch.channel_no)
        health, reason = evaluate_channel_health(
            ch,
            event,
            settings,
            device_model=model,
            profile=profile,
        )
        row = {
            "health": health,
            "reason": reason,
            "channel": _channel_dict(ch),
            "event": None
            if event is None
            else {
                "connected": event.connected,
                "video_loss": event.video_loss,
                "low_fps": event.low_fps,
            },
        }
        channel_rows.append(row)
        if health in ("warn", "error"):
            warn_channels.append(row)

    return {
        "host": recorder.host,
        "model": model,
        "device_type": device.device_type if device else None,
        "firmware": device.firmware_version if device else None,
        "channels_total": len(channels),
        "channels_warn_error": len(warn_channels),
        "warn_error_channels": warn_channels,
        "all_channels": channel_rows,
        "system_events": event_result.system_events,
    }


def format_analysis_section(title: str, analysis: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "#" * 72,
        f"# {title}",
        "#" * 72,
        f"host: {analysis['host']}",
        f"model: {analysis.get('model')}",
        f"device_type: {analysis.get('device_type')}",
        f"firmware: {analysis.get('firmware')}",
        f"channels: {analysis['channels_total']} total, "
        f"{analysis['channels_warn_error']} warn/error",
        "",
    ]
    if analysis["warn_error_channels"]:
        lines.append("Каналы с warn/error:")
        for row in analysis["warn_error_channels"]:
            ch = row["channel"]
            lines.append(
                f"  CH{ch['channel_no']:>2}  {row['health']:5}  "
                f"reg={ch.get('register_status')!r}  "
                f"src={ch.get('source_state')!r}  "
                f"rate={ch.get('data_rate')}  "
                f"event={row.get('event')}  "
                f"— {row['reason']}"
            )
        lines.append("")
    else:
        lines.append("Каналы с warn/error: нет")
        lines.append("")

    authfail = [
        row
        for row in analysis["all_channels"]
        if (row["channel"].get("register_status") or "").lower() == "authfail"
    ]
    lines.append(f"Каналы с register_status=AuthFail: {len(authfail)}")
    for row in authfail:
        ch = row["channel"]
        lines.append(
            f"  CH{ch['channel_no']:>2}  health={row['health']}  "
            f"src={ch.get('source_state')!r}  rate={ch.get('data_rate')}  "
            f"event={row.get('event')}  — {row['reason']}"
        )
    lines.append("")
    return lines


async def verify_poll_recorder(
    recorder: Recorder,
    credentials: Credentials,
    *,
    timeout: float,
) -> dict[str, Any]:
    poll = await poll_recorder(
        recorder,
        credentials,
        include_inventory=False,
        timeout=timeout,
    )
    return {
        "online": poll.online,
        "error": poll.error,
        "model": poll.device.model if poll.device else None,
        "channels_polled": poll.channels_polled,
        "channels_count": len(poll.channels),
        "cpu_usage_max": poll.cpu_usage_max,
        "data_rate_total_mbps": poll.data_rate_total_mbps,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("CONFIG_PATH", DEFAULT_CONFIG)),
        help="Путь к config.json",
    )
    parser.add_argument(
        "--host",
        action="append",
        dest="hosts",
        metavar="IP",
        help="IP регистратора (можно несколько раз; по умолчанию два адреса из задачи)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=80,
        help="Порт HTTP (по умолчанию 80)",
    )
    parser.add_argument(
        "--https",
        action="store_true",
        help="Использовать HTTPS",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Каталог для результатов (по умолчанию authfail-compare/<timestamp>/)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=25.0,
        help="Таймаут HTTP, секунды",
    )
    parser.add_argument(
        "--skip-poll-recorder",
        action="store_true",
        help="Не запускать async poll_recorder (только сырые HTTP-ответы)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    hosts = tuple(args.hosts) if args.hosts else DEFAULT_HOSTS
    username, password = load_credentials(args.config)
    credentials = Credentials(username=username, password=password)
    settings = MonitoringSettings()

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.out_dir or (OUT_BASE / ts)
    out_dir.mkdir(parents=True, exist_ok=True)

    analyses: list[dict[str, Any]] = []
    poll_checks: list[dict[str, Any]] = []

    with httpx.Client(auth=httpx.DigestAuth(username, password), verify=False) as client:
        for index, host in enumerate(hosts, start=1):
            recorder = make_recorder(
                host,
                port=args.port,
                use_https=args.https,
                index=index,
            )
            print(f"Опрос {host} ...", flush=True)

            raw_lines, bodies = fetch_all_endpoints(
                client, recorder, timeout=args.timeout
            )
            raw_path = out_dir / f"{host.replace('.', '-')}.txt"
            raw_path.write_text("\n".join(raw_lines), encoding="utf-8")
            print(f"  raw -> {raw_path}")

            analysis = analyze_host(recorder, bodies=bodies, settings=settings)
            analyses.append(analysis)

            analysis_json = out_dir / f"{host.replace('.', '-')}_analysis.json"
            analysis_json.write_text(
                json.dumps(analysis, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"  analysis -> {analysis_json}")

    if not args.skip_poll_recorder:
        print("Проверка через poll_recorder ...", flush=True)

        async def run_polls() -> list[dict[str, Any]]:
            results = []
            for index, host in enumerate(hosts, start=1):
                recorder = make_recorder(
                    host,
                    port=args.port,
                    use_https=args.https,
                    index=index,
                )
                check = await verify_poll_recorder(
                    recorder,
                    credentials,
                    timeout=args.timeout,
                )
                check["host"] = host
                results.append(check)
            return results

        poll_checks = asyncio.run(run_polls())
        poll_path = out_dir / "poll_recorder_check.json"
        poll_path.write_text(
            json.dumps(poll_checks, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"  poll_recorder -> {poll_path}")

    summary_lines = [
        f"AuthFail comparison dump",
        f"UTC: {ts}",
        f"Hosts: {', '.join(hosts)}",
        f"Config: {args.config}",
        "",
    ]
    for analysis in analyses:
        summary_lines.extend(
            format_analysis_section(f"Анализ {analysis['host']}", analysis)
        )

    if len(analyses) == 2:
        a, b = analyses
        summary_lines.extend(
            [
                "#" * 72,
                "# Сравнение register_status по номерам каналов",
                "#" * 72,
                "",
            ]
        )
        by_no_a = {row["channel"]["channel_no"]: row for row in a["all_channels"]}
        by_no_b = {row["channel"]["channel_no"]: row for row in b["all_channels"]}
        all_nos = sorted(set(by_no_a) | set(by_no_b))
        for no in all_nos:
            ra = by_no_a.get(no)
            rb = by_no_b.get(no)
            sta = (ra or {}).get("channel", {}).get("register_status")
            stb = (rb or {}).get("channel", {}).get("register_status")
            if sta != stb or (sta or "").lower() == "authfail" or (stb or "").lower() == "authfail":
                ha = (ra or {}).get("health", "-")
                hb = (rb or {}).get("health", "-")
                summary_lines.append(
                    f"CH{no:>2}  {hosts[0]}: reg={sta!r} health={ha}  |  "
                    f"{hosts[1]}: reg={stb!r} health={hb}"
                )
        summary_lines.append("")

    if poll_checks:
        summary_lines.extend(["poll_recorder:", json.dumps(poll_checks, ensure_ascii=False, indent=2)])

    summary_path = out_dir / "SUMMARY.txt"
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
    print(f"SUMMARY -> {summary_path}")
    print("Готово. Каталог raw/ в .gitignore — не коммитьте дампы с внутренними IP.")


if __name__ == "__main__":
    main()
