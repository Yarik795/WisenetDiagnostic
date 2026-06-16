"""Тесты drill-down дашборда Арсенал."""

from __future__ import annotations

from pathlib import Path

from app.arsenal_import import import_arsenal_xlsx
from app.state_store import StateStore
from app.ui.arsenal_dashboard import (
    arsenal_detail_context,
    arsenal_passport_context,
    display_object_name,
)
from tests.test_arsenal_import import _write_arsenal_xlsx


def test_display_object_name_prefers_address(tmp_path: Path) -> None:
    xlsx = tmp_path / "паспортам.xlsx"
    _write_arsenal_xlsx(xlsx)
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    import_arsenal_xlsx(xlsx, state)

    row = state.get_arsenal_analytics("114585")
    assert row is not None
    assert display_object_name(row) == row.address


def test_arsenal_detail_and_passport_context(tmp_path: Path) -> None:
    xlsx = tmp_path / "паспортам.xlsx"
    _write_arsenal_xlsx(xlsx)
    state = StateStore(path=tmp_path / "monitoring.db")
    state.init_db()
    import_arsenal_xlsx(xlsx, state)

    detail = arsenal_detail_context(
        state,
        dimension="manufacturer",
        value="HANWHA",
        system_type="ТСВ",
    )
    assert detail["arsenal_detail_count"] == 1
    assert detail["arsenal_detail_rows"][0]["passport_number"] == "114585"

    card = arsenal_passport_context(state, "114585")
    assert card["arsenal_passport_found"] is True
    assert card["name"] == card["address"]
    assert len(card["system_rows"]) == 2
