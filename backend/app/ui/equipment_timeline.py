"""Общая логика отчётов «по времени»: регистраторы (дата пр-ва) и диски (наработка)."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Any, Literal, Optional

from ..camera_manufacturer_lookup import (
    camera_brand_label,
    is_analog_camera_channel,
    resolve_camera_manufacturer,
    resolve_camera_model_display,
)
from ..config_store import ConfigStore
from ..device_kinds import recorder_device_kind
from ..models import Recorder
from ..state_store import ChannelRow, RecorderMetricsRow, StateStore
from .grouping import metrics_map_from_list
from .metrics_helpers import (
    disk_field,
    disk_power_on_hours_raw,
    disk_slot,
    format_manufacture_date,
    parse_disks_json,
)

PeriodGrouping = Literal["month", "quarter", "year"]
BucketYears = Literal["0.5", "1", "2"]

_CHART_COLORS = [
    "#3b82f6",
    "#10b981",
    "#f59e0b",
    "#ef4444",
    "#8b5cf6",
    "#06b6d4",
    "#ec4899",
    "#84cc16",
    "#f97316",
    "#6366f1",
]

_HOURS_PER_YEAR = 8760.0
_MANUFACTURE_RE = re.compile(r"^(\d{4})-(\d{2})$")
_LEGACY_WEAR_MODEL_PREFIXES = ("HRX-1620", "XRN-2010")


@dataclass(frozen=True)
class RecorderWithMetrics:
    recorder: Recorder
    metrics: Optional[RecorderMetricsRow]


@dataclass(frozen=True)
class DiskWearRow:
    recorder_id: str
    object_name: str
    recorder_name: Optional[str]
    host: str
    nvr_model: Optional[str]
    disk_slot: str
    disk_model: Optional[str]
    power_on_hours: int


def chart_color(index: int) -> str:
    return _CHART_COLORS[index % len(_CHART_COLORS)]


def list_tsv_recorders_with_metrics(
    store: ConfigStore,
    state: StateStore,
) -> list[RecorderWithMetrics]:
    metrics_map = metrics_map_from_list(state.list_recorder_metrics())
    items: list[RecorderWithMetrics] = []
    for recorder in store.list_recorders():
        if recorder_device_kind(recorder) != "tsv":
            continue
        items.append(
            RecorderWithMetrics(recorder, metrics_map.get(recorder.id))
        )
    return items


def parse_manufacture_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    m = _MANUFACTURE_RE.match(value.strip())
    if not m:
        return None
    year = int(m.group(1))
    month = int(m.group(2))
    if month < 1 or month > 12:
        return None
    return date(year, month, 1)


def period_key(d: date, grouping: PeriodGrouping) -> str:
    if grouping == "year":
        return f"{d.year:04d}"
    if grouping == "quarter":
        quarter = (d.month - 1) // 3 + 1
        return f"{d.year:04d}-Q{quarter}"
    return f"{d.year:04d}-{d.month:02d}"


def format_period_label(key: str, grouping: PeriodGrouping) -> str:
    if grouping == "year":
        return key
    if grouping == "quarter":
        year_s, _, q_s = key.partition("-Q")
        if year_s and q_s.isdigit():
            return f"{q_s} кв. {year_s}"
        return key
    parsed = parse_manufacture_date(key)
    if parsed:
        return format_manufacture_date(key)
    return key


def _period_sort_key(key: str, grouping: PeriodGrouping) -> tuple[int, int]:
    if grouping == "year":
        return (int(key), 0)
    if grouping == "quarter":
        year_s, _, q_s = key.partition("-Q")
        return (int(year_s), int(q_s) if q_s.isdigit() else 0)
    parsed = parse_manufacture_date(key)
    if parsed:
        return (parsed.year, parsed.month)
    return (0, 0)


def period_in_range(
    key: str,
    grouping: PeriodGrouping,
    from_key: str,
    to_key: str,
) -> bool:
    if not from_key and not to_key:
        return True
    sort_key = _period_sort_key(key, grouping)
    if from_key:
        if sort_key < _period_sort_key(from_key, grouping):
            return False
    if to_key:
        if sort_key > _period_sort_key(to_key, grouping):
            return False
    return True


def normalize_period_filter(value: str, grouping: PeriodGrouping) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if grouping == "year":
        m = re.match(r"^(\d{4})", value)
        return m.group(1) if m else value
    if grouping == "quarter":
        m = re.match(r"^(\d{4})-Q([1-4])$", value, re.IGNORECASE)
        if m:
            return f"{m.group(1)}-Q{m.group(2)}"
        parsed = parse_manufacture_date(value)
        if parsed:
            quarter = (parsed.month - 1) // 3 + 1
            return f"{parsed.year:04d}-Q{quarter}"
        return value
    m = _MANUFACTURE_RE.match(value)
    if m:
        return value
    parsed = parse_manufacture_date(value)
    return value if parsed else ""


def recorder_model(item: RecorderWithMetrics) -> Optional[str]:
    if item.metrics and item.metrics.model:
        return item.metrics.model
    return None


def recorder_manufacture_date(item: RecorderWithMetrics) -> Optional[str]:
    if item.metrics and item.metrics.manufacture_date:
        return item.metrics.manufacture_date
    return None


def filter_recorders_by_model(
    items: list[RecorderWithMetrics],
    model: str,
) -> list[RecorderWithMetrics]:
    if not model:
        return items
    return [item for item in items if recorder_model(item) == model]


def aggregate_recorders_by_period(
    items: list[RecorderWithMetrics],
    *,
    grouping: PeriodGrouping = "month",
    from_key: str = "",
    to_key: str = "",
    model: str = "",
) -> dict[str, Any]:
    filtered = filter_recorders_by_model(items, model)
    counter: Counter[str] = Counter()
    for item in filtered:
        mfg = recorder_manufacture_date(item)
        parsed = parse_manufacture_date(mfg)
        if not parsed:
            continue
        key = period_key(parsed, grouping)
        if not period_in_range(key, grouping, from_key, to_key):
            continue
        counter[key] += 1

    keys = sorted(counter.keys(), key=lambda k: _period_sort_key(k, grouping))
    labels = [format_period_label(k, grouping) for k in keys]
    values = [counter[k] for k in keys]
    colors = {k: chart_color(idx) for idx, k in enumerate(keys)}
    return {
        "labels": labels,
        "values": values,
        "keys": keys,
        "colors": colors,
    }


def recorder_age_detail_rows(
    items: list[RecorderWithMetrics],
    *,
    period: str,
    grouping: PeriodGrouping = "month",
    from_key: str = "",
    to_key: str = "",
    model: str = "",
) -> list[dict[str, Any]]:
    filtered = filter_recorders_by_model(items, model)
    rows: list[dict[str, Any]] = []
    for item in filtered:
        mfg = recorder_manufacture_date(item)
        parsed = parse_manufacture_date(mfg)
        if not parsed:
            continue
        key = period_key(parsed, grouping)
        if key != period:
            continue
        if not period_in_range(key, grouping, from_key, to_key):
            continue
        rec = item.recorder
        rows.append(
            {
                "object_name": rec.object_name,
                "recorder_name": rec.name or rec.host,
                "host": rec.host,
                "model": recorder_model(item) or "—",
                "serial_number": (
                    item.metrics.serial_number if item.metrics else None
                )
                or "—",
                "manufacture_date": mfg or "—",
                "metric_label": "Дата пр-ва",
                "metric_value": format_manufacture_date(mfg) if mfg else "—",
            }
        )
    rows.sort(key=lambda r: (r["object_name"], r["recorder_name"]))
    return rows


def recorder_age_missing_rows(
    items: list[RecorderWithMetrics],
    *,
    model: str = "",
) -> list[dict[str, Any]]:
    filtered = filter_recorders_by_model(items, model)
    rows: list[dict[str, Any]] = []
    for item in filtered:
        mfg = recorder_manufacture_date(item)
        if parse_manufacture_date(mfg):
            continue
        rec = item.recorder
        rows.append(
            {
                "object_name": rec.object_name,
                "recorder_name": rec.name or rec.host,
                "host": rec.host,
                "model": recorder_model(item) or "—",
                "serial_number": (
                    item.metrics.serial_number if item.metrics else None
                )
                or "—",
                "manufacture_date": mfg or "—",
                "metric_label": "Дата пр-ва",
                "metric_value": "—",
            }
        )
    rows.sort(key=lambda r: (r["object_name"], r["recorder_name"]))
    return rows


def explode_disk_rows(items: list[RecorderWithMetrics]) -> list[DiskWearRow]:
    rows: list[DiskWearRow] = []
    for item in items:
        metrics = item.metrics
        if not metrics or not metrics.disks_json:
            continue
        rec = item.recorder
        for disk in parse_disks_json(metrics.disks_json):
            hours = disk_power_on_hours_raw(disk)
            if hours is None:
                continue
            rows.append(
                DiskWearRow(
                    recorder_id=rec.id,
                    object_name=rec.object_name,
                    recorder_name=rec.name,
                    host=rec.host,
                    nvr_model=metrics.model,
                    disk_slot=disk_slot(disk),
                    disk_model=disk_field(disk, "Model", "model"),
                    power_on_hours=hours,
                )
            )
    return rows


def wear_years_from_hours(hours: int) -> float:
    return hours / _HOURS_PER_YEAR


def bucket_size_years(bucket: BucketYears) -> float:
    return {"0.5": 0.5, "1": 1.0, "2": 2.0}[bucket]


def wear_bucket_key(hours: int, bucket_years: float) -> str:
    years = wear_years_from_hours(hours)
    index = int(math.floor(years / bucket_years))
    start = index * bucket_years
    end = start + bucket_years
    return f"{start:g}-{end:g}"


def format_wear_bucket_label(key: str) -> str:
    start_s, _, end_s = key.partition("-")
    try:
        start = float(start_s)
        end = float(end_s)
    except ValueError:
        return key
    return f"{start:g}–{end:g} лет"


def _wear_bucket_sort_key(key: str) -> float:
    start_s = key.split("-", 1)[0]
    try:
        return float(start_s)
    except ValueError:
        return 0.0


def wear_in_range(
    hours: int,
    *,
    min_years: Optional[float],
    max_years: Optional[float],
) -> bool:
    years = wear_years_from_hours(hours)
    if min_years is not None and years < min_years:
        return False
    if max_years is not None and years > max_years:
        return False
    return True


def filter_disks_by_model(
    disks: list[DiskWearRow],
    model: str,
) -> list[DiskWearRow]:
    if not model:
        return disks
    return [d for d in disks if (d.disk_model or "") == model]


def aggregate_disks_by_wear(
    disks: list[DiskWearRow],
    *,
    bucket: BucketYears = "1",
    min_years: Optional[float] = None,
    max_years: Optional[float] = None,
    model: str = "",
) -> dict[str, Any]:
    bucket_years = bucket_size_years(bucket)
    filtered = filter_disks_by_model(disks, model)
    counter: Counter[str] = Counter()
    for row in filtered:
        if not wear_in_range(row.power_on_hours, min_years=min_years, max_years=max_years):
            continue
        counter[wear_bucket_key(row.power_on_hours, bucket_years)] += 1

    keys = sorted(counter.keys(), key=_wear_bucket_sort_key)
    labels = [format_wear_bucket_label(k) for k in keys]
    values = [counter[k] for k in keys]
    colors = {k: chart_color(idx) for idx, k in enumerate(keys)}
    return {
        "labels": labels,
        "values": values,
        "keys": keys,
        "colors": colors,
        "bucket_years": bucket_years,
    }


def disk_wear_detail_rows(
    disks: list[DiskWearRow],
    *,
    bucket_key: str,
    bucket: BucketYears = "1",
    min_years: Optional[float] = None,
    max_years: Optional[float] = None,
    model: str = "",
) -> list[dict[str, Any]]:
    bucket_years = bucket_size_years(bucket)
    filtered = filter_disks_by_model(disks, model)
    rows: list[dict[str, Any]] = []
    for row in filtered:
        if not wear_in_range(row.power_on_hours, min_years=min_years, max_years=max_years):
            continue
        key = wear_bucket_key(row.power_on_hours, bucket_years)
        if key != bucket_key:
            continue
        years = wear_years_from_hours(row.power_on_hours)
        rows.append(
            {
                "object_name": row.object_name,
                "recorder_name": row.recorder_name or row.host,
                "host": row.host,
                "nvr_model": row.nvr_model or "—",
                "disk_slot": row.disk_slot,
                "disk_model": row.disk_model or "—",
                "power_on_hours": row.power_on_hours,
                "wear_years": round(years, 1),
                "metric_label": "Наработка",
                "metric_value": f"{row.power_on_hours} ч ({years:.1f} лет)",
            }
        )
    rows.sort(
        key=lambda r: (r["object_name"], r["recorder_name"], r["disk_slot"])
    )
    return rows


def _legacy_wear_unavailable(nvr_model: Optional[str]) -> bool:
    if not nvr_model:
        return False
    model_upper = nvr_model.strip().upper()
    return any(
        model_upper.startswith(prefix) for prefix in _LEGACY_WEAR_MODEL_PREFIXES
    )


def disk_wear_missing_rows(
    items: list[RecorderWithMetrics],
    *,
    model: str = "",
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in items:
        metrics = item.metrics
        if not metrics or not metrics.disks_json:
            continue
        rec = item.recorder
        for disk in parse_disks_json(metrics.disks_json):
            if disk_power_on_hours_raw(disk) is not None:
                continue
            disk_model = disk_field(disk, "Model", "model") or "—"
            if model and disk_model != model:
                continue
            nvr_model = metrics.model or "—"
            legacy_unavailable = _legacy_wear_unavailable(metrics.model)
            rows.append(
                {
                    "object_name": rec.object_name,
                    "recorder_name": rec.name or rec.host,
                    "host": rec.host,
                    "nvr_model": nvr_model,
                    "disk_slot": disk_slot(disk),
                    "disk_model": disk_model,
                    "metric_label": "Наработка",
                    "metric_value": (
                        "— (SUNAPI CGI 2.5.x)"
                        if legacy_unavailable
                        else "—"
                    ),
                    "wear_unavailable_reason": (
                        "Наработка недоступна через SUNAPI (CGI 2.5.x)"
                        if legacy_unavailable
                        else None
                    ),
                }
            )
    rows.sort(
        key=lambda r: (r["object_name"], r["recorder_name"], r["disk_slot"])
    )
    return rows


def distinct_recorder_models(items: list[RecorderWithMetrics]) -> list[str]:
    models = sorted(
        {m for item in items if (m := recorder_model(item))}
    )
    return models


def distinct_disk_models(disks: list[DiskWearRow]) -> list[str]:
    return sorted({d.disk_model for d in disks if d.disk_model})


def recorder_age_kpi(items: list[RecorderWithMetrics], *, model: str = "") -> dict[str, Any]:
    filtered = filter_recorders_by_model(items, model)
    with_date = 0
    without_date = 0
    periods: list[tuple[int, int]] = []
    for item in filtered:
        mfg = recorder_manufacture_date(item)
        if mfg and parse_manufacture_date(mfg):
            with_date += 1
            parsed = parse_manufacture_date(mfg)
            assert parsed is not None
            periods.append((parsed.year, parsed.month))
        else:
            without_date += 1
    oldest = newest = "—"
    if periods:
        periods.sort()
        oldest = format_manufacture_date(f"{periods[0][0]:04d}-{periods[0][1]:02d}")
        newest = format_manufacture_date(
            f"{periods[-1][0]:04d}-{periods[-1][1]:02d}"
        )
    return {
        "total_recorders": len(filtered),
        "with_date": with_date,
        "without_date": without_date,
        "oldest": oldest,
        "newest": newest,
    }


def disk_wear_kpi(
    items: list[RecorderWithMetrics],
    disks: list[DiskWearRow],
    *,
    model: str = "",
) -> dict[str, Any]:
    filtered_disks = filter_disks_by_model(disks, model)
    slots_total = sum(
        len(parse_disks_json(item.metrics.disks_json))
        for item in items
        if item.metrics and item.metrics.disks_json
    )
    with_wear = len(filtered_disks)
    without_wear = max(slots_total - with_wear, 0)
    avg_years = 0.0
    if with_wear:
        avg_years = round(
            sum(wear_years_from_hours(d.power_on_hours) for d in filtered_disks)
            / with_wear,
            1,
        )
    return {
        "total_disks": slots_total,
        "with_wear": with_wear,
        "without_wear": without_wear,
        "avg_years": avg_years,
    }


def objects_for_period(
    detail_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Сводка по object_name для drill-down."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in detail_rows:
        grouped[row["object_name"]].append(row)
    summary: list[dict[str, Any]] = []
    for object_name, rows in sorted(grouped.items()):
        summary.append(
            {
                "object_name": object_name,
                "device_count": len(rows),
                "rows": rows,
            }
        )
    return summary


@dataclass(frozen=True)
class CameraWithContext:
    channel: ChannelRow
    recorder: Recorder


def list_tsv_cameras_with_context(
    store: ConfigStore,
    state: StateStore,
) -> list[CameraWithContext]:
    recorders = {
        r.id: r
        for r in store.list_recorders()
        if recorder_device_kind(r) == "tsv"
    }
    items: list[CameraWithContext] = []
    for channel in state.list_channels():
        if (channel.source_state or "").strip().lower() == "deactive":
            continue
        has_ip = bool((channel.camera_ip or "").strip())
        if not has_ip and not is_analog_camera_channel(channel):
            continue
        recorder = recorders.get(channel.recorder_id)
        if recorder is None:
            continue
        items.append(CameraWithContext(channel, recorder))
    return items


def camera_model(item: CameraWithContext) -> Optional[str]:
    return resolve_camera_model_display(item.channel)


def camera_manufacturer(item: CameraWithContext) -> Optional[str]:
    return resolve_camera_manufacturer(item.channel)


def camera_manufacture_date(item: CameraWithContext) -> Optional[str]:
    return item.channel.manufacture_date


def filter_cameras_by_model(
    items: list[CameraWithContext],
    model: str,
) -> list[CameraWithContext]:
    if not model:
        return items
    return [item for item in items if camera_model(item) == model]


def filter_cameras_by_brand(
    items: list[CameraWithContext],
    brand: str,
) -> list[CameraWithContext]:
    if not brand:
        return items
    return [item for item in items if (camera_manufacturer(item) or "") == brand]


def aggregate_cameras_by_period(
    items: list[CameraWithContext],
    *,
    grouping: PeriodGrouping = "month",
    from_key: str = "",
    to_key: str = "",
    model: str = "",
    brand: str = "",
) -> dict[str, Any]:
    filtered = filter_cameras_by_brand(filter_cameras_by_model(items, model), brand)
    counter: Counter[str] = Counter()
    for item in filtered:
        mfg = camera_manufacture_date(item)
        parsed = parse_manufacture_date(mfg)
        if not parsed:
            continue
        key = period_key(parsed, grouping)
        if not period_in_range(key, grouping, from_key, to_key):
            continue
        counter[key] += 1

    keys = sorted(counter.keys(), key=lambda k: _period_sort_key(k, grouping))
    labels = [format_period_label(k, grouping) for k in keys]
    values = [counter[k] for k in keys]
    colors = {k: chart_color(idx) for idx, k in enumerate(keys)}
    return {
        "labels": labels,
        "values": values,
        "keys": keys,
        "colors": colors,
    }


def _date_source_label(source: Optional[str]) -> str:
    if source == "firmware_build":
        return "сборка прошивки"
    if source == "serial_decode":
        return "S/N"
    return "—"


def _camera_missing_date_reason(item: CameraWithContext) -> str:
    ch = item.channel
    if is_analog_camera_channel(ch):
        return "аналоговая камера — дата производства недоступна"
    if ch.camera_inventory_error:
        return ch.camera_inventory_error
    mfg = camera_manufacture_date(item)
    if mfg and not parse_manufacture_date(mfg):
        return "невалидная дата"
    return "нет данных"


def camera_age_detail_rows(
    items: list[CameraWithContext],
    *,
    period: str,
    grouping: PeriodGrouping = "month",
    from_key: str = "",
    to_key: str = "",
    model: str = "",
    brand: str = "",
) -> list[dict[str, Any]]:
    filtered = filter_cameras_by_brand(filter_cameras_by_model(items, model), brand)
    rows: list[dict[str, Any]] = []
    for item in filtered:
        mfg = camera_manufacture_date(item)
        parsed = parse_manufacture_date(mfg)
        if not parsed:
            continue
        key = period_key(parsed, grouping)
        if key != period:
            continue
        if not period_in_range(key, grouping, from_key, to_key):
            continue
        ch = item.channel
        rec = item.recorder
        rows.append(
            {
                "object_name": rec.object_name,
                "recorder_name": rec.name or rec.host,
                "channel_name": ch.name or f"Канал {ch.channel_no + 1}",
                "camera_ip": ch.camera_ip or "—",
                "model": camera_model(item) or "—",
                "manufacturer": camera_manufacturer(item) or "—",
                "serial_number": ch.camera_serial or "—",
                "manufacture_date": mfg or "—",
                "date_source": _date_source_label(ch.manufacture_date_source),
                "metric_value": format_manufacture_date(mfg) if mfg else "—",
            }
        )
    rows.sort(key=lambda r: (r["object_name"], r["recorder_name"], r["channel_name"]))
    return rows


def camera_age_missing_rows(
    items: list[CameraWithContext],
    *,
    model: str = "",
    brand: str = "",
) -> list[dict[str, Any]]:
    filtered = filter_cameras_by_brand(filter_cameras_by_model(items, model), brand)
    rows: list[dict[str, Any]] = []
    for item in filtered:
        mfg = camera_manufacture_date(item)
        if parse_manufacture_date(mfg):
            continue
        ch = item.channel
        rec = item.recorder
        rows.append(
            {
                "object_name": rec.object_name,
                "recorder_name": rec.name or rec.host,
                "channel_name": ch.name or f"Канал {ch.channel_no + 1}",
                "camera_ip": ch.camera_ip or "—",
                "model": camera_model(item) or "—",
                "manufacturer": camera_manufacturer(item) or "—",
                "serial_number": ch.camera_serial or "—",
                "manufacture_date": mfg or "—",
                "date_source": _date_source_label(ch.manufacture_date_source),
                "metric_value": "—",
                "missing_reason": _camera_missing_date_reason(item),
            }
        )
    rows.sort(key=lambda r: (r["object_name"], r["recorder_name"], r["channel_name"]))
    return rows


def distinct_camera_models(items: list[CameraWithContext]) -> list[str]:
    return sorted({m for item in items if (m := camera_model(item))})


def distinct_camera_brands(items: list[CameraWithContext]) -> list[str]:
    return sorted({b for item in items if (b := camera_manufacturer(item))})


def aggregate_cameras_by_manufacturer(
    items: list[CameraWithContext],
    *,
    model: str = "",
    brand: str = "",
) -> dict[str, Any]:
    filtered = filter_cameras_by_brand(filter_cameras_by_model(items, model), brand)
    counter: Counter[str] = Counter()
    for item in filtered:
        counter[camera_manufacturer(item) or "unknown"] += 1
    keys = sorted(counter.keys(), key=lambda k: (-counter[k], k))
    labels = [camera_brand_label(k) for k in keys]
    values = [counter[k] for k in keys]
    colors = {k: chart_color(idx) for idx, k in enumerate(keys)}
    return {
        "manufacturers": labels,
        "labels": labels,
        "values": values,
        "keys": keys,
        "counts": values,
        "colors": colors,
    }


def camera_age_kpi(
    items: list[CameraWithContext],
    *,
    model: str = "",
    brand: str = "",
) -> dict[str, Any]:
    filtered = filter_cameras_by_brand(filter_cameras_by_model(items, model), brand)
    with_date = 0
    without_date = 0
    dahua_count = 0
    inventory_errors = 0
    periods: list[tuple[int, int]] = []
    for item in filtered:
        if item.channel.camera_inventory_error:
            inventory_errors += 1
        mfg = camera_manufacture_date(item)
        if mfg and parse_manufacture_date(mfg):
            with_date += 1
            parsed = parse_manufacture_date(mfg)
            assert parsed is not None
            periods.append((parsed.year, parsed.month))
        else:
            without_date += 1
        if camera_manufacturer(item) == "dahua":
            dahua_count += 1
    oldest = newest = "—"
    if periods:
        periods.sort()
        oldest = format_manufacture_date(f"{periods[0][0]:04d}-{periods[0][1]:02d}")
        newest = format_manufacture_date(
            f"{periods[-1][0]:04d}-{periods[-1][1]:02d}"
        )
    return {
        "total_cameras": len(filtered),
        "with_date": with_date,
        "without_date": without_date,
        "dahua_count": dahua_count,
        "inventory_errors": inventory_errors,
        "oldest": oldest,
        "newest": newest,
    }
