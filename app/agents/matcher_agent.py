"""
Matcher Agent.

Persists extracted cases, matches them against registered advocates,
and filters out anything already notified.

This agent does NOT:
- navigate the court website
- solve CAPTCHA
- send email
- download case PDFs
"""

from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.repositories.advocate_repository import AdvocateRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.notification_repository import NotificationRepository
from app.schemas.case_schema import CaseCreate


class MatcherAgent(BaseAgent):

    def __init__(self, db: Session):
        super().__init__()

        self.db = db
        self.case_repo = CaseRepository(db)
        self.advocate_repo = AdvocateRepository(db)
        self.notification_repo = NotificationRepository(db)

    def run(
        self,
        extracted_cases: list,
        department: str,
    ) -> list[tuple]:

        """
        Accept dictionaries returned by ExtractorAgent,
        convert them to CaseCreate objects, persist them,
        and match them against registered advocates.

        Returns:
            list of (case, advocate) tuples
        """

        registered = self.advocate_repo.list_active(
            department=department
        )

        if not registered:
            registered = self.advocate_repo.list_active()

        new_matches: list[tuple] = []

        for data in extracted_cases:

            # --------------------------------------------------
            # Convert Extractor dictionary to CaseCreate
            # --------------------------------------------------

            case_data = CaseCreate(
                case_number=data.get("case_details", ""),
                case_type=data.get("case_type"),
                cause_list_date=data.get(
                    "cause_list_date",
                    "",
                ),
                court_hall=data.get("court_no"),
                bench_judge=data.get("judge"),
                serial_number=data.get("sno"),
                petitioner=data.get("party"),
                petitioner_advocate=data.get("pet_adv"),
                respondent=data.get("respondent"),
                respondent_advocate=data.get("res_adv"),
                department=data.get(
                    "department",
                    department,
                ),
                listing_type=data.get("stage"),
                purpose=data.get("purpose"),
                remarks=data.get("ia_details"),
                source_url=data.get("source_url"),
                pdf_url=None,
            )

            # --------------------------------------------------
            # Save or retrieve case
            # --------------------------------------------------

            case, created = self.case_repo.get_or_create(
                case_data
            )

            # --------------------------------------------------
            # Match against registered advocates
            # --------------------------------------------------

            for advocate in registered:

                role = self._match_role(
                    case_data,
                    advocate.full_name,
                )

                if not role:
                    continue

                link = self.case_repo.link_advocate(
                    case.id,
                    advocate.id,
                    role,
                )

                if link is None:
                    continue

                if self.notification_repo.exists(
                    case.id,
                    advocate.id,
                ):
                    continue

                new_matches.append(
                    (case, advocate)
                )

        self.db.commit()

        return new_matches

    @staticmethod
    def _match_role(
        data: CaseCreate,
        advocate_name: str,
    ):

        name_lower = advocate_name.strip().lower()

        if (
            data.petitioner_advocate
            and name_lower in data.petitioner_advocate.lower()
        ):
            return "petitioner"

        if (
            data.respondent_advocate
            and name_lower in data.respondent_advocate.lower()
        ):
            return "respondent"

        return None