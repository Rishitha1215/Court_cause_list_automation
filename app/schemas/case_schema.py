"""API schemas for the Case entity. CaseCreate also doubles as the data
contract passed from the Extractor Agent to the Matcher Agent."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CaseCreate(BaseModel):
    case_number: str
    case_type: Optional[str] = None
    cause_list_date: str  # YYYY-MM-DD
    court_hall: Optional[str] = None
    bench_judge: Optional[str] = None
    serial_number: Optional[str] = None
    petitioner: Optional[str] = None
    respondent: Optional[str] = None
    petitioner_advocate: Optional[str] = None
    respondent_advocate: Optional[str] = None
    department: Optional[str] = None
    listing_type: Optional[str] = None
    purpose: Optional[str] = None
    remarks: Optional[str] = None
    source_url: Optional[str] = None
    pdf_url: Optional[str] = None


class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_number: str
    case_type: Optional[str]
    cause_list_date: str
    court_hall: Optional[str]
    bench_judge: Optional[str]
    serial_number: Optional[str]
    petitioner: Optional[str]
    respondent: Optional[str]
    department: Optional[str]
    purpose: Optional[str]
    remarks: Optional[str]
    pdf_url: Optional[str]
    downloaded_pdf_path: Optional[str]
    retrieved_at: datetime