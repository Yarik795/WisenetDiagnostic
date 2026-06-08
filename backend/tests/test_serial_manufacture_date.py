from datetime import date

import pytest

from app.serial_manufacture_date import (
    decode_samsung_manufacture_date,
    resolve_manufacture_date,
    should_store_serial_metrics,
)

_REF = date(2026, 6, 1)

# Эталоны с production-опроса (XRN-3210B2 / XRN-6410B2)
HANWHA_RECORDER_SERIALS = [
    ("ZNWH6V4N90000KJ", 2020, 9),
    ("ZNWH6V4N90004AB", 2020, 9),
    ("ZNWH6V4N90009FR", 2020, 9),
    ("ZSP06V4X200002J", 2024, 2),
    ("ZSP06V4X90001XA", 2024, 9),
    ("ZNWH6V4R500067T", 2021, 5),
    ("ZNWH6V4R50005SJ", 2021, 5),
    ("ZNWH6V4N9000EXR", 2020, 9),
    ("ZSP06V4X90000XM", 2024, 9),
    ("ZNYC70GMA0002HN", 2019, 10),
    ("ZNWH6V4R50007YZ", 2021, 5),
    ("ZNWH6V4R5000BMX", 2021, 5),
    ("ZNWH6V4R500075K", 2021, 5),
    ("ZNWH6V4R40007VJ", 2021, 4),
    ("ZNWH6V4R5000CHD", 2021, 5),
    ("ZNWH6V4R50005LA", 2021, 5),
    ("ZNWH6V4R5000CZB", 2021, 5),
    ("ZNWH6V4R400027Z", 2021, 4),
    ("ZNWH6V4N90007GE", 2020, 9),
    ("ZSP06V4WA0000MP", 2023, 10),
    ("ZNWH6V4N90008DN", 2020, 9),
    ("ZNYC70GMA0001NL", 2019, 10),
    ("ZSP06V4X900012H", 2024, 9),
]


def test_decode_15_char_appliance_examples() -> None:
    assert decode_samsung_manufacture_date("J0V07DDD801404K", reference_date=_REF) == date(
        2013, 8, 1
    )
    assert decode_samsung_manufacture_date("0ARV5BBJ400798K", reference_date=_REF) == date(
        2017, 4, 1
    )
    assert decode_samsung_manufacture_date("B078G8DK901569A", reference_date=_REF) == date(
        2018, 9, 1
    )


def test_decode_xrn_6410b2_sample_serial() -> None:
    assert decode_samsung_manufacture_date("ZPET6V4WA0000SP", reference_date=_REF) == date(
        2023, 10, 1
    )


@pytest.mark.parametrize("serial,year,month", HANWHA_RECORDER_SERIALS)
def test_decode_hanwha_recorder_serials(serial: str, year: int, month: int) -> None:
    assert decode_samsung_manufacture_date(serial, reference_date=_REF) == date(
        year, month, 1
    )
    assert resolve_manufacture_date(serial, "NVR", reference_date=_REF) == f"{year:04d}-{month:02d}"


def test_decode_unsupported_length() -> None:
    assert decode_samsung_manufacture_date("ABC") is None
    assert decode_samsung_manufacture_date("ABCDEFGHIJKL") is None


@pytest.mark.parametrize(
    "device_type,serial,expected",
    [
        ("NVR", "ZNWH6V4N90000KJ", True),
        ("DVR", "ZNWH6V4N90000KJ", True),
        ("Hybrid", "ZNWH6V4N90000KJ", True),
        ("NWC", "ZNWH6V4N90000KJ", False),
        ("NVR", "", False),
        ("NVR", None, False),
    ],
)
def test_should_store_serial_metrics(device_type: str, serial: str | None, expected: bool) -> None:
    assert should_store_serial_metrics(device_type, serial) is expected


def test_resolve_manufacture_date_rejects_camera() -> None:
    assert resolve_manufacture_date("ZNWH6V4N90000KJ", "NWC", reference_date=_REF) is None
