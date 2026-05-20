from app.ui.metrics_helpers import (
    is_manual_sync,
    sync_type_badge_class,
    sync_type_label,
)


def test_sync_type_helpers() -> None:
    assert is_manual_sync("Manual") is True
    assert is_manual_sync("NTP") is False
    assert sync_type_label("manual") == "Ручная"
    assert sync_type_label("NTP") == "NTP"
    assert sync_type_label("GPS") == "GPS"
    assert "manual" in sync_type_badge_class("Manual")
