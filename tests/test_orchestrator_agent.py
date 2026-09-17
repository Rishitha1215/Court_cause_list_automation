"""Orchestrator agent tests: verify one department's failure does not stop
the rest of the run, against an isolated in-memory database."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.database as database_module
from app.agents.orchestrator_agent import OrchestratorAgent
from app.core.exceptions import NavigationError


@pytest.fixture()
def isolated_db(monkeypatch):
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    database_module.Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine)
    monkeypatch.setattr(database_module, "SessionLocal", test_session)
    yield


def test_continues_after_one_department_fails(monkeypatch, isolated_db):
    monkeypatch.setattr("app.config.settings.court_departments", "Social Welfare,Civil")

    orchestrator = OrchestratorAgent()
    calls = {"n": 0}

    def fake_navigate(department):
        calls["n"] += 1
        if department == "Social Welfare":
            raise NavigationError("site down")
        return "<html></html>"

    monkeypatch.setattr(orchestrator.navigator, "run", fake_navigate)
    monkeypatch.setattr(orchestrator.extractor, "run", lambda *a, **k: [])

    orchestrator.run_full_cycle(triggered_by="test")

    assert calls["n"] == 2