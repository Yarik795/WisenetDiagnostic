from datetime import date

from app.serial_manufacture_date import decode_samsung_manufacture_date


def test_decode_15_char_appliance_examples() -> None:
    ref = date(2026, 6, 1)
    assert decode_samsung_manufacture_date("J0V07DDD801404K", reference_date=ref) == date(
        2013, 8, 1
    )
    assert decode_samsung_manufacture_date("0ARV5BBJ400798K", reference_date=ref) == date(
        2017, 4, 1
    )
    assert decode_samsung_manufacture_date("B078G8DK901569A", reference_date=ref) == date(
        2018, 9, 1
    )


def test_decode_xrn_6410b2_sample_serial() -> None:
    ref = date(2026, 6, 1)
    # pos8=W→2023, pos9=A→октябрь
    assert decode_samsung_manufacture_date("ZPET6V4WA0000SP", reference_date=ref) == date(
        2023, 10, 1
    )


def test_decode_unsupported_length() -> None:
    assert decode_samsung_manufacture_date("ABC") is None
    assert decode_samsung_manufacture_date("ABCDEFGHIJKL") is None
