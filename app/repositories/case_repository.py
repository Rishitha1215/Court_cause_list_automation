"""Data access for Case records, including advocate-link management."""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.case import Case, CaseAdvocateLink
from app.schemas.case_schema import CaseCreate


class CaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_number_and_date(self, case_number: str, cause_list_date: str) -> Optional[Case]:
        return (
            self.db.query(Case)
            .filter(Case.case_number == case_number, Case.cause_list_date == cause_list_date)
            .first()
        )

    def get_or_create(self, data: CaseCreate) -> tuple[Case, bool]:
        """Returns (case, created). Upserts on (case_number, cause_list_date)."""
        existing = self.get_by_number_and_date(data.case_number, data.cause_list_date)
        if existing:
            return existing, False
        case = Case(**data.model_dump())
        self.db.add(case)
        self.db.flush()
        return case, True

    def link_advocate(self, case_id: int, advocate_id: int, role: str) -> Optional[CaseAdvocateLink]:
        existing = (
            self.db.query(CaseAdvocateLink)
            .filter(CaseAdvocateLink.case_id == case_id, CaseAdvocateLink.advocate_id == advocate_id)
            .first()
        )
        if existing:
            return None
        link = CaseAdvocateLink(case_id=case_id, advocate_id=advocate_id, role=role)
        self.db.add(link)
        self.db.flush()
        return link

    def set_pdf_downloaded_path(self, case: Case, path: str) -> None:
        case.downloaded_pdf_path = path
        self.db.flush()

    def list_for_advocate(self, advocate_id: int, limit: int = 100) -> list[Case]:
        return (
            self.db.query(Case)
            .join(CaseAdvocateLink, CaseAdvocateLink.case_id == Case.id)
            .filter(CaseAdvocateLink.advocate_id == advocate_id)
            .order_by(Case.retrieved_at.desc())
            .limit(limit)
            .all()
        )