"""Logger Agent: thin wrapper the Orchestrator uses to record run-level and
step-level activity, so the admin dashboard has a consistent audit trail
regardless of which other agent produced the event."""
from typing import Optional

from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.models.run_log import RunLog, RunStatus
from app.repositories.run_repository import RunRepository


class LoggerAgent(BaseAgent):
    def __init__(self, db: Session):
        super().__init__()
        self.repo = RunRepository(db)

    def start_run(self, triggered_by: str, departments: list[str]) -> RunLog:
        return self.repo.start_run(triggered_by, departments)

    def log_step(self, run_id: int, agent_name: str, action: str, status: str,
                  message: Optional[str] = None) -> None:
        self.repo.log_action(run_id, agent_name, action, status, message)
        log_fn = self.logger.info if status == "success" else self.logger.error
        log_fn("[run=%s] %s.%s -> %s %s", run_id, agent_name, action, status, message or "")

    def finish_run(self, run: RunLog, status: RunStatus, cases_found: int, new_cases: int,
                    notifications_sent: int, error_message: Optional[str] = None) -> None:
        self.repo.finish_run(run, status, cases_found, new_cases, notifications_sent, error_message)

    def run(self, *args, **kwargs):
        # LoggerAgent is used via its named methods above rather than a
        # single run() call, but BaseAgent requires the method to exist.
        raise NotImplementedError("LoggerAgent is used via start_run/log_step/finish_run")