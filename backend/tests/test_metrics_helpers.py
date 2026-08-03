from app.ui.metrics_helpers import (
    disk_space_mb,
    format_archive_days_value,
    format_archive_range,
)


def test_format_archive_range_single() -> None:
    assert format_archive_range(35.0, 35.0, 30) == "35.0 сут."


def test_format_archive_range_min_max() -> None:
    assert format_archive_range(8.2, 31.4, 30) == "8.2-31.4 сут. (норма 30)"


def test_format_archive_range_collapses_near_equal_display() -> None:
    assert format_archive_range(48.47, 48.53, 30) == "48.5 сут."
    assert format_archive_range(48.48, 48.52, 30) == "48.5 сут."


def test_format_archive_days_value() -> None:
    assert format_archive_days_value(15.0) == "15.0 сут."
    assert format_archive_days_value(None) == "—"


def test_disk_space_mb_parses_tb_units() -> None:
    disk = {
        "UsedSpace": "5.98TB",
        "TotalSpace": "5.98TB",
    }
    used, total = disk_space_mb(disk)
    assert used is not None
    assert total is not None
    assert abs(used - 5.98 * 1024 * 1024) < 1
    assert abs(total - 5.98 * 1024 * 1024) < 1

