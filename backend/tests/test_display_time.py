import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.display_time import format_for_display, get_display_tz, to_display


def test_to_display_moscow(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"monitoring": {"display_timezone": "Europe/Moscow"}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("CONFIG_PATH", str(config_path))
    utc = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    local = to_display(utc)
    assert local is not None
    assert local.hour == 15
    assert format_for_display(utc, "%H:%M") == "15:00"


def test_get_display_tz_fallback_on_invalid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"monitoring": {"display_timezone": "Not/A/Timezone"}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("CONFIG_PATH", str(config_path))
    import app.display_time as display_time

    display_time._warned_invalid_tz = False
    tz = get_display_tz()
    utc = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    assert utc.astimezone(tz).hour == 15


def test_moscow_tz_fixed_offset_without_zoneinfo(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.display_time as display_time
    from zoneinfo import ZoneInfoNotFoundError

    def missing(_name: str):
        raise ZoneInfoNotFoundError(_name)

    monkeypatch.setattr(display_time, "ZoneInfo", missing)
    tz = display_time._load_moscow_tz()
    utc = datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc)
    assert utc.astimezone(tz).hour == 15
