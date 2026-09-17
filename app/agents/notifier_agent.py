"""
Notifier Agent.

Generates one Excel cause-list report and sends it
as a single email.

This agent does NOT:
- send CAPTCHA emails
- solve CAPTCHA
- send individual case emails
"""

from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.agents.email_agent import EmailAgent
from app.agents.excel_agent import ExcelAgent


class NotifierAgent(BaseAgent):

    def __init__(self):
        super().__init__()

        self.excel_agent = ExcelAgent()
        self.email_agent = EmailAgent()

    def run(
        self,
        cases: list,
        advocate_name: str,
        recipient_email: str,
    ) -> Path | None:

        # -------------------------------------------------
        # NO CASES
        # -------------------------------------------------

        if not cases:

            print(
                "No cases found. "
                "Excel report will not be generated."
            )

            return None

        # -------------------------------------------------
        # CHECK EMAIL
        # -------------------------------------------------

        if not recipient_email:

            raise ValueError(
                "Recipient email address is required."
            )

        # -------------------------------------------------
        # GENERATE EXCEL
        # -------------------------------------------------

        print()
        print("=" * 60)
        print("Generating Excel report...")
        print("=" * 60)

        excel_file = (
            self.excel_agent.generate_report(
                cases=cases,
                advocate_name=advocate_name,
            )
        )

        if not excel_file:

            raise RuntimeError(
                "Excel report could not be generated."
            )

        print(
            f"Excel report created: {excel_file}"
        )

        # -------------------------------------------------
        # SEND EMAIL
        # -------------------------------------------------

        print()
        print("=" * 60)
        print("Sending Excel report by email...")
        print("=" * 60)

        self.email_agent.send_email(
            recipient_email=recipient_email,
            advocate_name=advocate_name,
            excel_file=excel_file,
            total_cases=len(cases),
        )

        print(
            "Excel report email sent successfully."
        )

        return excel_file