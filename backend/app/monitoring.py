from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from .config_store import ConfigStore
from .health import HealthStatus, worst_status
from .models import CheckStatus, MonitoringSettings, Recorder
from .state_store import StateStore
from .sunapi import check_recorder
from .sunapi_extended import ChannelInfo, EventChannelStatus, RecorderPollData, poll_recorder

logger = logging.getLogger("monitoring")


def evaluate_channel_health(
    ch: ChannelInfo,
    event: Optional[EventChannelStatus],
    settings: MonitoringSettings,
) -> tuple[str, str]:
    if event and event.video_loss is True:
        return HealthStatus.ERROR.value, "Потеря видео (VideoLoss)"
    if event and event.connected is False:
        return HealthStatus.ERROR.value, "Камера не подключена"
    state = (ch.source_state or "").lower()
    if state in ("deactive", "off"):
        return HealthStatus.ERROR.value, f"Канал {ch.source_state}"
    reg = (ch.register_status or "").lower()
    if reg and reg not in ("success", "ok"):
        return HealthStatus.WARN.value, f"Статус регистрации: {ch.register_status}"
    if ch.camera_ip and state == "on":
        return HealthStatus.OK.value, "Канал активен"
    if state == "on":
        return HealthStatus.OK.value, "Канал включён"
    return HealthStatus.UNKNOWN.value, "Нет данных о канале"


def evaluate_recorder_health(
    poll: RecorderPollData,
    channel_statuses: list[str],
    settings: MonitoringSettings,
) -> tuple[str, str]:
    if not poll.online:
        return HealthStatus.ERROR.value, poll.error or "NVR недоступен"

    reasons: list[str] = []
    status = HealthStatus.OK.value

    if poll.storage:
        pct = poll.storage.used_percent
        if poll.storage.worst_status and str(poll.storage.worst_status).lower() in (
            "error",
            "fail",
            "full",
        ):
            status = HealthStatus.ERROR.value
            reasons.append(f"Диск: {poll.storage.worst_status}")
        elif pct is not None:
            if pct >= settings.disk_usage_error_percent:
                status = HealthStatus.ERROR.value
                reasons.append(f"Заполнение диска {pct}%")
            elif pct >= settings.disk_usage_warn_percent:
                if status != HealthStatus.ERROR.value:
                    status = HealthStatus.WARN.value
                reasons.append(f"Заполнение диска {pct}%")

    if poll.date_time:
        if poll.date_time.ntp_status and poll.date_time.ntp_status.lower() == "fail":
            if status != HealthStatus.ERROR.value:
                status = HealthStatus.WARN.value
            reasons.append("NTP: Fail")
        skew = poll.date_time.skew_seconds
        if skew is not None:
            if skew >= settings.time_skew_error_seconds:
                status = HealthStatus.ERROR.value
                reasons.append(f"Расхождение времени {int(skew)} с")
            elif skew >= settings.time_skew_warn_seconds:
                if status != HealthStatus.ERROR.value:
                    status = HealthStatus.WARN.value
                reasons.append(f"Расхождение времени {int(skew)} с")

    if poll.recording_period and poll.recording_period.archive_days is not None:
        days = poll.recording_period.archive_days
        if days < settings.archive_days_required:
            if status != HealthStatus.ERROR.value:
                status = HealthStatus.WARN.value
            reasons.append(
                f"Глубина архива {days:.1f} сут. (норма {settings.archive_days_required})"
            )

    ch_worst = worst_status(*channel_statuses) if channel_statuses else HealthStatus.UNKNOWN.value
    if ch_worst == HealthStatus.ERROR.value:
        status = HealthStatus.ERROR.value
        reasons.append("Есть неисправные каналы")
    elif ch_worst == HealthStatus.WARN.value and status == HealthStatus.OK.value:
        status = HealthStatus.WARN.value
        reasons.append("Есть каналы с деградацией")

    if not reasons:
        return HealthStatus.OK.value, "NVR в норме"
    return status, "; ".join(reasons)


