"""
Нормализация длинных текстов причин в короткие группы для фильтра отчёта.
"""

from __future__ import annotations

import re
from typing import Optional

_SOURCE_PREFIXES = ("[Канал] ", "[Категория] ", "[Регистратор] ")

# Порядок важен: первая подходящая подстрока задаёт группу регистратора.
_RECORDER_RULES: tuple[tuple[str, str], ...] = (
    ("Нет соединения", "Нет соединения"),
    ("HTTP ", "HTTP ошибка"),
    ("Превышено время ожидания", "Превышено время ожидания"),
    ("Ошибка HDD", "Ошибка HDD"),
    ("Ошибка сети", "Ошибка сети"),
    ("Запись на накопитель отключена", "Запись на накопитель отключена"),
    ("Заполнение диска", "Заполнение диска"),
    ("Требуется форматирование", "Требуется форматирование накопителя"),
    ("Потеря кадров записи", "Потеря кадров записи"),
    ("Перегрузка CPU", "Перегрузка CPU"),
    ("вентилятор", "Вентилятор"),
    ("Температура HDD", "Температура HDD"),
    ("NTP: Fail", "NTP: Fail"),
    ("Расхождение времени", "Расхождение времени"),
    ("Глубина архива", "__archive__"),
    ("Каналов с нулевым битрейтом", "Каналов с нулевым битрейтом"),
    ("Есть неисправные каналы", "Есть неисправные каналы"),
    ("Есть каналы с деградацией", "Есть каналы с деградацией"),
)

_CHANNEL_RULES: tuple[tuple[str, str], ...] = (
    ("Потеря видео", "Потеря видео (VideoLoss)"),
    ("Камера не подключена", "Камера не подключена"),
    ("Нулевой битрейт", "Нулевой битрейт потока"),
    ("Статус регистрации", "Регистрация камеры"),
    ("Канал выключен", "Канал выключен"),
    ("Скрытый режим", "Скрытый режим (Covert)"),
    ("Нагрузка декодирования", "Нагрузка декодирования"),
)


def _split_prefix(event_type: str) -> tuple[str, str]:
    for prefix in _SOURCE_PREFIXES:
        if event_type.startswith(prefix):
            return prefix, event_type[len(prefix) :]
    return "", event_type


def _archive_group(body: str) -> str:
    lower = body.lower()
    if "критично" in lower:
        return "Глубина архива (критично)"
    if "норма" in lower:
        return "Глубина архива (ниже нормы)"
    return "Глубина архива"


def _match_rules(body: str, rules: tuple[tuple[str, str], ...]) -> Optional[str]:
    body_lower = body.lower()
    for needle, label in rules:
        if needle.lower() in body_lower:
            if label == "__archive__":
                return _archive_group(body)
            return label
    return None


def normalize_event_group(event_type: str) -> str:
    """
    Сводит сотни вариантов health_reason к десяткам групп для фильтра.
    Исходный event_type сохраняется в детальной таблице отчёта.
    """
    prefix, body = _split_prefix(event_type.strip())
    if not body:
        return event_type

    if prefix == "[Категория] ":
        return event_type

    if prefix == "[Канал] ":
        grouped = _match_rules(body, _CHANNEL_RULES)
        return f"{prefix}{grouped or body}"

    if prefix == "[Регистратор] ":
        if "Заполнение диска" in body:
            return f"{prefix}Заполнение диска"
        if re.search(r"100\s*%", body) and "Глубина архива" not in body:
            return f"{prefix}Заполнение диска"
        grouped = _match_rules(body, _RECORDER_RULES)
        if grouped:
            return f"{prefix}{grouped}"
        # Составные причины без явного правила — убрать числа и диапазоны
        simplified = re.sub(r"\d+[\d\s.,/-]*", "…", body)
        simplified = re.sub(r";\s*", "; ", simplified).strip(" ;")
        if len(simplified) > 80:
            simplified = simplified[:77] + "…"
        return f"{prefix}{simplified or body}"

    return event_type


def group_sort_key(group_label: str) -> tuple[int, str]:
    order = {"[Канал]": 0, "[Категория]": 1, "[Регистратор]": 2}
    for prefix, rank in order.items():
        if group_label.startswith(prefix):
            return rank, group_label
    return 9, group_label
