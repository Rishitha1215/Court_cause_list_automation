import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

from app.config import settings


class EmailAgent:

    def send_email(
        self,
        recipient_email: str,
        advocate_name: str,
        excel_file: Path,
        total_cases: int,
    ):

        if not recipient_email:
            raise ValueError(
                "Recipient email address is not configured."
            )

        excel_file = Path(excel_file)

        if not excel_file.exists():
            raise FileNotFoundError(
                f"Excel report not found: {excel_file}"
            )

        report_date = datetime.now().strftime(
            "%d %B %Y"
        )

        msg = EmailMessage()

        msg["Subject"] = (
            "AP High Court Cause List Report"
        )

        msg["From"] = settings.smtp_from_address

        msg["To"] = recipient_email

        msg.set_content(
            f"""Dear Sir/Madam,

Please find attached the AP High Court Cause List Report.

Report Date : {report_date}
Advocate / Department : {advocate_name}
Total Cases : {total_cases}

Regards,
Court Cause List Agent
"""
        )

        with open(
            excel_file,
            "rb",
        ) as f:

            file_data = f.read()

        msg.add_attachment(
            file_data,
            maintype="application",
            subtype=(
                "vnd.openxmlformats-officedocument"
                ".spreadsheetml.sheet"
            ),
            filename=excel_file.name,
        )

        self._send_message(msg)

        print(
            "Cause list email sent successfully."
        )

    def _send_message(
        self,
        msg: EmailMessage,
    ):

        if not settings.smtp_username:
            raise ValueError(
                "SMTP_USERNAME is not configured."
            )

        if not settings.smtp_password:
            raise ValueError(
                "SMTP_PASSWORD is not configured."
            )

        # Gmail SSL - port 465
        if settings.smtp_use_ssl:

            with smtplib.SMTP_SSL(
                settings.smtp_host,
                settings.smtp_port,
                timeout=60,
            ) as smtp:

                smtp.login(
                    settings.smtp_username,
                    settings.smtp_password,
                )

                smtp.send_message(msg)

        else:

            with smtplib.SMTP(
                settings.smtp_host,
                settings.smtp_port,
                timeout=60,
            ) as smtp:

                if settings.smtp_use_tls:

                    smtp.starttls()

                smtp.login(
                    settings.smtp_username,
                    settings.smtp_password,
                )

                smtp.send_message(msg)