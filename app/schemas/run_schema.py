"""API schemas for scheduler run history (admin dashboard)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.run_log import RunStatus


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    triggered_by: str
    status: RunStatus
    departments: Optional[str]
    cases_found: int
    new_cases: int
    notifications_sent: int
    error_message: Optional[str]
    started_at: datetime
    finished_at: Optional[datetime]