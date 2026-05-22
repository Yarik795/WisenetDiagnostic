from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


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
    enabled: bool = True

    @field_validator("object_name", "host")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


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
    ntp_server: str = ""
    ntp_posix_timezone: str = "STWT-3STWST,M3.5.0/1:00:00,M10.5.0/1:00:00"

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


class AppConfig(BaseModel):
    credentials: Credentials = Field(default_factory=Credentials)
    recorders: list[Recorder] = Field(default_factory=list)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)


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
