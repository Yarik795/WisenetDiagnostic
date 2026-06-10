from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Literal, Optional
from zoneinfo import ZoneInfo

from .config_store import ConfigStore
from .display_time import get_display_tz, to_display
from .logging_config import get_logger
from .email_sender import send_report_email
from .exclusions import excluded_ids_set, pollable_recorders
from .models import AppConfig, EmailReportSettings
from .report_delivery_history import (
    DeliveryTrigger,
    ReportDeliveryHistory,
    ReportDeliveryHistoryStore,
    ReportDeliveryRecord,
)
from .state_store import StateStore
from .ui.error_report import ErrorReportContext, build_error_report_context
from .ui.error_report_render import (
    build_email_dashboard_context,
    build_email_subject,
    render_email_dashboard_html,
    render_error_report_html,
)
from .ui.email_history_series import (
    aggregate_successful_by_local_day,
    kpi_delta_vs_previous_day,
)

logger = get_logger("report_delivery")

_SCHEDULED_TRIGGERS = frozenset({"scheduled", "catchup"})


@dataclass(frozen=True)
class SendDecision:
    should_send: bool
    trigger: Optional[DeliveryTrigger] = None
    reason: str = ""


@dataclass(frozen=True)
class SendResult:
    ok: bool
    message: str


def parse_send_time(send_time: str) -> time:
    hour_s, minute_s = send_time.split(":")
    return time(int(hour_s), int(minute_s))


def _local_now(now: datetime, tz: ZoneInfo) -> datetime:
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now.astimezone(tz)


def _sent_on_local_date(sent_at: datetime, tz: ZoneInfo) -> date:
    displayed = to_display(sent_at)
    if displayed is not None:
        return displayed.date()
    if sent_at.tzinfo is None:
        sent_at = sent_at.replace(tzinfo=timezone.utc)
    return sent_at.astimezone(tz).date()


def _last_success_for_triggers(
    history: ReportDeliveryHistory,
    triggers: frozenset[str],
) -> Optional[ReportDeliveryRecord]:
    for entry in reversed(history.entries):
        if entry.status == "success" and entry.trigger in triggers:
            return entry
    return None


def _hours_since_last_success(
    now: datetime, history: ReportDeliveryHistory
) -> Optional[float]:
    last = history.last_success()
    if last is None:
        return None
    ref = now if now.tzinfo else now.replace(tzinfo=timezone.utc)
    sent = last.sent_at if last.sent_at.tzinfo else last.sent_at.replace(tzinfo=timezone.utc)
    return (ref - sent).total_seconds() / 3600.0


def validate_email_config(settings: EmailReportSettings) -> list[str]:
    errors: list[str] = []
    if not settings.from_email:
        errors.append("не задан from_email")
    if not settings.to_emails:
        errors.append("пустой to_emails")
    if not settings.smtp_host:
        errors.append("не задан smtp_host")
    return errors


def should_send_report(
    now: datetime,
    settings: EmailReportSettings,
    history: ReportDeliveryHistory,
    *,
    display_tz: ZoneInfo | None = None,
) -> SendDecision:
    if not settings.enabled:
        return SendDecision(False, reason="email_report disabled")

    tz = display_tz or get_display_tz()
    local_now = _local_now(now, tz)
    today = local_now.date()
    send_at = parse_send_time(settings.send_time)

    last_scheduled = _last_success_for_triggers(history, _SCHEDULED_TRIGGERS)
    if last_scheduled is not None:
        if _sent_on_local_date(last_scheduled.sent_at, tz) == today:
            return SendDecision(False, reason="already sent successfully today")

    hours_since = _hours_since_last_success(now, history)
    catchup_due = hours_since is None or hours_since >= settings.catchup_after_hours
    if catchup_due:
        return SendDecision(True, trigger="catchup", reason="catchup after 24h")

    last = history.last_entry()
    if last is not None and last.status == "failed":
        ref = now if now.tzinfo else now.replace(tzinfo=timezone.utc)
        sent = last.sent_at if last.sent_at.tzinfo else last.sent_at.replace(tzinfo=timezone.utc)
        minutes = (ref - sent).total_seconds() / 60.0
        if minutes < settings.failed_retry_minutes:
            return SendDecision(
                False,
                reason=f"last attempt failed, retry in {settings.failed_retry_minutes} min",
            )

    if local_now.time() >= send_at:
        return SendDecision(True, trigger="scheduled", reason="scheduled send_time reached")

    return SendDecision(False, reason="before send_time")


def report_metrics_from_context(report: ErrorReportContext) -> tuple[int, int, dict[str, int]]:
    problem_count = report.problem_count
    recorder_ids = {row.recorder.id for row in report.rows}
    category_counts: dict[str, int] = {}
    for row in report.rows:
        label = row.category_label
        category_counts[label] = category_counts.get(label, 0) + 1
    return problem_count, len(recorder_ids), category_counts


def _metrics_map(state: StateStore) -> dict:
    from .ui.grouping import metrics_map_from_list

    return metrics_map_from_list(state.list_recorder_metrics())


def _has_poll_data(config: AppConfig, metrics_map: dict) -> bool:
    pollable = pollable_recorders(config)
    if not pollable:
        return False
    return any(r.id in metrics_map for r in pollable)


