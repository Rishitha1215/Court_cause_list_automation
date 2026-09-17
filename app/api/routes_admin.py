"""
Admin-facing endpoints (require an admin JWT).

GET  /admin/runs                  - recent scheduler/manual run history
GET  /admin/runs/{run_id}         - a single run's summary
POST /admin/runs/trigger          - manually trigger a full cycle immediately
GET  /admin/notifications/failed  - failed notifications for retry review
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.orchestrator_agent import OrchestratorAgent
from app.api.deps import require_admin
from app.database import get_db
from app.repositories.notification_repository import NotificationRepository
from app.repositories.run_repository import RunRepository
from app.schemas.notification_schema import NotificationOut
from app.schemas.run_schema import RunOut

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/runs", response_model=list[RunOut])
def list_runs(db: Session = Depends(get_db)):
    return RunRepository(db).list_recent()


@router.get("/runs/{run_id}", response_model=RunOut)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = RunRepository(db).get(run_id)
    if not run:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Run not found")
    return run


@router.post("/runs/trigger", status_code=status.HTTP_202_ACCEPTED)
def trigger_run(background_tasks: BackgroundTasks):
    background_tasks.add_task(OrchestratorAgent().run_full_cycle, "manual")
    return {"detail": "Run triggered"}


@router.get("/notifications/failed", response_model=list[NotificationOut])
def list_failed_notifications(db: Session = Depends(get_db)):
    return NotificationRepository(db).list_failed()