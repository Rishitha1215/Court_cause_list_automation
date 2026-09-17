"""
General case lookup and PDF download endpoints (any authenticated user).

GET /cases/{case_id}      - case details
GET /cases/{case_id}/pdf  - download the associated PDF, if one was stored
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.case import Case
from app.schemas.case_schema import CaseOut

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("/{case_id}", response_model=CaseOut)
def get_case(case_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Case not found")
    return case


@router.get("/{case_id}/pdf")
def download_case_pdf(case_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Case not found")
    if not case.downloaded_pdf_path:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No PDF stored for this case")
    return FileResponse(case.downloaded_pdf_path, filename=f"{case.case_number}.pdf")