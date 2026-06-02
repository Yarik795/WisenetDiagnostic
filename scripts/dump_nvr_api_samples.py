#!/usr/bin/env python3
"""Снять сырые ответы SUNAPI по одному NVR каждого типа (для парсеров и новых метрик).

Результат: docs/nvr-samples/raw/<slug>_<host>_<timestamp>.txt
Каталог raw/ в .gitignore — дампы с внутренними IP в репозиторий не кладут.

Перед запуском:
  - В config.json заданы credentials.username и credentials.password (как для опроса NVR).
  - В SAMPLES ниже указаны актуальные host/port (по умолчанию — из docs/nvr-api-check.txt).
  - Есть сетевая доступность регистраторов с машины, где запускается скрипт.

Запуск (из корня проекта, где лежат backend/ и config.json):

  Windows PowerShell:
    cd "D:\\Путь\\К\\Wisenet Диагностика"
    .\\backend\\.venv\\Scripts\\python.exe scripts\\dump_nvr_api_samples.py

  С явным путём к конфигу:
    $env:CONFIG_PATH = ".\\config.json"
    .\\backend\\.venv\\Scripts\\python.exe scripts\\dump_nvr_api_samples.py

  Linux / macOS:
    cd /path/to/project
    ./backend/.venv/bin/python scripts/dump_nvr_api_samples.py

  Только выбранные модели:
    .\\backend\\.venv\\Scripts\\python.exe scripts\\dump_nvr_api_samples.py --slug xrn-3210b2 --slug hrx-1634

  Справка по аргументам:
    .\\backend\\.venv\\Scripts\\python.exe scripts\\dump_nvr_api_samples.py --help

Зависимости: httpx (уже в backend/requirements.txt; venv создаётся по docs/ЗАПУСК.md).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import httpx

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config.json"
OUT_DIR = ROOT / "docs" / "nvr-samples" / "raw"

# По одному регистратору на тип из docs/nvr-api-check.txt и nvr-samples/
SAMPLES: list[dict] = [
    {
        "slug": "hrx-1620",
        "label": "HRX-1620",
        "host": "100.111.22.14",
        "port": 80,
        "use_https": False,
    },
    {
        "slug": "hrx-1634",
        "label": "HRX-1634",
        "host": "10.89.210.104",
        "port": 80,
        "use_https": False,
    },
    {
        "slug": "xrn-2010",
        "label": "XRN-2010",
        "host": "10.89.182.224",
        "port": 80,
        "use_https": False,
    },
    {
        "slug": "xrn-2010p",
        "label": "XRN-2010P",
        "host": "100.111.8.50",
        "port": 80,
        "use_https": False,
    },
    {
        "slug": "xrn-3210b2",
        "label": "XRN-3210B2",
        "host": "100.111.25.196",
        "port": 80,
        "use_https": False,
    },
    {
        "slug": "xrn-6410b2",
        "label": "XRN-6410B2",
        "host": "10.89.7.138",
        "port": 80,
        "use_https": False,
    },
]

# Те же endpoint, что poll_recorder, плюс recording/storage (не было в nvr-api-check)
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
    return user, password


def build_url(sample: dict, cgi: str, submenu: str, action: str, extra: dict[str, str]) -> str:
    scheme = "https" if sample["use_https"] else "http"
    base = f"{scheme}://{sample['host']}:{sample['port']}/stw-cgi/{cgi}"
    return f"{base}?{urlencode({'msubmenu': submenu, 'action': action, **extra})}"


def fetch(client: httpx.Client, url: str, timeout: float) -> tuple[int, str, str | None]:
    try:
        response = client.get(url, timeout=timeout)
        return response.status_code, response.text, None
    except httpx.TimeoutException:
        return 0, "", "timeout"
    except httpx.RequestError as exc:
        return 0, "", str(exc)


def dump_sample(
    client: httpx.Client,
    sample: dict,
    *,
    out_dir: Path,
    timeout: float,
) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = out_dir / f"{sample['slug']}_{sample['host']}_{ts}.txt"
    lines: list[str] = [
        f"# SUNAPI dump {sample['label']} @ {sample['host']}:{sample['port']}",
        f"# UTC {ts}",
        "",
    ]
    for cgi, submenu, action, extra in ENDPOINTS:
        url = build_url(sample, cgi, submenu, action, extra)
        status, body, err = fetch(client, url, timeout)
        lines.extend(
            [
                "=" * 72,
                f"{sample['label']} / {submenu} / {cgi}",
                url,
                f"HTTP: {status}" + (f"  ERROR: {err}" if err else ""),
                "----- BODY START -----",
                body if body else "(empty)",
                "----- BODY END -----",
                "",
            ]
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("CONFIG_PATH", DEFAULT_CONFIG)),
        help="Путь к config.json (по умолчанию CONFIG_PATH или ./config.json)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=OUT_DIR,
        help=f"Каталог для дампов (по умолчанию {OUT_DIR.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--slug",
        action="append",
        dest="slugs",
        metavar="SLUG",
        help="Опросить только указанные slug (можно несколько раз)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=25.0,
        help="Таймаут HTTP, секунды",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    username, password = load_credentials(args.config)

    samples = SAMPLES
    if args.slugs:
        known = {s["slug"] for s in SAMPLES}
        unknown = set(args.slugs) - known
        if unknown:
            raise SystemExit(f"Неизвестный slug: {', '.join(sorted(unknown))}")
        samples = [s for s in SAMPLES if s["slug"] in args.slugs]

    args.out_dir.mkdir(parents=True, exist_ok=True)

    with httpx.Client(auth=httpx.DigestAuth(username, password)) as client:
        for sample in samples:
            print(f"Опрос {sample['label']} {sample['host']} ...", flush=True)
            path = dump_sample(client, sample, out_dir=args.out_dir, timeout=args.timeout)
            print(f"  -> {path}")

    print("Готово. Каталог raw/ в .gitignore — не коммитьте дампы с внутренними IP, если политика запрещает.")


if __name__ == "__main__":
    main()