def _subject_delta_problems(
    history: ReportDeliveryHistory,
    problem_count: int,
    settings: EmailReportSettings,
) -> Optional[int]:
    tz = get_display_tz()
    points = aggregate_successful_by_local_day(
        history, tz=tz, days=settings.email_trend_days
    )
    delta_p, _ = kpi_delta_vs_previous_day(points)
    if delta_p is not None:
        return delta_p
    last = history.last_success()
    if last is not None:
        return problem_count - last.problem_count
    return None


class ReportDeliveryService:
    def __init__(
        self,
        config_store: ConfigStore | None = None,
        state_store: StateStore | None = None,
        history_store: ReportDeliveryHistoryStore | None = None,
    ) -> None:
        self.config_store = config_store or ConfigStore()
        self.state_store = state_store or StateStore()
        self.history_store = history_store or ReportDeliveryHistoryStore()

    def tick_sync(self) -> None:
        config = self.config_store.load()
        email_cfg = config.email_report
        if not email_cfg.enabled:
            return

        now = datetime.now(timezone.utc)
        history = self.history_store.load()
        decision = should_send_report(now, email_cfg, history)
        if not decision.should_send or decision.trigger is None:
            logger.debug("report delivery skip: %s", decision.reason)
            return

        result = self.send_report_now(trigger=decision.trigger, now=now)
        if not result.ok:
            logger.info(
                "report delivery skip: %s",
                result.message,
                extra={"event": "report_delivery_skip"},
            )

    def send_report_now(
        self,
        *,
        trigger: DeliveryTrigger,
        now: datetime | None = None,
    ) -> SendResult:
        config = self.config_store.load()
        email_cfg = config.email_report
        config_errors = validate_email_config(email_cfg)
        if config_errors:
            return SendResult(
                ok=False,
                message="Настройте email_report в config.json: " + "; ".join(config_errors),
            )
        if trigger == "manual" and not email_cfg.enabled:
            logger.warning(
                "manual report email while email_report.enabled is false",
                extra={"event": "report_delivery_manual_disabled"},
            )

        if now is None:
            now = datetime.now(timezone.utc)

        metrics_map = _metrics_map(self.state_store)
        if not _has_poll_data(config, metrics_map):
            return SendResult(
                ok=False,
                message="Нет данных опроса — сначала выполните опрос регистраторов",
            )

        history = self.history_store.load()
        recorders = self.config_store.list_recorders()
        report = build_error_report_context(
            recorders,
            metrics_map,
            config.monitoring,
            credentials=config.credentials,
            ntp_server=config.monitoring.ntp_server or "",
            device_auth="userinfo",
            problem_since_map=self.state_store.category_problem_since_map(),
            recorder_problem_since_map=self.state_store.recorder_problem_since_map(),
            excluded_ids=excluded_ids_set(config),
        )
        problem_count, recorders_with_errors, category_counts = report_metrics_from_context(
            report
        )

        attachment_html = render_error_report_html(report)
        attachment_name = (
            "wisenet-tso-errors-"
            f"{format_for_delivery_filename(now)}.html"
        )
        dashboard_ctx = build_email_dashboard_context(
            report=report,
            history=history,
            trigger=trigger,
            settings=email_cfg,
            recorders_with_errors=recorders_with_errors,
        )
        body_html = render_email_dashboard_html(dashboard_ctx)
        delta_p = _subject_delta_problems(history, problem_count, email_cfg)
        subject = build_email_subject(
            email_cfg,
            problem_count=problem_count,
            recorders_with_errors=recorders_with_errors,
            delta_problems=delta_p,
            sent_at=now,
        )

        error_msg: str | None = None
        status: Literal["success", "failed"] = "success"
        try:
            send_report_email(
                email_cfg,
                body_html=body_html,
                attachment_html=attachment_html,
                attachment_filename=attachment_name,
                subject=subject,
            )
            logger.info(
                "report email sent",
                extra={
                    "event": "report_delivery_sent",
                    "extra_trigger": trigger,
                    "extra_problem_count": problem_count,
                    "extra_recorders_with_errors": recorders_with_errors,
                },
            )
        except Exception as exc:
            status = "failed"
            error_msg = str(exc)
            logger.exception(
                "report email failed",
                extra={
                    "event": "report_delivery_failed",
                    "extra_trigger": trigger,
                },
            )
            short = error_msg[:200] + ("…" if len(error_msg) > 200 else "")
            return SendResult(ok=False, message=f"Ошибка отправки: {short}")

        self.history_store.append(
            ReportDeliveryRecord(
                sent_at=now,
                problem_count=problem_count,
                recorders_with_errors=recorders_with_errors,
                category_counts=category_counts,
                status=status,
                trigger=trigger,
                error=error_msg,
            ),
            max_entries=email_cfg.history_max_entries,
        )
        recipients = ", ".join(email_cfg.to_emails)
        return SendResult(ok=True, message=f"Отчёт отправлен на {recipients}")


def format_for_delivery_filename(now: datetime) -> str:
    from .display_time import format_for_display

    return format_for_display(now, "%Y%m%d-%H%M")
