#!/usr/bin/env python3
"""Опрос регистраторов из docs/nvr-samples: SerialNumber и расчёт даты производства.

Берёт IP/host из референсных образцов nvr-samples, запрашивает SUNAPI deviceinfo
и применяет алгоритм Samsung к полю SerialNumber (если оно есть в ответе).

Перед запуском:
  - В config.json заданы credentials.username и credentials.password.
  - С машины запуска есть сетевая доступность регистраторов.

Запуск (из корня проекта):

  Windows PowerShell:
    cd "D:\\Путь\\К\\Wisenet Диагностика"
    .\\backend\\.venv\\Scripts\\python.exe scripts\\probe_nvr_manufacture_date.py

  Только один образец:
    .\\backend\\.venv\\Scripts\\python.exe scripts\\probe_nvr_manufacture_date.py --slug xrn-6410b2

  Сохранить JSON-отчёт в docs/nvr-samples/raw/:
    .\\backend\\.venv\\Scripts\\python.exe scripts\\probe_nvr_manufacture_date.py --save-json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import httpx

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.serial_manufacture_date import decode_samsung_manufacture_date  # noqa: E402
from app.sunapi_parsing import parse_key_value_body  # noqa: E402

DEFAULT_CONFIG = ROOT / "config.json"
OUT_DIR = ROOT / "docs" / "nvr-samples" / "raw"

# Хосты из имён файлов docs/nvr-samples/*.md
SAMPLES: list[dict] = [
    {
        "slug": "xrn-2010p",
        "label": "XRN-2010P",
        "host": "100.111.2.2",
        "port": 80,
        "use_https": False,
        "sample_file": "xrn-2010p-100-111-2-2.md",
    },
    {
        "slug": "xrn-3210b2",
        "label": "XRN-3210B2",
        "host": "100.111.25.196",
        "port": 80,
        "use_https": False,
        "sample_file": "xrn-3210b2-100-111-25-196.md",
    },
    {
        "slug": "xrn-6410b2",
        "label": "XRN-6410B2",
        "host": "10.89.7.138",
        "port": 80,
        "use_https": False,
        "sample_file": "xrn-6410b2-10-89-7-138.md",
    },
    {
        "slug": "hrx-1634",
        "label": "HRX-1634",
        "host": "10.89.215.130",
        "port": 80,
        "use_https": False,
        "sample_file": "hrx-1634-10-89-215-130-no-hdd.md",
    },
]


@dataclass
class ProbeResult:
    slug: str
    label: str
    host: str
    port: int
    http_status: int
    error: str | None
    model: str | None
    device_type: str | None
    firmware_version: str | None
    build_date: str | None
    serial_number: str | None
    serial_length: int | None
    manufacture_date: str | None
    decode_rule: str | None
    deviceinfo_url: str


def load_credentials(config_path: Path) -> tuple[str, str]:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    creds = data.get("credentials") or {}
    user = (creds.get("username") or "").strip()
    password = creds.get("password") or ""
    if not user:
        raise SystemExit(f"Нет credentials.username в {config_path}")
    if not password or password == "CHANGE_ME":
        print(
            "Предупреждение: пароль в config.json пустой или CHANGE_ME — опрос может не пройти.",
            file=sys.stderr,
        )
    return user, password


def build_deviceinfo_url(sample: dict) -> str:
    scheme = "https" if sample["use_https"] else "http"
    base = f"{scheme}://{sample['host']}:{sample['port']}/stw-cgi/system.cgi"
    return f"{base}?{urlencode({'msubmenu': 'deviceinfo', 'action': 'view'})}"


def _decode_rule(serial: str | None) -> str | None:
    if not serial:
        return None
    n = len(serial.strip())
    if n == 11:
        return "11-char: pos4=year, pos5=month"
    if n >= 15:
        return "15-char: pos8=year, pos9=month"
    return f"unsupported length {n}"


def probe_one(
    client: httpx.Client,
    sample: dict,
    *,
    timeout: float,
) -> ProbeResult:
    url = build_deviceinfo_url(sample)
    try:
        response = client.get(url, timeout=timeout)
        status = response.status_code
        body = response.text
        err = None if status == 200 else f"HTTP {status}"
    except httpx.TimeoutException:
        return ProbeResult(
            slug=sample["slug"],
            label=sample["label"],
            host=sample["host"],
            port=sample["port"],
            http_status=0,
            error="timeout",
            model=None,
            device_type=None,
            firmware_version=None,
            build_date=None,
            serial_number=None,
            serial_length=None,
            manufacture_date=None,
            decode_rule=None,
            deviceinfo_url=url,
        )
    except httpx.RequestError as exc:
        return ProbeResult(
            slug=sample["slug"],
            label=sample["label"],
            host=sample["host"],
            port=sample["port"],
            http_status=0,
            error=str(exc),
            model=None,
            device_type=None,
            firmware_version=None,
            build_date=None,
            serial_number=None,
            serial_length=None,
            manufacture_date=None,
            decode_rule=None,
            deviceinfo_url=url,
        )

    fields = parse_key_value_body(body) if status == 200 and body.strip() else {}
    serial = (fields.get("SerialNumber") or "").strip() or None
    mfg: str | None = None
    if serial:
        decoded = decode_samsung_manufacture_date(serial)
        if decoded:
            mfg = decoded.strftime("%Y-%m")

    return ProbeResult(
        slug=sample["slug"],
        label=sample["label"],
        host=sample["host"],
        port=sample["port"],
        http_status=status,
        error=err,
        model=fields.get("Model"),
        device_type=fields.get("DeviceType"),
        firmware_version=fields.get("FirmwareVersion"),
        build_date=fields.get("BuildDate"),
        serial_number=serial,
        serial_length=len(serial) if serial else None,
        manufacture_date=mfg,
        decode_rule=_decode_rule(serial),
        deviceinfo_url=url,
    )


def _print_table(results: list[ProbeResult]) -> None:
    cols = [
        ("slug", 14),
        ("host", 18),
        ("model", 14),
        ("serial", 18),
        ("mfg_date", 10),
        ("build_date", 12),
        ("status", 8),
    ]
    header = " ".join(name.ljust(w) for name, w in cols)
    print(header)
    print("-" * len(header))
    for r in results:
        status = "OK" if r.error is None and r.http_status == 200 else (r.error or "ERR")
        serial = (r.serial_number or "—")[:18]
        print(
            f"{r.slug[:14]:<14} "
            f"{r.host:<18} "
            f"{(r.model or '—')[:14]:<14} "
            f"{serial:<18} "
            f"{(r.manufacture_date or '—'):<10} "
            f"{(r.build_date or '—')[:12]:<12} "
            f"{status:<8}"
        )
    print()
    for r in results:
        if r.serial_number and not r.manufacture_date:
            print(
                f"  [{r.slug}] SerialNumber={r.serial_number!r} — "
                f"дата не распознана ({r.decode_rule})"
            )
        if r.http_status == 200 and not r.serial_number:
            print(f"  [{r.slug}] deviceinfo без SerialNumber (BuildDate={r.build_date!r})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("CONFIG_PATH", DEFAULT_CONFIG)),
        help="Путь к config.json",
    )
    parser.add_argument(
        "--slug",
        action="append",
        dest="slugs",
        metavar="SLUG",
        help="Опросить только указанный slug (можно несколько раз)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="Таймаут HTTP, секунды",
    )
    parser.add_argument(
        "--save-json",
        action="store_true",
        help=f"Сохранить JSON в {OUT_DIR.relative_to(ROOT)}/manufacture_probe_<ts>.json",
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

    results: list[ProbeResult] = []
    with httpx.Client(auth=httpx.DigestAuth(username, password)) as client:
        for sample in samples:
            print(f"Опрос {sample['label']} @ {sample['host']} ...", flush=True)
            result = probe_one(client, sample, timeout=args.timeout)
            results.append(result)
            if result.error:
                print(f"  ошибка: {result.error}", flush=True)
            elif result.serial_number:
                print(
                    f"  S/N={result.serial_number} → "
                    f"производство={result.manufacture_date or 'не распознано'} "
                    f"(BuildDate прошивки={result.build_date})",
                    flush=True,
                )
            else:
                print(
                    f"  SerialNumber отсутствует (BuildDate={result.build_date})",
                    flush=True,
                )

    print()
    _print_table(results)

    if args.save_json:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out_path = OUT_DIR / f"manufacture_probe_{ts}.json"
        payload = {
            "probed_at": ts,
            "samples_source": "docs/nvr-samples",
            "results": [asdict(r) for r in results],
        }
        out_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"JSON: {out_path}")


if __name__ == "__main__":
    main()
