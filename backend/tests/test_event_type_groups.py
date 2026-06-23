"""Тесты нормализации групп событий (scripts/event_type_groups.py)."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from event_type_groups import normalize_event_group  # noqa: E402


def test_archive_groups() -> None:
    assert (
        normalize_event_group("[Регистратор] Глубина архива 22.3-67.5 сут. (норма 30)")
        == "[Регистратор] Глубина архива (ниже нормы)"
    )
    assert (
        normalize_event_group("[Регистратор] Глубина архива 2.0 сут. (критично < 7 сут.)")
        == "[Регистратор] Глубина архива (критично)"
    )


def test_time_skew_group() -> None:
    assert (
        normalize_event_group("[Регистратор] NTP: Fail; Расхождение времени 72 с")
        == "[Регистратор] NTP: Fail"
    )
    assert (
        normalize_event_group("[Регистратор] Расхождение времени 1123184 с")
        == "[Регистратор] Расхождение времени"
    )


def test_channel_registration_group() -> None:
    assert (
        normalize_event_group("[Канал] Статус регистрации: ConnectFail")
        == "[Канал] Регистрация камеры"
    )


def test_category_unchanged() -> None:
    assert (
        normalize_event_group("[Категория] Глубина архива")
        == "[Категория] Глубина архива"
    )
