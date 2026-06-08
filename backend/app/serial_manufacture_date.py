"""Дата производства по серийному номеру Samsung / Hanwha (наследие Samsung Techwin).

Правила (Samsung appliance / mobile):
- 11 символов: 4-й — год, 5-й — месяц
- ≥ 15 символов: 8-й — год, 9-й — месяц
Месяц: 1–9, A=окт, B=ноя, C=дек.
Год: буквенный код с 20-летним циклом; при неоднозначности — самый поздний год ≤ reference_date.
"""

from __future__ import annotations

from datetime import date

# Код года → возможные календарные годы (Samsung date codes).
_YEAR_CODE_CANDIDATES: dict[str, list[int]] = {
    "R": [2001, 2021],
    "T": [2002, 2022],
    "W": [2003, 2023],
    "X": [2004, 2024],
    "Y": [2005, 2025],
    "A": [2006],
    "L": [2006],
    "P": [2007],
    "Q": [2008],
    "S": [2009],
    "Z": [2010],
    "B": [2011],
    "C": [2012],
    "D": [2013],
    "F": [2014],
    "G": [2015],
    "H": [2016],
    "J": [2017],
    "K": [2018],
    "M": [2019],
    "N": [2020],
}

_MONTH_CODE: dict[str, int] = {
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "A": 10,
    "B": 11,
    "C": 12,
}


def _resolve_year(year_char: str, reference: date) -> int | None:
    candidates = _YEAR_CODE_CANDIDATES.get(year_char.upper())
    if not candidates:
        return None
    valid = [y for y in candidates if y <= reference.year]
    if not valid:
        return min(candidates)
    return max(valid)


def _year_month_positions(length: int) -> tuple[int, int] | None:
    if length == 11:
        return 3, 4
    if length >= 15:
        return 7, 8
    return None


def decode_samsung_manufacture_date(
    serial_number: str,
    *,
    reference_date: date | None = None,
) -> date | None:
    """Вернуть первый день месяца производства или None, если S/N не распознан."""
    serial = (serial_number or "").strip().upper()
    if not serial:
        return None

    positions = _year_month_positions(len(serial))
    if positions is None:
        return None

    year_idx, month_idx = positions
    if month_idx >= len(serial):
        return None

    year_char = serial[year_idx]
    month_char = serial[month_idx]
    month = _MONTH_CODE.get(month_char)
    if month is None:
        return None

    ref = reference_date or date.today()
    year = _resolve_year(year_char, ref)
    if year is None:
        return None

    return date(year, month, 1)


RECORDER_DEVICE_TYPES = frozenset({"NVR", "DVR", "HYBRID"})


def should_store_serial_metrics(
    device_type: str | None,
    serial_number: str | None,
) -> bool:
    """Записывать S/N и дату только для регистраторов с непустым SerialNumber в deviceinfo."""
    serial = (serial_number or "").strip()
    if not serial:
        return False
    return (device_type or "").upper() in RECORDER_DEVICE_TYPES


def resolve_manufacture_date(
    serial_number: str | None,
    device_type: str | None,
    *,
    reference_date: date | None = None,
) -> str | None:
    """YYYY-MM или None. Эмпирически S/N в API отдают XRN-3210B2 и XRN-6410B2."""
    if not should_store_serial_metrics(device_type, serial_number):
        return None
    decoded = decode_samsung_manufacture_date(
        serial_number or "",
        reference_date=reference_date,
    )
    return decoded.strftime("%Y-%m") if decoded else None
