from __future__ import annotations

from typing import TYPE_CHECKING

from .models import AppConfig, Recorder

if TYPE_CHECKING:
    from .config_store import ConfigStore


def excluded_ids_set(config: AppConfig) -> set[str]:
    return set(config.exclusions.recorder_ids)


def is_excluded(recorder_id: str, config: AppConfig) -> bool:
    return recorder_id in excluded_ids_set(config)


def is_pollable(recorder: Recorder, config: AppConfig) -> bool:
    return not is_excluded(recorder.id, config)


def pollable_recorders(config: AppConfig) -> list[Recorder]:
    excluded = excluded_ids_set(config)
    return [r for r in config.recorders if r.id not in excluded]


def prune_exclusions(config: AppConfig) -> AppConfig:
    valid_ids = {r.id for r in config.recorders}
    pruned = [rid for rid in config.exclusions.recorder_ids if rid in valid_ids]
    if pruned == config.exclusions.recorder_ids:
        return config
    return config.model_copy(
        update={
            "exclusions": config.exclusions.model_copy(update={"recorder_ids": pruned})
        }
    )


def migrate_config_raw(data: dict) -> dict:
    """Нормализация сырого JSON: exclusions, миграция enabled=false → recorder_ids."""
    if "exclusions" not in data or not isinstance(data.get("exclusions"), dict):
        data["exclusions"] = {"recorder_ids": []}
    exclusions = data["exclusions"]
    if "recorder_ids" not in exclusions or not isinstance(exclusions.get("recorder_ids"), list):
        exclusions["recorder_ids"] = []

    recorder_ids: list[str] = list(exclusions["recorder_ids"])
    seen = set(recorder_ids)

    for rec in data.get("recorders") or []:
        if not isinstance(rec, dict):
            continue
        if rec.pop("enabled", True) is False:
            rid = rec.get("id")
            if rid and rid not in seen:
                recorder_ids.append(rid)
                seen.add(rid)

    exclusions["recorder_ids"] = recorder_ids
    return data
