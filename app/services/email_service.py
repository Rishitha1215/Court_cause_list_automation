"""Composes and sends the case notification email over SMTP."""
import smtplib
from email.message import EmailMessage

from app.config import settings
from app.core.exceptions import NotificationDeliveryError
from app.models.advocate import Advocate
from app.models.case import Case
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _build_message(advocate: Advocate, case: Case) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = f"New Case Listed: {case.case_number} on {case.cause_list_date}"
    msg["From"] = settings.smtp_from_address
    msg["To"] = advocate.user.email

    if case.downloaded_pdf_path:
        pdf_line = "Case document attached."
    elif case.pdf_url:
        pdf_line = f"Case document: {case.pdf_url}"
    else:
        pdf_line = "No case document available."

    body = f"""Dear {advocate.full_name},

A case in which you are listed has appeared on the Daily Cause List.

Cause List Date : {case.cause_list_date}
Case Number      : {case.case_number}
Court Hall       : {case.court_hall or 'N/A'}
Bench / Judge    : {case.bench_judge or 'N/A'}
Serial Number    : {case.serial_number or 'N/A'}
Petitioner       : {case.petitioner or 'N/A'}
Respondent       : {case.respondent or 'N/A'}
Purpose          : {case.purpose or 'N/A'}
Remarks          : {case.remarks or 'N/A'}

{pdf_line}

View full details on your dashboard.

-- Court Cause List Agent
"""
    msg.set_content(body)

    if case.downloaded_pdf_path:
        try:
            with open(case.downloaded_pdf_path, "rb") as f:
                msg.add_attachment(
                    f.read(), maintype="application", subtype="pdf",
                    filename=f"{case.case_number}.pdf",
                )
        except OSError as exc:
            logger.warning("Could not attach PDF for case %s: %s", case.case_number, exc)

    return msg


def send_case_notification(advocate: Advocate, case: Case) -> None:
    """Raises NotificationDeliveryError on failure; caller decides retry policy."""
    message = _build_message(advocate, case)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_username:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
        logger.info("Sent notification for case %s to %s", case.case_number, advocate.user.email)
    except Exception as exc:  # noqa: BLE001
        raise NotificationDeliveryError(str(exc)) from exc