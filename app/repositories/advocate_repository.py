"""Data access for Advocate profiles."""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.advocate import Advocate


class AdvocateRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, **fields) -> Advocate:
        advocate = Advocate(user_id=user_id, **fields)
        self.db.add(advocate)
        self.db.flush()
        return advocate

    def get_by_user_id(self, user_id: int) -> Optional[Advocate]:
        return self.db.query(Advocate).filter(Advocate.user_id == user_id).first()

    def get_by_id(self, advocate_id: int) -> Optional[Advocate]:
        return self.db.get(Advocate, advocate_id)

    def list_active(self, department: Optional[str] = None) -> list[Advocate]:
        query = self.db.query(Advocate).filter(Advocate.is_active.is_(True))
        if department:
            query = query.filter(Advocate.department == department)
        return query.all()

    def update(self, advocate: Advocate, **fields) -> Advocate:
        for key, value in fields.items():
            if value is not None:
                setattr(advocate, key, value)
        self.db.flush()
        return advocate