def apply_poll_result(
    store: ConfigStore,
    state: StateStore,
    recorder: Recorder,
    poll: RecorderPollData,
    settings: MonitoringSettings,
    polled_at: datetime,
) -> None:
    events_map = {e.channel_no: e for e in poll.events}
    channel_statuses: list[str] = []
    channel_nos: list[int] = []

    for ch in poll.channels:
        event = events_map.get(ch.channel_no)
        h_status, h_reason = evaluate_channel_health(ch, event, settings)
        channel_statuses.append(h_status)
        channel_nos.append(ch.channel_no)
        state.upsert_channel(
            recorder.id,
            ch.channel_no,
            name=ch.name,
            camera_ip=ch.camera_ip,
            camera_model=ch.camera_model,
            source_state=ch.source_state,
            health_status=h_status,
            health_reason=h_reason,
            video_loss=event.video_loss if event else None,
            last_polled_at=polled_at,
        )
        state.record_history(
            "channel",
            f"{recorder.id}:{ch.channel_no}",
            h_status,
            h_reason,
            polled_at,
        )

    state.remove_channels_not_in(recorder.id, channel_nos)

    rec_status, rec_reason = evaluate_recorder_health(poll, channel_statuses, settings)
    counts = _count_statuses(channel_statuses)

    storage_pct = poll.storage.used_percent if poll.storage else None
    storage_st = poll.storage.worst_status if poll.storage else None
    archive_days = (
        poll.recording_period.archive_days if poll.recording_period else None
    )

    state.upsert_recorder_metrics(
        recorder.id,
        model=poll.device.model if poll.device else None,
        firmware_version=poll.device.firmware_version if poll.device else None,
        device_online=poll.online,
        health_status=rec_status,
        health_reason=rec_reason,
        ntp_status=poll.date_time.ntp_status if poll.date_time else None,
        time_skew_seconds=poll.date_time.skew_seconds if poll.date_time else None,
        storage_used_percent=storage_pct,
        storage_status=storage_st,
        archive_start=(
            poll.recording_period.start_time if poll.recording_period else None
        ),
        archive_end=poll.recording_period.end_time if poll.recording_period else None,
        archive_days=archive_days,
        channel_count=len(poll.channels),
        channels_ok=counts["ok"],
        channels_warn=counts["warn"],
        channels_error=counts["error"],
        channels_unknown=counts["unknown"],
        last_polled_at=polled_at,
    )
    state.record_history("recorder", recorder.id, rec_status, rec_reason, polled_at)

    check_status = CheckStatus.ONLINE if poll.online else CheckStatus.OFFLINE
    store.update_recorder_status(
        recorder.id,
        check_status,
        polled_at,
        poll.error if not poll.online else None,
    )


def _count_statuses(statuses: list[str]) -> dict[str, int]:
    counts = {"ok": 0, "warn": 0, "error": 0, "unknown": 0}
    for s in statuses:
        counts[s] = counts.get(s, 0) + 1
    return counts


async def poll_single_recorder(
    config_store: ConfigStore,
    state_store: StateStore,
    recorder: Recorder,
    *,
    include_inventory: bool = True,
) -> None:
    if not recorder.enabled:
        return
    config = config_store.load()
    credentials = config.credentials
    settings = config.monitoring
    polled_at = datetime.now(timezone.utc)

    poll = await poll_recorder(
        recorder,
        credentials,
        include_inventory=include_inventory,
    )
    apply_poll_result(config_store, state_store, recorder, poll, settings, polled_at)


async def run_poll_cycle(
    config_store: ConfigStore,
    state_store: StateStore,
    *,
    include_inventory: bool = False,
) -> None:
    config = config_store.load()
    recorders = [r for r in config.recorders if r.enabled]
    if not recorders:
        return

    sem = asyncio.Semaphore(config.monitoring.max_concurrent_polls)

    async def _one(rec: Recorder) -> None:
        async with sem:
            try:
                await poll_single_recorder(
                    config_store,
                    state_store,
                    rec,
                    include_inventory=include_inventory,
                )
            except Exception:
                logger.exception("poll failed for %s", rec.id)

    await asyncio.gather(*[_one(r) for r in recorders])
    logger.info("poll cycle done", extra={"recorders": len(recorders)})


async def run_inventory_cycle(
    config_store: ConfigStore,
    state_store: StateStore,
) -> None:
    await run_poll_cycle(config_store, state_store, include_inventory=True)
