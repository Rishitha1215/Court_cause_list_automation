"""
Authentication endpoints.

POST /auth/register  - register a new advocate account
POST /auth/login      - obtain a JWT access token (body: email, password)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, DuplicateEntityError
from app.database import get_db
from app.schemas.advocate_schema import AdvocateCreate, AdvocateOut
from app.schemas.auth_schema import LoginRequest, Token
from app.services.auth_service import authenticate, register_advocate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AdvocateOut, status_code=status.HTTP_201_CREATED)
def register(data: AdvocateCreate, db: Session = Depends(get_db)):
    try:
        _user, advocate = register_advocate(db, data)
        return advocate
    except DuplicateEntityError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        token = authenticate(db, data.email, data.password)
        return Token(access_token=token)
    except AuthenticationError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc