"""Navigator agent tests: verify the retry/backoff wrapper without ever
launching a real browser (the internal fetch method is monkeypatched)."""
import pytest

from app.agents.navigator_agent import NavigatorAgent
from app.core.exceptions import CaptchaSolveError


class _AlwaysFailingSolver:
    def solve(self, image_bytes: bytes) -> str:
        raise CaptchaSolveError("bad captcha")


def test_retries_on_captcha_failure_then_raises(monkeypatch):
    agent = NavigatorAgent(captcha_solver=_AlwaysFailingSolver())
    calls = {"n": 0}

    def fake_fetch(department):
        calls["n"] += 1
        raise CaptchaSolveError("simulated failure")

    monkeypatch.setattr(agent, "_navigate_and_fetch", fake_fetch)
    monkeypatch.setattr("app.agents.navigator_agent.settings.captcha_max_retries", 3)

    with pytest.raises(CaptchaSolveError):
        agent.run("Social Welfare")

    assert calls["n"] == 3


def test_succeeds_after_transient_captcha_failure(monkeypatch):
    agent = NavigatorAgent(captcha_solver=_AlwaysFailingSolver())
    attempts = {"n": 0}

    def flaky_fetch(department):
        attempts["n"] += 1
        if attempts["n"] < 2:
            raise CaptchaSolveError("transient")
        return "<html>ok</html>"

    monkeypatch.setattr(agent, "_navigate_and_fetch", flaky_fetch)

    result = agent.run("Social Welfare")
    assert result == "<html>ok</html>"