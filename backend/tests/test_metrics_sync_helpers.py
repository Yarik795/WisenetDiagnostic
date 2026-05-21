from types import SimpleNamespace

from app.ui.metrics_helpers import (
    is_manual_sync,
    needs_ntp_time_update,
    ntp_action_button_label,
    show_ntp_action_button,
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


def test_needs_ntp_time_update() -> None:
    assert needs_ntp_time_update(SimpleNamespace(time_skew_seconds=2.0)) is True
    assert needs_ntp_time_update(SimpleNamespace(time_skew_seconds=1.0)) is False
    assert needs_ntp_time_update(SimpleNamespace(time_skew_seconds=0.5)) is False
    assert needs_ntp_time_update(None) is False
    assert needs_ntp_time_update(SimpleNamespace(time_skew_seconds=None)) is False


def test_show_ntp_action_button() -> None:
    manual = SimpleNamespace(sync_type="Manual", time_skew_seconds=0.0)
    assert show_ntp_action_button(manual) is True
    assert ntp_action_button_label(manual) == "Включить NTP"

    ntp_skew = SimpleNamespace(sync_type="NTP", time_skew_seconds=5.0)
    assert show_ntp_action_button(ntp_skew) is True
    assert ntp_action_button_label(ntp_skew) == "Обновить NTP"

    ntp_ok = SimpleNamespace(sync_type="NTP", time_skew_seconds=0.5)
    assert show_ntp_action_button(ntp_ok) is False
