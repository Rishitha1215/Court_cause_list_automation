"""Notification -- one row per email attempt for a (case, advocate) pair.
The unique constraint is the hard guarantee against duplicate emails."""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Text, Enum, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        UniqueConstraint("case_id", "advocate_id", name="uq_notification_case_advocate"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), nullable=False)
    advocate_id: Mapped[int] = mapped_column(ForeignKey("advocates.id"), nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus), default=NotificationStatus.PENDING, nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    case: Mapped["Case"] = relationship(back_populates="notifications")
    advocate: Mapped["Advocate"] = relationship(back_populates="notifications")