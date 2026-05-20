from datetime import datetime, timezone
from pathlib import Path

from app.state_store import StateStore


def test_channel_and_recorder_archive_fields(tmp_path: Path) -> None:
    store = StateStore(path=tmp_path / "monitoring.db")
    store.init_db()
    polled = datetime(2026, 5, 20, 12, 0, 0, tzinfo=timezone.utc)

    store.upsert_channel(
        "nvr-1",
        0,
        name="Cam 1",
        archive_start="2026-01-01 00:00:00",
        archive_end="2026-05-01 00:00:00",
        archive_days=120.5,
        last_polled_at=polled,
    )
    ch = store.get_channel("nvr-1", 0)
    assert ch is not None
    assert ch.archive_days == 120.5

    store.upsert_recorder_metrics(
        "nvr-1",
        archive_min_days=8.2,
        archive_max_days=31.4,
        archive_days=31.4,
        last_polled_at=polled,
    )
    metrics = store.get_recorder_metrics("nvr-1")
    assert metrics is not None
    assert metrics.archive_min_days == 8.2
    assert metrics.archive_max_days == 31.4
