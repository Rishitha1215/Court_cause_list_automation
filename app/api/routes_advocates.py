"""
Advocate-facing endpoints (require an advocate JWT via Authorization: Bearer <token>).

GET  /advocates/me                - profile
PUT  /advocates/me                - update notification preferences
GET  /advocates/me/cases          - cases matched to this advocate
GET  /advocates/me/notifications  - notification history
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_advocate
from app.database import get_db
from app.models.advocate import Advocate
from app.repositories.advocate_repository import AdvocateRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.notification_repository import NotificationRepository
from app.schemas.advocate_schema import AdvocateOut, AdvocateUpdate
from app.schemas.case_schema import CaseOut
from app.schemas.notification_schema import NotificationOut

router = APIRouter(prefix="/advocates", tags=["advocates"])


@router.get("/me", response_model=AdvocateOut)
def read_profile(advocate: Advocate = Depends(get_current_advocate)):
    return advocate


@router.put("/me", response_model=AdvocateOut)
def update_profile(data: AdvocateUpdate, advocate: Advocate = Depends(get_current_advocate),
                    db: Session = Depends(get_db)):
    updated = AdvocateRepository(db).update(advocate, **data.model_dump(exclude_unset=True))
    db.commit()
    return updated


@router.get("/me/cases", response_model=list[CaseOut])
def list_my_cases(advocate: Advocate = Depends(get_current_advocate), db: Session = Depends(get_db)):
    return CaseRepository(db).list_for_advocate(advocate.id)


@router.get("/me/notifications", response_model=list[NotificationOut])
def list_my_notifications(advocate: Advocate = Depends(get_current_advocate), db: Session = Depends(get_db)):
    return NotificationRepository(db).list_for_advocate(advocate.id)