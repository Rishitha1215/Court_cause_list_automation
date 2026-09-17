"""Data access for Notification records. The sole gate that guarantees no
duplicate email is ever sent for the same (case, advocate) pair."""
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationStatus


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def exists(self, case_id: int, advocate_id: int) -> bool:
        return (
            self.db.query(Notification)
            .filter(Notification.case_id == case_id, Notification.advocate_id == advocate_id)
            .first()
            is not None
        )

    def create_pending(self, case_id: int, advocate_id: int) -> Notification:
        notification = Notification(case_id=case_id, advocate_id=advocate_id, status=NotificationStatus.PENDING)
        self.db.add(notification)
        self.db.flush()
        return notification

    def mark_sent(self, notification: Notification) -> None:
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.utcnow()
        self.db.flush()

    def mark_failed(self, notification: Notification, error_message: str) -> None:
        notification.status = NotificationStatus.FAILED
        notification.error_message = error_message
        self.db.flush()

    def list_for_advocate(self, advocate_id: int, limit: int = 100) -> list[Notification]:
        return (
            self.db.query(Notification)
            .filter(Notification.advocate_id == advocate_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

    def list_failed(self, limit: int = 100) -> list[Notification]:
        return (
            self.db.query(Notification)
            .filter(Notification.status == NotificationStatus.FAILED)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )