from pathlib import Path

from app.logging_config import PROJECT_ROOT, resolve_log_paths


def test_resolve_log_paths_creates_writable_dir(tmp_path, monkeypatch):
    monkeypatch.delenv("WISENET_LOG_DIR", raising=False)
    fake_root = tmp_path / "proj"
    backend = fake_root / "backend"
    app_pkg = backend / "app"
    app_pkg.mkdir(parents=True)
    monkeypatch.setattr("app.logging_config.PROJECT_ROOT", fake_root)
    monkeypatch.setattr("app.logging_config.BACKEND_DIR", backend)
    monkeypatch.setattr("app.logging_config.APP_DIR", app_pkg)

    log_dir, log_file = resolve_log_paths()
    assert log_dir.exists()
    assert log_file.parent == log_dir
    assert log_file.name == "wisenet.log"


def test_resolve_log_paths_uses_env(tmp_path, monkeypatch):
    custom = tmp_path / "custom_logs"
    monkeypatch.setenv("WISENET_LOG_DIR", str(custom))
    log_dir, log_file = resolve_log_paths()
    assert log_dir == custom.resolve()
    assert log_file == custom.resolve() / "wisenet.log"
