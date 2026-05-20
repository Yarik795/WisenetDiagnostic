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


class AppConfig(BaseModel):
    credentials: Credentials = Field(default_factory=Credentials)
    recorders: list[Recorder] = Field(default_factory=list)


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
