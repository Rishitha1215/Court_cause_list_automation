"""Case model -- one row per case found on the daily cause list, plus the
many-to-many link that records which registered advocate(s) matched it."""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Text, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Case(Base):
    __tablename__ = "cases"
    __table_args__ = (
        UniqueConstraint("case_number", "cause_list_date", name="uq_case_number_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    case_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    case_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cause_list_date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    court_hall: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bench_judge: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    petitioner: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    respondent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    petitioner_advocate: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    respondent_advocate: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    listing_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    purpose: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    downloaded_pdf_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    advocate_links: Mapped[list["CaseAdvocateLink"]] = relationship(back_populates="case")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="case")


class CaseAdvocateLink(Base):
    """Records which registered advocate matched which case, and in what role."""
    __tablename__ = "case_advocate_links"
    __table_args__ = (
        UniqueConstraint("case_id", "advocate_id", name="uq_case_advocate"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), nullable=False)
    advocate_id: Mapped[int] = mapped_column(ForeignKey("advocates.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "petitioner" | "respondent"
    matched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    case: Mapped["Case"] = relationship(back_populates="advocate_links")
    advocate: Mapped["Advocate"] = relationship(back_populates="case_links")