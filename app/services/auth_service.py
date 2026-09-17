"""Registration and login logic, combining security primitives with the
user/advocate repositories."""
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, DuplicateEntityError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import UserRole
from app.repositories.advocate_repository import AdvocateRepository
from app.repositories.user_repository import UserRepository
from app.schemas.advocate_schema import AdvocateCreate


def register_advocate(db: Session, data: AdvocateCreate):
    user_repo = UserRepository(db)
    advocate_repo = AdvocateRepository(db)

    if user_repo.get_by_email(data.email):
        raise DuplicateEntityError(f"A user with email {data.email} already exists")

    user = user_repo.create(
        email=data.email,
        hashed_password=hash_password(data.password),
        role=UserRole.ADVOCATE,
    )
    advocate = advocate_repo.create(
        user_id=user.id,
        full_name=data.full_name,
        phone=data.phone,
        bar_council_number=data.bar_council_number,
        department=data.department,
    )
    db.commit()
    return user, advocate


def authenticate(db: Session, email: str, password: str) -> str:
    """Returns a signed access token, or raises AuthenticationError."""
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(email)
    if not user or not user.is_active or not verify_password(password, user.hashed_password):
        raise AuthenticationError("Invalid email or password")
    return create_access_token(subject=user.email, extra_claims={"role": user.role.value, "uid": user.id})