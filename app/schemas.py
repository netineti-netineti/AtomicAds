from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


class AlertCreate(BaseModel):
    title: str
    body: str
    severity: Severity
    delivery_types: Optional[List[str]] = ["inapp"]
    start_at: Optional[datetime]
    expires_at: Optional[datetime]
    reminders_enabled: Optional[bool] = True
    reminder_frequency_minutes: Optional[int] = 120
    visibility: Optional[Dict] = {"org": False, "teams": [], "users": []}


class AlertUpdate(BaseModel):
    title: Optional[str]
    body: Optional[str]
    severity: Optional[Severity]
    reminders_enabled: Optional[bool]
    start_at: Optional[datetime]
    expires_at: Optional[datetime]
    reminder_frequency_minutes: Optional[int]
    visibility: Optional[Dict]


class UserActionResponse(BaseModel):
    success: bool
    detail: Optional[str]