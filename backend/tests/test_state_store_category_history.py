from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.state_store import StateStore


def _store(tmp_path: Path) -> StateStore:
    store = StateStore(path=tmp_path / "monitoring.db")
    store.init_db()
    return store


def test_init_db_creates_category_status_history(tmp_path: Path) -> None:
    store = _store(tmp_path)
    with store._connect() as conn:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='category_status_history'"
        ).fetchone()
    assert row is not None


def test_record_category_status_skips_duplicate_status(tmp_path: Path) -> None:
    store = _store(tmp_path)
    t0 = datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc)
    store.record_category_status("nvr-1", "archive", "warn", "low archive", t0)
    store.record_category_status("nvr-1", "archive", "warn", "still low", t0 + timedelta(hours=1))
    rows = store.list_category_history(recorder_id="nvr-1", category="archive")
    assert len(rows) == 1


def test_warn_to_error_keeps_episode_start(tmp_path: Path) -> None:
    store = _store(tmp_path)
    t_warn = datetime(2026, 5, 1, 8, 0, tzinfo=timezone.utc)
    t_error = datetime(2026, 5, 10, 8, 0, tzinfo=timezone.utc)
    store.record_category_status("nvr-1", "archive", "ok", None, t_warn - timedelta(days=1))
    store.record_category_status("nvr-1", "archive", "warn", "warn", t_warn)
    store.record_category_status("nvr-1", "archive", "error", "critical", t_error)
    since = store.get_category_problem_since("nvr-1", "archive")
    assert since == t_warn


def test_ok_to_error_starts_new_episode(tmp_path: Path) -> None:
    store = _store(tmp_path)
    t_ok = datetime(2026, 4, 1, 8, 0, tzinfo=timezone.utc)
    t_error = datetime(2026, 5, 1, 8, 0, tzinfo=timezone.utc)
    store.record_category_status("nvr-1", "time", "error", "skew", t_ok)
    store.record_category_status("nvr-1", "time", "ok", None, t_ok + timedelta(days=5))
    store.record_category_status("nvr-1", "time", "error", "skew again", t_error)
    since = store.get_category_problem_since("nvr-1", "time")
    assert since == t_error


def test_problem_since_none_when_currently_ok(tmp_path: Path) -> None:
    store = _store(tmp_path)
    t0 = datetime(2026, 5, 1, 8, 0, tzinfo=timezone.utc)
    store.record_category_status("nvr-1", "fans", "error", "fan", t0)
    store.record_category_status("nvr-1", "fans", "ok", None, t0 + timedelta(days=2))
    assert store.get_category_problem_since("nvr-1", "fans") is None
    assert ("nvr-1", "fans") not in store.category_problem_since_map()


def test_delete_recorder_data_removes_category_history(tmp_path: Path) -> None:
    store = _store(tmp_path)
    t0 = datetime(2026, 5, 1, 8, 0, tzinfo=timezone.utc)
    store.record_category_status("nvr-1", "archive", "warn", "x", t0)
    store.delete_recorder_data("nvr-1")
    assert store.list_category_history(recorder_id="nvr-1") == []
