from app.ui.metrics_helpers import (
    format_archive_days_value,
    format_archive_range,
)


def test_format_archive_range_single() -> None:
    assert format_archive_range(35.0, 35.0, 30) == "35.0 сут."


def test_format_archive_range_min_max() -> None:
    assert format_archive_range(8.2, 31.4, 30) == "8.2-31.4 сут. (норма 30)"


def test_format_archive_days_value() -> None:
    assert format_archive_days_value(15.0) == "15.0 сут."
    assert format_archive_days_value(None) == "—"
