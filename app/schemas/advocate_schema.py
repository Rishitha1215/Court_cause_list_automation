"""API schemas for the Advocate profile entity."""
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class AdvocateCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    bar_council_number: Optional[str] = None
    department: Optional[str] = None


class AdvocateUpdate(BaseModel):
    phone: Optional[str] = None
    department: Optional[str] = None
    notify_by_email: Optional[bool] = None


class AdvocateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    phone: Optional[str]
    bar_council_number: Optional[str]
    department: Optional[str]
    notify_by_email: bool
    is_active: bool