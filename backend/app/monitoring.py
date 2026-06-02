from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .poll_jobs import PollJobTracker

from .config_store import ConfigStore, RecorderStatusUpdate
from .health import HealthStatus, worst_status
from .models import CheckStatus, MonitoringSettings, Recorder
from .state_store import ChannelRow, StateStore
from .sunapi import check_recorder
from .sunapi_extended import (
    ChannelInfo,
    EventChannelStatus,
    NvrApiProfile,
    RecorderPollData,
    RecordingPeriodInfo,
    channel_is_active,
    enable_recorder_ntp,
    is_register_status_error,
    is_stale_connectfail_on_live_channel,
    normalize_register_status,
    poll_recorder,
)
from .ui.health_classifiers import CATEGORY_LABELS, classify_category
from .ui.metrics_helpers import (
    SYSTEM_EVENT_ERROR_LABELS,
    SYSTEM_EVENT_WARN_LABELS,
    active_system_event_labels,
    any_disk_format_required,
    max_disk_drop_datarate_percent,
    max_disk_temperature_celsius_from_disks,
)

logger = logging.getLogger("monitoring")


def evaluate_channel_health(
    ch: ChannelInfo,
    event: Optional[EventChannelStatus],
    settings: MonitoringSettings,
    *,
    device_model: Optional[str] = None,
    profile: Optional[NvrApiProfile] = None,
) -> tuple[str, str]:
    state = (ch.source_state or ch.video_state or "").lower()

    if event and event.sd_fail is True:
        return HealthStatus.ERROR.value, "Сбой SD-карты камеры"
    if event and event.sd_full is True:
        return HealthStatus.WARN.value, "SD-карта камеры заполнена"
    if event and event.low_fps is True:
        return HealthStatus.WARN.value, "Низкий FPS"
    if event and event.tampering is True:
        return HealthStatus.WARN.value, "Вмешательство (Tampering)"
    if event and event.defocus is True:
        return HealthStatus.WARN.value, "Расфокус"
    if event and event.fog is True:
        return HealthStatus.WARN.value, "Туман / засветка (Fog)"

    if state == "deactive":
        return HealthStatus.UNKNOWN.value, "Канал деактивирован (не используется)"
    if state == "off":
        return HealthStatus.WARN.value, "Канал выключен"
    if state in ("covert1", "covert2"):
        return HealthStatus.WARN.value, f"Скрытый режим ({ch.source_state})"

    if event and event.video_loss is True:
        return HealthStatus.ERROR.value, "Потеря видео (VideoLoss)"
    if event and event.connected is False:
        return HealthStatus.ERROR.value, "Камера не подключена"

    if is_stale_connectfail_on_live_channel(ch, event, device_model=device_model):
        return (
            HealthStatus.OK.value,
            "Канал активен (в API регистрации ConnectFail, поток в норме)",
        )

    reg_key = normalize_register_status(ch.register_status)
    if state == "on" and is_register_status_error(ch.register_status):
        return (
            HealthStatus.ERROR.value,
            f"Статус регистрации: {ch.register_status}",
        )
    if reg_key and reg_key not in ("success", "ok"):
        return HealthStatus.WARN.value, f"Статус регистрации: {ch.register_status}"

    if channel_is_active(ch):
        if ch.data_rate is not None and ch.data_rate <= 0:
            return HealthStatus.WARN.value, "Нулевой битрейт потока"
        if profile and profile.supports_poe_status and ch.poe_status is False:
            return HealthStatus.WARN.value, "PoE выключен на канале"
        if (
            ch.cpu_usage is not None
            and ch.cpu_usage >= settings.cpu_usage_error_percent
        ):
            return (
                HealthStatus.ERROR.value,
                f"Нагрузка декодирования {ch.cpu_usage:.1f}%",
            )
        if (
            ch.cpu_usage is not None
            and ch.cpu_usage >= settings.cpu_usage_warn_percent
        ):
            return (
                HealthStatus.WARN.value,
                f"Нагрузка декодирования {ch.cpu_usage:.1f}%",
            )

    if ch.camera_ip and state == "on":
        return HealthStatus.OK.value, "Канал активен"
    if state == "on":
        return HealthStatus.OK.value, "Канал включён"
    return HealthStatus.UNKNOWN.value, "Нет данных о канале"


def archive_bounds(
    periods: dict[int, RecordingPeriodInfo],
) -> tuple[Optional[float], Optional[float]]:
    days = [p.archive_days for p in periods.values() if p.archive_days is not None]
    if not days:
        return None, None
    return min(days), max(days)


def _apply_system_event_health(
    system_events: dict[str, bool],
    status: str,
    reasons: list[str],
) -> str:
    for label in active_system_event_labels(
        system_events, labels=SYSTEM_EVENT_ERROR_LABELS
    ):
        status = HealthStatus.ERROR.value
        reasons.append(label)
    for label in active_system_event_labels(
        system_events, labels=SYSTEM_EVENT_WARN_LABELS
    ):
        if status != HealthStatus.ERROR.value:
            status = HealthStatus.WARN.value
        reasons.append(label)
    return status


def evaluate_recorder_health(
    poll: RecorderPollData,
    channel_statuses: list[str],
    settings: MonitoringSettings,
    *,
    archive_min_days: Optional[float] = None,
    archive_max_days: Optional[float] = None,
    profile: Optional[NvrApiProfile] = None,
) -> tuple[str, str]:
    if not poll.online:
        return HealthStatus.ERROR.value, poll.error or "NVR недоступен"

    reasons: list[str] = []
    status = HealthStatus.OK.value

    if poll.system_events:
        status = _apply_system_event_health(poll.system_events, status, reasons)

    if poll.storage:
        if poll.storage.worst_status and str(poll.storage.worst_status).lower() in (
            "error",
            "fail",
        ):
            status = HealthStatus.ERROR.value
            reasons.append(f"Диск: {poll.storage.worst_status}")
        if poll.storage.disks:
            max_temp = max_disk_temperature_celsius_from_disks(poll.storage.disks)
            if max_temp is not None:
                if max_temp >= settings.hdd_temperature_error_celsius:
                    status = HealthStatus.ERROR.value
                    reasons.append(
                        f"Температура HDD {max_temp:.0f} °C "
                        f"(критично ≥ {settings.hdd_temperature_error_celsius} °C)"
                    )
                elif max_temp >= settings.hdd_temperature_warn_celsius:
                    if status != HealthStatus.ERROR.value:
                        status = HealthStatus.WARN.value
                    reasons.append(
                        f"Температура HDD {max_temp:.0f} °C "
                        f"(предупреждение ≥ {settings.hdd_temperature_warn_celsius} °C)"
                    )
            if profile and profile.supports_modern_storage_metrics:
                if any_disk_format_required(poll.storage.disks):
                    status = HealthStatus.ERROR.value
                    reasons.append("Требуется форматирование накопителя")
                max_drop = max_disk_drop_datarate_percent(poll.storage.disks)
                if (
                    max_drop is not None
                    and max_drop >= settings.storage_drop_datarate_warn_percent
                ):
                    if status != HealthStatus.ERROR.value:
                        status = HealthStatus.WARN.value
                    reasons.append(
                        f"Потери записи на диск {max_drop:.1f}% "
                        f"(≥ {settings.storage_drop_datarate_warn_percent:.0f}%)"
                    )

    if poll.recording_storage_enable is False:
        status = HealthStatus.ERROR.value
        reasons.append("Запись на накопитель отключена")

    if poll.cpu_usage_max is not None:
        if poll.cpu_usage_max >= settings.cpu_usage_error_percent:
            status = HealthStatus.ERROR.value
            reasons.append(
                f"Нагрузка декодирования max {poll.cpu_usage_max:.1f}% "
                f"(критично ≥ {settings.cpu_usage_error_percent:.0f}%)"
            )
        elif poll.cpu_usage_max >= settings.cpu_usage_warn_percent:
            if status != HealthStatus.ERROR.value:
                status = HealthStatus.WARN.value
            reasons.append(
                f"Нагрузка декодирования max {poll.cpu_usage_max:.1f}% "
                f"(≥ {settings.cpu_usage_warn_percent:.0f}%)"
            )

    if poll.channels_zero_bitrate and poll.channels_zero_bitrate > 0:
        if status != HealthStatus.ERROR.value:
            status = HealthStatus.WARN.value
        reasons.append(
            f"Каналов с нулевым битрейтом: {poll.channels_zero_bitrate}"
        )

    if poll.channels_poe_off and poll.channels_poe_off > 0:
        if status != HealthStatus.ERROR.value:
            status = HealthStatus.WARN.value
        reasons.append(f"Каналов с выкл. PoE: {poll.channels_poe_off}")

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

    archive_check_days = archive_min_days
    if archive_check_days is None and poll.recording_period:
        archive_check_days = poll.recording_period.archive_days
    if archive_check_days is not None:
        if archive_check_days < settings.archive_days_error_threshold:
            status = HealthStatus.ERROR.value
            reasons.append(
                f"Глубина архива {archive_check_days:.1f} сут. "
                f"(критично < {settings.archive_days_error_threshold} сут.)"
            )
        elif archive_check_days < settings.archive_days_required:
            if status != HealthStatus.ERROR.value:
                status = HealthStatus.WARN.value
            if archive_min_days is not None and archive_max_days is not None:
                if archive_min_days != archive_max_days:
                    reasons.append(
                        f"Глубина архива {archive_min_days:.1f}-{archive_max_days:.1f} сут. "
                        f"(норма {settings.archive_days_required})"
                    )
                else:
                    reasons.append(
                        f"Глубина архива {archive_min_days:.1f} сут. "
                        f"(норма {settings.archive_days_required})"
                    )
            else:
                reasons.append(
                    f"Глубина архива {archive_check_days:.1f} сут. "
                    f"(норма {settings.archive_days_required})"
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


def _channel_info_from_row(row: ChannelRow) -> ChannelInfo:
    return ChannelInfo(
        channel_no=row.channel_no,
        name=row.name,
        source_state=row.source_state,
        camera_ip=row.camera_ip,
        camera_model=row.camera_model,
        data_rate=row.data_rate,
        cpu_usage=row.cpu_usage,
        poe_status=row.poe_status,
    )


def _upsert_channel_from_poll(
    state: StateStore,
    recorder_id: str,
    ch: ChannelInfo,
    event: Optional[EventChannelStatus],
    settings: MonitoringSettings,
    polled_at: datetime,
    period: Optional[RecordingPeriodInfo],
    *,
    device_model: Optional[str] = None,
    profile: Optional[NvrApiProfile] = None,
) -> str:
    h_status, h_reason = evaluate_channel_health(
        ch,
        event,
        settings,
        device_model=device_model,
        profile=profile,
    )
    state.upsert_channel(
        recorder_id,
        ch.channel_no,
        name=ch.name,
        camera_ip=ch.camera_ip,
        camera_model=ch.camera_model,
        source_state=ch.source_state,
        health_status=h_status,
        health_reason=h_reason,
        video_loss=event.video_loss if event else None,
        last_polled_at=polled_at,
        archive_start=period.start_time if period else None,
        archive_end=period.end_time if period else None,
        archive_days=period.archive_days if period else None,
        data_rate=ch.data_rate,
        cpu_usage=ch.cpu_usage,
        poe_status=ch.poe_status,
    )
    state.record_history(
        "channel",
        f"{recorder_id}:{ch.channel_no}",
        h_status,
        h_reason,
        polled_at,
    )
    return h_status


def apply_poll_result(
    store: ConfigStore,
    state: StateStore,
    recorder: Recorder,
    poll: RecorderPollData,
    settings: MonitoringSettings,
    polled_at: datetime,
    *,
    update_config: bool = True,
) -> Optional[RecorderStatusUpdate]:
    events_map = {e.channel_no: e for e in poll.events}
    channel_statuses: list[str] = []
    channel_nos: list[int] = []

    periods = poll.channel_recording_periods
    device_model = poll.device.model if poll.device else None
    profile = NvrApiProfile.from_device(poll.device) if poll.device else None

    if poll.channels_polled:
        for ch in poll.channels:
            event = events_map.get(ch.channel_no)
            period = periods.get(ch.channel_no)
            h_status = _upsert_channel_from_poll(
                state,
                recorder.id,
                ch,
                event,
                settings,
                polled_at,
                period,
                device_model=device_model,
                profile=profile,
            )
            channel_statuses.append(h_status)
            channel_nos.append(ch.channel_no)
        state.remove_channels_not_in(recorder.id, channel_nos)
    else:
        for row in state.list_channels(recorder.id):
            ch = _channel_info_from_row(row)
            event = events_map.get(ch.channel_no)
            if event is not None:
                h_status = _upsert_channel_from_poll(
                    state,
                    recorder.id,
                    ch,
                    event,
                    settings,
                    polled_at,
                    periods.get(ch.channel_no),
                    device_model=device_model,
                    profile=profile,
                )
                channel_statuses.append(h_status)
            else:
                channel_statuses.append(row.health_status)

    archive_min_days, archive_max_days = archive_bounds(periods)
    if archive_min_days is None and poll.recording_period:
        archive_min_days = poll.recording_period.archive_days
        archive_max_days = poll.recording_period.archive_days

    rec_status, rec_reason = evaluate_recorder_health(
        poll,
        channel_statuses,
        settings,
        archive_min_days=archive_min_days,
        archive_max_days=archive_max_days,
        profile=profile,
    )
    if poll.channels_polled:
        counts = _count_statuses(channel_statuses)
        channel_count = len(poll.channels)
        channels_ok = counts["ok"]
        channels_warn = counts["warn"]
        channels_error = counts["error"]
        channels_unknown = counts["unknown"]
    else:
        existing = state.get_recorder_metrics(recorder.id)
        if existing and existing.channel_count > 0:
            channel_count = existing.channel_count
            channels_ok = existing.channels_ok
            channels_warn = existing.channels_warn
            channels_error = existing.channels_error
            channels_unknown = existing.channels_unknown
        else:
            counts = _count_statuses(channel_statuses)
            channel_count = len(channel_statuses)
            channels_ok = counts["ok"]
            channels_warn = counts["warn"]
            channels_error = counts["error"]
            channels_unknown = counts["unknown"]

    storage_pct = poll.storage.used_percent if poll.storage else None
    storage_st = poll.storage.worst_status if poll.storage else None
    global_period = poll.recording_period
    archive_days = archive_max_days or (
        global_period.archive_days if global_period else None
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
        archive_start=global_period.start_time if global_period else None,
        archive_end=global_period.end_time if global_period else None,
        archive_days=archive_days,
        archive_min_days=archive_min_days,
        archive_max_days=archive_max_days,
        channel_count=channel_count,
        channels_ok=channels_ok,
        channels_warn=channels_warn,
        channels_error=channels_error,
        channels_unknown=channels_unknown,
        last_polled_at=polled_at,
        local_time=poll.date_time.local_time if poll.date_time else None,
        utc_time=poll.date_time.utc_time if poll.date_time else None,
        sync_type=poll.date_time.sync_type if poll.date_time else None,
        storage_used_mb=poll.storage.used_space_mb if poll.storage else None,
        storage_total_mb=poll.storage.total_space_mb if poll.storage else None,
        disks=poll.storage.disks if poll.storage else None,
        system_events=poll.system_events or None,
        storageinfo_ok=bool(poll.storage and poll.storage.storageinfo_ok),
        archive_poll_error=poll.recording_period_error,
        recording_storage_enable=poll.recording_storage_enable,
        recording_storage_overwrite=poll.recording_storage_overwrite,
        cpu_usage_max=poll.cpu_usage_max,
        cpu_usage_avg=poll.cpu_usage_avg,
        data_rate_total_mbps=poll.data_rate_total_mbps,
        channels_zero_bitrate=poll.channels_zero_bitrate or None,
        channels_poe_off=poll.channels_poe_off or None,
    )
    metrics = state.get_recorder_metrics(recorder.id)
    for category in CATEGORY_LABELS:
        cat_status, cat_reason = classify_category(
            category, recorder, metrics, settings
        )
        state.record_category_status(
            recorder.id,
            category,
            cat_status,
            cat_reason,
            polled_at,
        )
    state.record_history("recorder", recorder.id, rec_status, rec_reason, polled_at)

    check_status = CheckStatus.ONLINE if poll.online else CheckStatus.OFFLINE
    status_update = RecorderStatusUpdate(
        recorder_id=recorder.id,
        status=check_status,
        checked_at=polled_at,
        error=poll.error if not poll.online else None,
    )
    if update_config:
        store.update_recorder_statuses([status_update])
    return status_update


def _count_statuses(statuses: list[str]) -> dict[str, int]:
    counts = {"ok": 0, "warn": 0, "error": 0, "unknown": 0}
    for s in statuses:
        counts[s] = counts.get(s, 0) + 1
    return counts


@dataclass
class _WavePollResult:
    online: bool
    poll: RecorderPollData
    error: Optional[str] = None
    duration_ms: int = 0
    outcome: str = "offline"


@dataclass
class _RecorderPollState:
    attempts: int = 0
    success_attempt: Optional[int] = None


@dataclass
class PollCycleStats:
    total: int = 0
    responded: int = 0
    responded_after_retry: int = 0
    still_unreachable: int = 0


async def _fetch_poll_for_recorder(
    recorder: Recorder,
    credentials,
    *,
    include_inventory: bool,
) -> _WavePollResult:
    start = time.perf_counter()
    try:
        poll = await poll_recorder(
            recorder,
            credentials,
            include_inventory=include_inventory,
        )
        duration_ms = round((time.perf_counter() - start) * 1000)
        if poll.online:
            return _WavePollResult(
                online=True,
                poll=poll,
                duration_ms=duration_ms,
                outcome="success",
            )
        return _WavePollResult(
            online=False,
            poll=poll,
            error=poll.error,
            duration_ms=duration_ms,
            outcome="offline",
        )
    except Exception as exc:
        duration_ms = round((time.perf_counter() - start) * 1000)
        logger.exception("poll failed for %s", recorder.id)
        return _WavePollResult(
            online=False,
            poll=RecorderPollData(online=False, error=str(exc)),
            error=str(exc),
            duration_ms=duration_ms,
            outcome="error",
        )


async def poll_single_recorder(
    config_store: ConfigStore,
    state_store: StateStore,
    recorder: Recorder,
    *,
    include_inventory: bool = True,
    update_config: bool = True,
) -> Optional[RecorderStatusUpdate]:
    config = config_store.load()
    from .exclusions import is_pollable

    if not is_pollable(recorder, config):
        return None
    credentials = config.credentials
    settings = config.monitoring
    polled_at = datetime.now(timezone.utc)

    wave = await _fetch_poll_for_recorder(
        recorder,
        credentials,
        include_inventory=include_inventory,
    )
    return apply_poll_result(
        config_store,
        state_store,
        recorder,
        wave.poll,
        settings,
        polled_at,
        update_config=update_config,
    )


class PollCycleCancelled(Exception):
    """Массовый опрос прерван по запросу пользователя."""


async def _interruptible_sleep(
    seconds: float, cancel_event: Optional[asyncio.Event]
) -> None:
    if not cancel_event:
        await asyncio.sleep(seconds)
        return
    try:
        await asyncio.wait_for(cancel_event.wait(), timeout=seconds)
    except asyncio.TimeoutError:
        return
    if cancel_event.is_set():
        raise PollCycleCancelled()


async def _abort_wave_tasks(tasks: list[asyncio.Task]) -> None:
    for task in tasks:
        if not task.done():
            task.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


def _poll_retry_settings(config) -> tuple[int, int]:
    settings = config.monitoring
    if settings.poll_retry_enabled and settings.poll_retry_max > 0:
        return 1 + settings.poll_retry_max, settings.poll_retry_delay_seconds
    return 1, settings.poll_retry_delay_seconds


async def run_poll_cycle(
    config_store: ConfigStore,
    state_store: StateStore,
    *,
    include_inventory: bool = False,
    job_id: Optional[str] = None,
    tracker: Optional["PollJobTracker"] = None,
    cancel_event: Optional[asyncio.Event] = None,
) -> PollCycleStats:
    from .exclusions import pollable_recorders

    config = config_store.load()
    recorders = pollable_recorders(config)
    stats = PollCycleStats(total=len(recorders))
    max_attempts, retry_delay = _poll_retry_settings(config)

    if tracker:
        await tracker.set_total(len(recorders))
        await tracker.set_retry_config(max_attempts, retry_delay)
    if not recorders:
        return stats
    credentials = config.credentials
    settings = config.monitoring
    sem = asyncio.Semaphore(config.monitoring.max_concurrent_polls)
    status_updates: list[RecorderStatusUpdate] = []
    poll_states: dict[str, _RecorderPollState] = {
        rec.id: _RecorderPollState() for rec in recorders
    }
    pending: list[Recorder] = list(recorders)
    attempt = 0

    async def _poll_wave_one(rec: Recorder) -> tuple[Recorder, _WavePollResult]:
        if tracker:
            await tracker.recorder_started(rec)
        async with sem:
            result = await _fetch_poll_for_recorder(
                rec,
                credentials,
                include_inventory=include_inventory,
            )
        if tracker:
            await tracker.recorder_attempt_finished(rec)
        return rec, result

    try:
        while pending and attempt < max_attempts:
            if cancel_event and cancel_event.is_set():
                raise PollCycleCancelled()
            attempt += 1
            if attempt > 1 and tracker:
                await tracker.set_waiting_retry(
                    attempt, len(pending), retry_delay, max_attempts
                )
                await _interruptible_sleep(retry_delay, cancel_event)
            if tracker:
                await tracker.set_polling_round(attempt, len(pending))

            still_pending: list[Recorder] = []
            polled_at = datetime.now(timezone.utc)
            wave_tasks = [
                asyncio.create_task(_poll_wave_one(r), name=f"poll-{r.id}")
                for r in pending
            ]

            async def _apply_wave_result(rec: Recorder, wave: _WavePollResult) -> None:
                state = poll_states[rec.id]
                state.attempts = attempt

                if job_id:
                    state_store.insert_poll_attempt(
                        job_id=job_id,
                        recorder_id=rec.id,
                        attempt=attempt,
                        outcome=wave.outcome,
                        online=wave.online,
                        error=wave.error,
                        duration_ms=wave.duration_ms,
                        recorded_at=polled_at,
                    )

                if wave.online:
                    state.success_attempt = attempt
                    update = apply_poll_result(
                        config_store,
                        state_store,
                        rec,
                        wave.poll,
                        settings,
                        polled_at,
                        update_config=False,
                    )
                    if update is not None:
                        status_updates.append(update)
                    stats.responded += 1
                    if attempt > 1:
                        stats.responded_after_retry += 1
                    if tracker:
                        await tracker.recorder_final_finished(
                            rec,
                            success=True,
                            after_retry=attempt > 1,
                        )
                elif attempt >= max_attempts:
                    update = apply_poll_result(
                        config_store,
                        state_store,
                        rec,
                        wave.poll,
                        settings,
                        polled_at,
                        update_config=False,
                    )
                    if update is not None:
                        status_updates.append(update)
                    stats.still_unreachable += 1
                    if tracker:
                        await tracker.recorder_final_finished(
                            rec,
                            success=False,
                            after_retry=False,
                            error=wave.error,
                        )
                else:
                    still_pending.append(rec)

            for finished in asyncio.as_completed(wave_tasks):
                if cancel_event and cancel_event.is_set():
                    await _abort_wave_tasks(wave_tasks)
                    raise PollCycleCancelled()
                rec, wave = await finished
                await _apply_wave_result(rec, wave)

            pending = still_pending
    finally:
        if job_id:
            for rec in recorders:
                state = poll_states[rec.id]
                if state.attempts <= 0:
                    continue
                state_store.update_poll_recorder_summary(
                    rec.id,
                    job_id=job_id,
                    attempts=state.attempts,
                    success_attempt=state.success_attempt,
                    first_try_ok=state.success_attempt == 1,
                )
        if status_updates:
            config_store.update_recorder_statuses(status_updates)

    logger.info(
        "poll cycle done",
        extra={
            "recorders": len(recorders),
            "responded": stats.responded,
            "after_retry": stats.responded_after_retry,
            "unreachable": stats.still_unreachable,
            "attempts": max_attempts,
        },
    )
    return stats


async def run_inventory_cycle(
    config_store: ConfigStore,
    state_store: StateStore,
) -> None:
    await run_poll_cycle(config_store, state_store, include_inventory=True)


@dataclass
class NtpFixAllResult:
    success: int = 0
    failed: int = 0
    total: int = 0
    errors: list[str] = field(default_factory=list)


async def run_ntp_fix_all(
    config_store: ConfigStore,
    state_store: StateStore,
) -> NtpFixAllResult:
    from .ui.metrics_helpers import show_ntp_action_button

    config = config_store.load()
    credentials = config.credentials
    ntp_server = (config.monitoring.ntp_server or "").strip()
    posix_tz = (config.monitoring.ntp_posix_timezone or "").strip()

    result = NtpFixAllResult()
    if not ntp_server:
        result.errors.append("Не задан monitoring.ntp_server в config.json")
        return result
    if not credentials.username or not credentials.password:
        result.errors.append("Не заданы учётные данные API в настройках")
        return result

    metrics_map = {
        m.recorder_id: m for m in state_store.list_recorder_metrics()
    }
    from .exclusions import is_pollable

    fixable = [
        r
        for r in config.recorders
        if is_pollable(r, config)
        and (m := metrics_map.get(r.id))
        and m.device_online
        and show_ntp_action_button(m)
    ]
    result.total = len(fixable)
    if not fixable:
        return result

    sem = asyncio.Semaphore(config.monitoring.max_concurrent_polls)
    ntp_status_updates: list[RecorderStatusUpdate] = []

    async def _one_ntp(rec: Recorder) -> None:
        async with sem:
            try:
                fix_result = await enable_recorder_ntp(
                    rec,
                    credentials,
                    ntp_server,
                    posix_timezone=posix_tz,
                )
                if not fix_result.success:
                    result.failed += 1
                    result.errors.append(
                        f"{rec.id}: {fix_result.error or 'ошибка NTP'}"
                    )
                    return
                update = await poll_single_recorder(
                    config_store,
                    state_store,
                    rec,
                    include_inventory=False,
                    update_config=False,
                )
                if update is not None:
                    ntp_status_updates.append(update)
                result.success += 1
            except Exception as exc:
                result.failed += 1
                result.errors.append(f"{rec.id}: {exc}")
                logger.exception("ntp fix failed for %s", rec.id)

    await asyncio.gather(*[_one_ntp(r) for r in fixable])
    if ntp_status_updates:
        config_store.update_recorder_statuses(ntp_status_updates)
    return result
