"""Отчёт «Анализ повторных РВР» из pp_requests + naumen_records."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

from .cashflow_report import FIO_NAMES

WORK_TYPE_REQUIRED = "РВР"
TBANK_MUST_CONTAIN = "3800"
STATUS_REVOKED_SUBSTR = "отозвана"
EXCLUDED_SYSTEM_KIND = "УС"
OBJECT_TYPE_ADZ = "АДЗ"
OBJECT_TYPE_VSP = "ВСП"

MARK_START = "Комментарий ВК: "
MARK_END = " ФИО ВК"
MARK_END_ALT = "ФИО ВК"

_FIO_ADZ_RE = re.compile("|".join(re.escape(n) for n in FIO_NAMES), re.IGNORECASE)

SummaryGroupKey = tuple[str, str]


def extract_vk_comment(desc: str) -> str:
    """Текст между «Комментарий ВК: » и « ФИО ВК» / «ФИО ВК»."""
    if not desc:
        return ""
    start = desc.find(MARK_START)
    if start < 0:
        return ""
    after = desc[start + len(MARK_START) :]
    end = after.find(MARK_END)
    if end < 0:
        end = after.find(MARK_END_ALT)
    if end < 0:
        return ""
    return after[:end].strip()


def norm_sberdrug_key(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if value != value:
            return ""
        if value.is_integer():
            return str(int(value))
        return str(value).strip()
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    return str(value).strip()


def norm_address(addr: str) -> str:
    if not addr:
        return ""
    t = addr.replace("\u00a0", " ").replace("\u202f", " ")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def object_type_from_fio(fio: str) -> str:
    return OBJECT_TYPE_ADZ if _FIO_ADZ_RE.search(fio or "") else OBJECT_TYPE_VSP


def _status_revoked(status: str) -> bool:
    lc = (status or "").lower().replace("ё", "е")
    return STATUS_REVOKED_SUBSTR.lower().replace("ё", "е") in lc


def _parse_created_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _format_created_date_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%d.%m.%Y")


def _zayavka_summary_entry_line(num: str, date_ddmmyyyy: str, short_desc: str) -> str:
    n = (num or "").strip()
    ds = (date_ddmmyyyy or "").strip()
    s = (short_desc or "").strip()
    if not n:
        tail = ", ".join(x for x in (ds, s) if x)
        return tail or ""
    head = f"{n}, {ds}" if ds else n
    if s:
        return f"{head}, {s}"
    return f"{head}, —"


def _repeat_count_for_group(
    by_kind: dict[str, list[dict[str, str]]], kinds: list[str]
) -> int:
    return sum(max(0, len(by_kind.get(k, [])) - 1) for k in kinds)


def _group_keys_min_per_kind(
    summary: dict[SummaryGroupKey, dict[str, list[dict[str, str]]]],
    min_count: int,
) -> list[SummaryGroupKey]:
    keys = [
        gk
        for gk, by_kind in summary.items()
        if any(len(entries) >= min_count for entries in by_kind.values())
    ]
    keys.sort()
    return keys


def _sort_group_keys_by_repeats_desc(
    group_keys: list[SummaryGroupKey],
    summary: dict[SummaryGroupKey, dict[str, list[dict[str, str]]]],
    kinds: list[str],
) -> list[SummaryGroupKey]:
    return sorted(
        group_keys,
        key=lambda gk: (
            -_repeat_count_for_group(summary[gk], kinds),
            gk[0],
            gk[1],
        ),
    )


def _summary_groups_from_dict(
    summary: dict[SummaryGroupKey, dict[str, list[dict[str, str]]]],
    kinds: list[str],
    group_keys: list[SummaryGroupKey],
) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for gk in group_keys:
        addr, obj = gk
        by_kind = summary[gk]
        repeat_total = _repeat_count_for_group(by_kind, kinds)
        kind_entries: dict[str, list[dict[str, str]]] = {}
        for kind in kinds:
            entries = by_kind.get(kind, [])
            if entries:
                kind_entries[kind] = list(entries)
        groups.append(
            {
                "address": addr,
                "object_type": obj,
                "repeat_count": repeat_total,
                "by_kind": kind_entries,
                "analysis": None,
            }
        )
    return groups


def _period_label(date_from: date, date_to: date) -> str:
    return f"{date_from.strftime('%d.%m.%Y')} — {date_to.strftime('%d.%m.%Y')} (UTC)"


def _in_period(created: datetime, date_from: date, date_to: date) -> bool:
    u = created.astimezone(timezone.utc)
    start = datetime(
        date_from.year, date_from.month, date_from.day, tzinfo=timezone.utc
    )
    end_exclusive = datetime(
        date_to.year, date_to.month, date_to.day, tzinfo=timezone.utc
    ) + timedelta(days=1)
    return start <= u < end_exclusive


def build_rvr_repeat_report(
    rows: list[dict[str, Any]],
    desc_map: dict[str, str],
    *,
    date_from: date,
    date_to: date,
) -> dict[str, Any]:
    summary: dict[SummaryGroupKey, dict[str, list[dict[str, str]]]] = (
        defaultdict(lambda: defaultdict(list))
    )
    all_kinds: set[str] = set()
    data_rows: list[dict[str, Any]] = []

    for row in rows:
        created = _parse_created_dt(row.get("created_at"))
        if created is None or not _in_period(created, date_from, date_to):
            continue

        work_type = (row.get("work_type") or "").strip()
        if work_type != WORK_TYPE_REQUIRED:
            continue

        tb = (row.get("tb") or "").strip()
        if TBANK_MUST_CONTAIN not in tb:
            continue

        status = (row.get("status") or "").strip()
        if _status_revoked(status):
            continue

        kind = (row.get("security_system_type") or "").strip()
        if kind == EXCLUDED_SYSTEM_KIND:
            continue

        drug_key = norm_sberdrug_key(row.get("drug_number"))
        raw_desc = desc_map.get(drug_key, "")
        short_desc = extract_vk_comment(raw_desc)

        request_number = (row.get("request_number") or "").strip()
        if not request_number:
            request_number = drug_key

        addr = norm_address((row.get("address") or "").strip())
        fio = (row.get("customer_fio") or "").strip()
        row_object_type = object_type_from_fio(fio)
        date_s = _format_created_date_utc(created)

        data_rows.append(
            {
                **row,
                "description": short_desc,
                "object_type": row_object_type,
                "created_date_display": date_s,
            }
        )

        if addr and kind:
            gk: SummaryGroupKey = (addr, row_object_type)
            summary[gk][kind].append(
                {
                    "num": request_number,
                    "date": date_s,
                    "desc": short_desc,
                }
            )
            all_kinds.add(kind)

    sorted_kinds = sorted(all_kinds)
    keys_ge2 = _sort_group_keys_by_repeats_desc(
        _group_keys_min_per_kind(summary, 2), summary, sorted_kinds
    )
    keys_ge3 = _sort_group_keys_by_repeats_desc(
        _group_keys_min_per_kind(summary, 3), summary, sorted_kinds
    )
    groups_ge2 = _summary_groups_from_dict(summary, sorted_kinds, keys_ge2)
    groups_ge3 = _summary_groups_from_dict(summary, sorted_kinds, keys_ge3)

    repeats_total = sum(g["repeat_count"] for g in groups_ge2)
    top_object = ""
    if groups_ge2:
        top = groups_ge2[0]
        top_object = f"{top['address']} ({top['object_type']})"

    return {
        "period": {
            "from": date_from.isoformat(),
            "to": date_to.isoformat(),
            "label": _period_label(date_from, date_to),
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "kinds": sorted_kinds,
        "groups_ge2": groups_ge2,
        "groups_ge3": groups_ge3,
        "kpi": {
            "groups_total": len(groups_ge2),
            "repeats_total": repeats_total,
            "top_object": top_object,
            "requests_total": len(data_rows),
        },
        "data_rows": data_rows,
        "has_data": bool(data_rows),
        "filters_text": (
            "Отбор: «Вид работ» = РВР; «Территориальный банк» содержит «3800»; "
            "статус без подстроки «отозвана»; вид систем не «УС»; "
            "колонка «Описание» — фрагмент из Naumen (Комментарий ВК … ФИО ВК)."
        ),
    }


def format_kind_cell(entries: list[dict[str, str]]) -> str:
    parts = [
        _zayavka_summary_entry_line(e["num"], e["date"], e["desc"])
        for e in entries
    ]
    return ";\n".join(parts) if parts else ""
