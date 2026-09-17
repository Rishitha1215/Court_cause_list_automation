"""FastAPI dependencies: current user extraction and role guards."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.advocate import Advocate
from app.models.user import User, UserRole
from app.repositories.advocate_repository import AdvocateRepository
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    claims = decode_access_token(token)
    if not claims:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    user = UserRepository(db).get_by_email(claims["sub"])
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")
    return user


def get_current_advocate(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Advocate:
    if user.role != UserRole.ADVOCATE:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Advocate account required")
    advocate = AdvocateRepository(db).get_by_user_id(user.id)
    if not advocate:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Advocate profile not found")
    return advocate


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin privileges required")
    return user