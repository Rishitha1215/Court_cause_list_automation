"""API schema for Notification history."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.notification import NotificationStatus


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_id: int
    advocate_id: int
    status: NotificationStatus
    error_message: Optional[str]
    sent_at: Optional[datetime]
    created_at: datetime