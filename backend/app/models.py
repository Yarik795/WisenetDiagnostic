from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .device_kinds import DeviceKind


class CheckStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    DISABLED = "disabled"


class Credentials(BaseModel):
    username: str = ""
    password: str = ""


class CredentialsUpdate(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class RecorderBase(BaseModel):
    object_name: str = Field(..., min_length=1)
    name: Optional[str] = None
    host: str = Field(..., min_length=1)
    port: int = Field(default=80, ge=1, le=65535)
    use_https: bool = False
    device_kind: DeviceKind = "tsv"
    mac: Optional[str] = None

    @field_validator("object_name", "host")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()

    @field_validator("mac")
    @classmethod
    def strip_mac(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        stripped = v.strip()
        return stripped or None


class Recorder(RecorderBase):
    id: str
    last_status: Optional[CheckStatus] = None
    last_check_at: Optional[datetime] = None
    last_error: Optional[str] = None


class RecorderCreate(RecorderBase):
    pass


class RecorderUpdate(RecorderBase):
    pass


class MonitoringSettings(BaseModel):
    poll_interval_minutes: int = Field(default=5, ge=1, le=1440)
    full_poll_interval_minutes: int = Field(default=15, ge=1, le=1440)
    max_concurrent_polls: int = Field(default=5, ge=1, le=50)
    archive_days_required: int = Field(default=30, ge=1, le=365)
    time_skew_warn_seconds: int = Field(default=60, ge=1)
    time_skew_error_seconds: int = Field(default=300, ge=1)
    hdd_temperature_warn_celsius: int = Field(default=50, ge=1, le=120)
    hdd_temperature_error_celsius: int = Field(default=60, ge=1, le=120)
    archive_days_error_threshold: int = Field(default=7, ge=0, le=365)
    channels_error_threshold_percent: int = Field(default=25, ge=1, le=100)
    cpu_usage_warn_percent: float = Field(default=80.0, ge=0.0, le=100.0)
    cpu_usage_error_percent: float = Field(default=95.0, ge=0.0, le=100.0)
    storage_drop_datarate_warn_percent: float = Field(
        default=5.0, ge=0.0, le=100.0
    )
    ntp_server: str = ""
    ntp_posix_timezone: str = "STWT-3STWST,M3.5.0/1:00:00,M10.5.0/1:00:00"
    display_timezone: str = "Europe/Moscow"
    poll_retry_enabled: bool = True
    poll_retry_max: int = Field(default=3, ge=0, le=10)
    poll_retry_delay_seconds: int = Field(default=5, ge=1, le=120)

    @field_validator("cpu_usage_error_percent")
    @classmethod
    def cpu_error_above_warn(cls, v: float, info) -> float:
        warn = info.data.get("cpu_usage_warn_percent")
        if warn is not None and v < warn:
            raise ValueError(
                "cpu_usage_error_percent must be >= cpu_usage_warn_percent"
            )
        return v

    @field_validator("hdd_temperature_error_celsius")
    @classmethod
    def hdd_temp_error_above_warn(cls, v: int, info) -> int:
        warn = info.data.get("hdd_temperature_warn_celsius")
        if warn is not None and v < warn:
            raise ValueError(
                "hdd_temperature_error_celsius must be >= hdd_temperature_warn_celsius"
            )
        return v

    @field_validator("archive_days_error_threshold")
    @classmethod
    def archive_error_below_required(cls, v: int, info) -> int:
        required = info.data.get("archive_days_required")
        if required is not None and v > required:
            raise ValueError(
                "archive_days_error_threshold must be <= archive_days_required"
            )
        return v


class ExclusionSettings(BaseModel):
    """Регистраторы из списка не опрашиваются и не попадают в отчёты/дашборды проблем."""

    recorder_ids: list[str] = Field(default_factory=list)


class EmailReportSettings(BaseModel):
    enabled: bool = False
    smtp_host: str = "MTA.SIGMA.SBRF.RU"
    smtp_port: int = Field(default=25, ge=1, le=65535)
    use_starttls: bool = True
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = ""
    to_emails: list[str] = Field(default_factory=list)
    subject: str = "Wisenet Диагностика — отчёт по ошибкам"
    send_time: str = "09:30"
    catchup_after_hours: int = Field(default=24, ge=1, le=168)
    history_max_entries: int = Field(default=90, ge=7, le=365)
    dashboard_history_days: int = Field(default=30, ge=7, le=90)
    email_trend_days: int = Field(default=7, ge=7, le=14)
    failed_retry_minutes: int = Field(default=60, ge=5, le=240)

    @field_validator("send_time")
    @classmethod
    def validate_send_time(cls, v: str) -> str:
        parts = v.strip().split(":")
        if len(parts) != 2:
            raise ValueError("send_time must be HH:MM")
        hour, minute = int(parts[0]), int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("send_time must be a valid HH:MM")
        return f"{hour:02d}:{minute:02d}"


class AppConfig(BaseModel):
    credentials: Credentials = Field(default_factory=Credentials)
    recorders: list[Recorder] = Field(default_factory=list)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    exclusions: ExclusionSettings = Field(default_factory=ExclusionSettings)
    email_report: EmailReportSettings = Field(default_factory=EmailReportSettings)


class CheckResult(BaseModel):
    status: CheckStatus
    checked_at: datetime
    error: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    device_type: Optional[str] = None


class RecorderCheckResponse(BaseModel):
    recorder: Recorder
    check: CheckResult
