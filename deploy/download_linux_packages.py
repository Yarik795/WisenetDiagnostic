"""Скачать Linux-колёса Python 3.12 в python-packages/ (запускать на Windows с интернетом)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

PYTHON_VERSION = "312"
PLATFORM = "manylinux2014_x86_64"
PACKAGES_DIRNAME = "python-packages"

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
REQUIREMENTS = PROJECT_ROOT / "backend" / "requirements.txt"
DEST = PROJECT_ROOT / PACKAGES_DIRNAME


def _fail(message: str, *, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def main() -> None:
    if not REQUIREMENTS.is_file():
        _fail(f"Не найден файл зависимостей: {REQUIREMENTS}")

    print(f"Проект: {PROJECT_ROOT}")
    print(f"Зависимости: {REQUIREMENTS}")
    print(f"Цель: Python {PYTHON_VERSION}, платформа {PLATFORM}")
    print(f"Папка: {DEST}")

    if DEST.exists():
        print(f"Удаляю предыдущую папку {DEST} ...")
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)

    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        str(REQUIREMENTS),
        "--target",
        str(DEST),
        "--python-version",
        PYTHON_VERSION,
        "--platform",
        PLATFORM,
        "--only-binary=:all:",
        "--upgrade",
    ]
    print("Команда:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        _fail(
            "Не удалось скачать Linux-колёса. "
            "Нужен pip 23+ и интернет. Исходники вместо wheels ставить нельзя — "
            f"на Ubuntu-виртуалке нет сети. Код pip: {exc.returncode}"
        )
    except OSError as exc:
        _fail(f"Не удалось запустить pip: {exc}")

    entries = [p.name for p in DEST.iterdir() if p.name != "__pycache__"]
    if not entries:
        _fail(f"Папка {DEST} пуста после установки — пакеты не скачались.")

    print()
    print(f"Готово: {len(entries)} записей в {DEST}")
    print("Скопируйте весь проект (включая python-packages/) на Ubuntu-виртуалку.")
    print("Запуск на Ubuntu (Python 3.12, без venv, без интернета):")
    print()
    print("  bash deploy/run.sh")
    print()
    print("или:")
    print()
    print("  cd backend")
    print("  PYTHONPATH=../python-packages python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000")


if __name__ == "__main__":
    main()
