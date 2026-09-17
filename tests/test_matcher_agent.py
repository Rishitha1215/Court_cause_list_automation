"""Matcher agent tests: pure business logic over an in-memory DB."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agents.matcher_agent import MatcherAgent
from app.core.security import hash_password
from app.database import Base
from app.models.advocate import Advocate
from app.models.user import User, UserRole
from app.repositories.notification_repository import NotificationRepository
from app.schemas.case_schema import CaseCreate


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def _make_advocate(db, name: str, email: str) -> Advocate:
    user = User(email=email, hashed_password=hash_password("x"), role=UserRole.ADVOCATE)
    db.add(user)
    db.flush()
    advocate = Advocate(user_id=user.id, full_name=name, department="Social Welfare")
    db.add(advocate)
    db.commit()
    return advocate


def test_matches_registered_advocate_by_name(db_session, monkeypatch):
    monkeypatch.setattr("app.agents.matcher_agent.download_pdf", lambda *a, **k: None)
    advocate = _make_advocate(db_session, "K. Suresh", "suresh@example.com")

    case_data = CaseCreate(
        case_number="WP/1/2026", cause_list_date="2026-07-21",
        petitioner_advocate="K. Suresh", department="Social Welfare",
    )

    matcher = MatcherAgent(db_session)
    matches = matcher.run([case_data], department="Social Welfare")

    assert len(matches) == 1
    assert matches[0][1].id == advocate.id


def test_does_not_rematch_already_notified_case(db_session, monkeypatch):
    monkeypatch.setattr("app.agents.matcher_agent.download_pdf", lambda *a, **k: None)
    advocate = _make_advocate(db_session, "K. Suresh", "suresh@example.com")
    case_data = CaseCreate(
        case_number="WP/2/2026", cause_list_date="2026-07-21",
        petitioner_advocate="K. Suresh", department="Social Welfare",
    )

    matcher = MatcherAgent(db_session)
    first = matcher.run([case_data], department="Social Welfare")
    assert len(first) == 1

    case_id = first[0][0].id
    NotificationRepository(db_session).create_pending(case_id, advocate.id)
    db_session.commit()

    second = matcher.run([case_data], department="Social Welfare")
    assert second == []