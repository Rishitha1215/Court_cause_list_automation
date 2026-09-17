"""Data access for RunLog / AgentActionLog -- the scheduler and admin
dashboard's audit trail."""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.run_log import RunLog, AgentActionLog, RunStatus


class RunRepository:
    def __init__(self, db: Session):
        self.db = db

    def start_run(self, triggered_by: str, departments: list[str]) -> RunLog:
        run = RunLog(triggered_by=triggered_by, status=RunStatus.RUNNING, departments=",".join(departments))
        self.db.add(run)
        self.db.flush()
        return run

    def log_action(self, run_id: int, agent_name: str, action: str, status: str,
                    message: Optional[str] = None) -> None:
        self.db.add(
            AgentActionLog(run_id=run_id, agent_name=agent_name, action=action, status=status, message=message)
        )
        self.db.flush()

    def finish_run(self, run: RunLog, status: RunStatus, cases_found: int, new_cases: int,
                    notifications_sent: int, error_message: Optional[str] = None) -> None:
        run.status = status
        run.cases_found = cases_found
        run.new_cases = new_cases
        run.notifications_sent = notifications_sent
        run.error_message = error_message
        run.finished_at = datetime.utcnow()
        self.db.flush()

    def list_recent(self, limit: int = 20) -> list[RunLog]:
        return self.db.query(RunLog).order_by(RunLog.started_at.desc()).limit(limit).all()

    def get(self, run_id: int) -> Optional[RunLog]:
        return self.db.get(RunLog, run_id)