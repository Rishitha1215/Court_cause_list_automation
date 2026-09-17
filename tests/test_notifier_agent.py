"""Notifier agent tests: verifies duplicate-prevention state transitions."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agents.notifier_agent import NotifierAgent
from app.core.exceptions import NotificationDeliveryError
from app.core.security import hash_password
from app.database import Base
from app.models.advocate import Advocate
from app.models.case import Case
from app.models.notification import Notification, NotificationStatus
from app.models.user import User, UserRole


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def _setup(db):
    user = User(email="a@example.com", hashed_password=hash_password("x"), role=UserRole.ADVOCATE)
    db.add(user)
    db.flush()
    advocate = Advocate(user_id=user.id, full_name="K. Suresh")
    db.add(advocate)
    case = Case(case_number="WP/1/2026", cause_list_date="2026-07-21")
    db.add(case)
    db.commit()
    return advocate, case


def test_marks_notification_sent_on_success(db_session, monkeypatch):
    advocate, case = _setup(db_session)
    monkeypatch.setattr("app.agents.notifier_agent.send_case_notification", lambda a, c: None)

    notifier = NotifierAgent(db_session)
    sent = notifier.run([(case, advocate)])

    assert sent == 1
    notification = db_session.query(Notification).one()
    assert notification.status == NotificationStatus.SENT


def test_marks_notification_failed_without_raising(db_session, monkeypatch):
    advocate, case = _setup(db_session)

    def _raise(a, c):
        raise NotificationDeliveryError("smtp down")

    monkeypatch.setattr("app.agents.notifier_agent.send_case_notification", _raise)

    notifier = NotifierAgent(db_session)
    sent = notifier.run([(case, advocate)])

    assert sent == 0
    notification = db_session.query(Notification).one()
    assert notification.status == NotificationStatus.FAILED