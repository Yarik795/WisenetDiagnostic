#!/usr/bin/env python3
"""Опрос NVR: SerialNumber из deviceinfo и расчёт даты производства (Samsung S/N).

По умолчанию опрашивает все регистраторы из config.json (кроме исключённых),
как в инвентаре Wisenet Диагностика. Режим --samples — только 4 эталона из
docs/nvr-samples.

Перед запуском:
  - В config.json заданы credentials и список recorders.
  - Есть сетевая доступность регистраторов с машины запуска.

Запуск (из корня проекта):

  Windows PowerShell:
    cd "D:\\Путь\\К\\Wisenet Диагностика"
    .\\backend\\.venv\\Scripts\\python.exe scripts\\probe_nvr_manufacture_date.py --save-json

  Только эталоны nvr-samples:
    .\\backend\\.venv\\Scripts\\python.exe scripts\\probe_nvr_manufacture_date.py --samples

  Один хост:
    .\\backend\\.venv\\Scripts\\python.exe scripts\\probe_nvr_manufacture_date.py --host 10.89.7.138

  Параллелизм (как в мониторинге):
    .\\backend\\.venv\\Scripts\\python.exe scripts\\probe_nvr_manufacture_date.py --workers 10
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import httpx

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.exclusions import migrate_config_raw  # noqa: E402
from app.serial_manufacture_date import (  # noqa: E402
    resolve_manufacture_date,
    should_store_serial_metrics,
)
from app.sunapi_parsing import parse_key_value_body  # noqa: E402

DEFAULT_CONFIG = ROOT / "config.json"
OUT_DIR = ROOT / "docs" / "nvr-samples" / "raw"

# Эталоны из docs/nvr-samples/*.md (режим --samples)
NVR_SAMPLES: list[dict] = [
    {
        "id": "sample-xrn-2010p",
        "slug": "xrn-2010p",
        "label": "XRN-2010P",
        "host": "100.111.2.2",
        "port": 80,
        "use_https": False,
        "object_name": "nvr-samples",
    },
    {
        "id": "sample-xrn-3210b2",
        "slug": "xrn-3210b2",
        "label": "XRN-3210B2",
        "host": "100.111.25.196",
        "port": 80,
        "use_https": False,
        "object_name": "nvr-samples",
    },
    {
        "id": "sample-xrn-6410b2",
        "slug": "xrn-6410b2",
        "label": "XRN-6410B2",
        "host": "10.89.7.138",
        "port": 80,
        "use_https": False,
        "object_name": "nvr-samples",
    },
    {
        "id": "sample-hrx-1634",
        "slug": "hrx-1634",
        "label": "HRX-1634",
        "host": "10.89.215.130",
        "port": 80,
        "use_https": False,
        "object_name": "nvr-samples",
    },
]


@dataclass
class ProbeResult:
    recorder_id: str
    slug: str
    label: str
    object_name: str | None
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


def load_config(config_path: Path) -> dict:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return migrate_config_raw(data)


def load_credentials(config: dict, config_path: Path) -> tuple[str, str]:
    creds = config.get("credentials") or {}
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


def load_targets_from_config(
    config: dict,
    *,
    include_excluded: bool = False,
) -> list[dict]:
    excluded = set((config.get("exclusions") or {}).get("recorder_ids") or [])
    targets: list[dict] = []
    for rec in config.get("recorders") or []:
        if not isinstance(rec, dict):
            continue
        rid = (rec.get("id") or "").strip()
        host = (rec.get("host") or "").strip()
        if not rid or not host:
            continue
        if not include_excluded and rid in excluded:
            continue
        name = (rec.get("name") or "").strip() or host
        label = name
        # В UI часто «XRN-3210B2 100.111.25.196»
        if host not in name:
            label = f"{name} {host}".strip()

        targets.append(
            {
                "id": rid,
                "slug": rid,
                "label": label,
                "host": host,
                "port": int(rec.get("port") or 80),
                "use_https": bool(rec.get("use_https")),
                "object_name": (rec.get("object_name") or "").strip() or None,
            }
        )
    return targets


def build_deviceinfo_url(target: dict) -> str:
    scheme = "https" if target["use_https"] else "http"
    base = f"{scheme}://{target['host']}:{target['port']}/stw-cgi/system.cgi"
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
    target: dict,
    *,
    username: str,
    password: str,
    timeout: float,
) -> ProbeResult:
    url = build_deviceinfo_url(target)
    try:
        with httpx.Client(auth=httpx.DigestAuth(username, password)) as client:
            response = client.get(url, timeout=timeout)
        status = response.status_code
        body = response.text
        err = None if status == 200 else f"HTTP {status}"
    except httpx.TimeoutException:
        return _error_result(target, url, "timeout")
    except httpx.RequestError as exc:
        return _error_result(target, url, str(exc))

    fields = parse_key_value_body(body) if status == 200 and body.strip() else {}
    device_type = fields.get("DeviceType")
    raw_serial = (fields.get("SerialNumber") or "").strip() or None
    serial = raw_serial if should_store_serial_metrics(device_type, raw_serial) else None
    mfg = resolve_manufacture_date(raw_serial, device_type) if serial else None

    return ProbeResult(
        recorder_id=target["id"],
        slug=target["slug"],
        label=target["label"],
        object_name=target.get("object_name"),
        host=target["host"],
        port=target["port"],
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


def _error_result(target: dict, url: str, error: str) -> ProbeResult:
    return ProbeResult(
        recorder_id=target["id"],
        slug=target["slug"],
        label=target["label"],
        object_name=target.get("object_name"),
        host=target["host"],
        port=target["port"],
        http_status=0,
        error=error,
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


def _print_summary(results: list[ProbeResult]) -> None:
    total = len(results)
    ok = sum(1 for r in results if r.error is None and r.http_status == 200)
    with_serial = sum(1 for r in results if r.serial_number)
    with_mfg = sum(1 for r in results if r.manufacture_date)
    no_serial = sum(
        1 for r in results if r.error is None and r.http_status == 200 and not r.serial_number
    )
    decode_fail = sum(
        1 for r in results if r.serial_number and not r.manufacture_date
    )
    failed = total - ok

    print("--- Сводка ---")
    print(f"  Всего:              {total}")
    print(f"  deviceinfo OK:      {ok}")
    print(f"  Ошибки/таймаут:     {failed}")
    print(f"  С SerialNumber:     {with_serial}")
    print(f"  Дата распознана:    {with_mfg}")
    print(f"  Без SerialNumber:   {no_serial}")
    print(f"  S/N не декодирован: {decode_fail}")

    by_model: dict[str, dict[str, int]] = {}
    for r in results:
        if r.error is not None or r.http_status != 200:
            continue
        model = r.model or "?"
        bucket = by_model.setdefault(model, {"total": 0, "serial": 0, "mfg": 0})
        bucket["total"] += 1
        if r.serial_number:
            bucket["serial"] += 1
        if r.manufacture_date:
            bucket["mfg"] += 1

    if by_model:
        print("\n--- По модели (успешный deviceinfo) ---")
        for model in sorted(by_model):
            b = by_model[model]
            print(
                f"  {model}: {b['total']} шт., "
                f"S/N={b['serial']}, дата={b['mfg']}"
            )


def _print_table(results: list[ProbeResult]) -> None:
    cols = [
        ("host", 18),
        ("model", 14),
        ("serial", 18),
        ("mfg_date", 10),
        ("build_date", 12),
        ("status", 10),
    ]
    header = " ".join(name.ljust(w) for name, w in cols)
    print(header)
    print("-" * len(header))
    for r in results:
        status = "OK" if r.error is None and r.http_status == 200 else (r.error or "ERR")
        serial = (r.serial_number or "—")[:18]
        print(
            f"{r.host:<18} "
            f"{(r.model or '—')[:14]:<14} "
            f"{serial:<18} "
            f"{(r.manufacture_date or '—'):<10} "
            f"{(r.build_date or '—')[:12]:<12} "
            f"{str(status)[:10]:<10}"
        )


def _print_notes(results: list[ProbeResult]) -> None:
    for r in results:
        if r.serial_number and not r.manufacture_date:
            print(
                f"  [{r.host}] SerialNumber={r.serial_number!r} — "
                f"дата не распознана ({r.decode_rule})"
            )
        if r.http_status == 200 and not r.serial_number:
            hint = (
                f"DeviceType={r.device_type!r} — не регистратор"
                if r.device_type and r.device_type.upper() not in {"NVR", "DVR", "HYBRID"}
                else "нет SerialNumber в deviceinfo"
            )
            print(
                f"  [{r.host}] {r.model or '?'} — "
                f"{hint} (BuildDate={r.build_date!r})"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("CONFIG_PATH", DEFAULT_CONFIG)),
        help="Путь к config.json",
    )
    parser.add_argument(
        "--samples",
        action="store_true",
        help="Только 4 эталона из docs/nvr-samples (не весь инвентарь)",
    )
    parser.add_argument(
        "--include-excluded",
        action="store_true",
        help="Включить NVR из exclusions.recorder_ids",
    )
    parser.add_argument(
        "--host",
        action="append",
        dest="hosts",
        metavar="IP",
        help="Опросить только указанные IP (можно несколько раз)",
    )
    parser.add_argument(
        "--slug",
        action="append",
        dest="slugs",
        metavar="ID",
        help="Фильтр по recorder id / sample slug",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        metavar="N",
        help="Опросить не более N устройств (0 = без ограничения)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        metavar="N",
        help="Параллельных HTTP-запросов (по умолчанию 5)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="Таймаут HTTP, секунды",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Строка на каждый NVR при опросе",
    )
    parser.add_argument(
        "--save-json",
        action="store_true",
        help=f"Сохранить JSON в {OUT_DIR.relative_to(ROOT)}/manufacture_probe_<ts>.json",
    )
    return parser.parse_args()


def _filter_targets(targets: list[dict], args: argparse.Namespace) -> list[dict]:
    filtered = targets
    if args.hosts:
        host_set = set(args.hosts)
        filtered = [t for t in filtered if t["host"] in host_set]
    if args.slugs:
        slug_set = set(args.slugs)
        filtered = [
            t
            for t in filtered
            if t["slug"] in slug_set
            or t["id"] in slug_set
            or any(s in t["label"].lower() for s in slug_set)
        ]
    if args.limit and args.limit > 0:
        filtered = filtered[: args.limit]
    return filtered


def main() -> None:
    args = parse_args()
    if not args.config.is_file():
        raise SystemExit(f"Нет файла конфигурации: {args.config}")

    config = load_config(args.config)
    username, password = load_credentials(config, args.config)

    if args.samples:
        targets = list(NVR_SAMPLES)
        source = "docs/nvr-samples"
    else:
        targets = load_targets_from_config(
            config, include_excluded=args.include_excluded
        )
        source = str(args.config)

    targets = _filter_targets(targets, args)
    if not targets:
        raise SystemExit("Нет устройств для опроса (проверьте фильтры и config.json).")

    print(
        f"Опрос {len(targets)} NVR ({source}), workers={args.workers}, "
        f"timeout={args.timeout}s",
        flush=True,
    )

    results: list[ProbeResult] = []
    done = 0
    workers = max(1, args.workers)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(
                probe_one,
                target,
                username=username,
                password=password,
                timeout=args.timeout,
            ): target
            for target in targets
        }
        for future in as_completed(futures):
            target = futures[future]
            result = future.result()
            results.append(result)
            done += 1

            if args.verbose:
                if result.error:
                    line = f"ошибка: {result.error}"
                elif result.serial_number:
                    line = (
                        f"S/N={result.serial_number} → "
                        f"{result.manufacture_date or 'дата не распознана'}"
                    )
                else:
                    line = f"нет SerialNumber, BuildDate={result.build_date}"
                print(f"[{done}/{len(targets)}] {result.host} {line}", flush=True)
            elif done % 25 == 0 or done == len(targets):
                print(f"  … {done}/{len(targets)}", flush=True)

    results.sort(key=lambda r: (r.object_name or "", r.host))

    print()
    _print_summary(results)

    if len(results) <= 50 or args.verbose:
        print()
        _print_table(results)
        print()
        _print_notes(results)
    else:
        print("\n(таблица скрыта: >50 NVR; добавьте --verbose или --host для деталей)")

    if args.save_json:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out_path = OUT_DIR / f"manufacture_probe_{ts}.json"
        payload = {
            "probed_at": ts,
            "source": source,
            "total": len(results),
            "results": [asdict(r) for r in results],
        }
        out_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nJSON: {out_path}")


if __name__ == "__main__":
    main()
