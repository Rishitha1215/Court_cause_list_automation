"""
Orchestrator Agent.

Coordinates the complete AP High Court cause-list workflow.

Workflow:

Navigator
    -> Manual CAPTCHA
    -> Cause-list HTML

Extractor
    -> Extract case information

Matcher
    -> Match/store cases

Notifier
    -> Generate one Excel report
    -> Send Excel by email
"""

from datetime import date

from app.agents.extractor_agent import ExtractorAgent
from app.agents.logger_agent import LoggerAgent
from app.agents.matcher_agent import MatcherAgent
from app.agents.navigator_agent import NavigatorAgent
from app.agents.notifier_agent import NotifierAgent

from app.config import settings
from app.core.exceptions import AgentError
from app.database import session_scope
from app.models.run_log import RunStatus


class OrchestratorAgent:

    def __init__(self):

        self.navigator = NavigatorAgent()
        self.extractor = ExtractorAgent()
        self.notifier = NotifierAgent()

    def run_full_cycle(
        self,
        triggered_by: str = "scheduler",
    ):

        departments = settings.department_list

        cases_found = 0
        new_cases = 0
        notifications_sent = 0

        failures = []

        with session_scope() as db:

            logger = LoggerAgent(db)
            matcher = MatcherAgent(db)

            # -------------------------------------------------
            # START RUN
            # -------------------------------------------------

            run = logger.start_run(
                triggered_by,
                departments,
            )

            # -------------------------------------------------
            # PROCESS EACH ADVOCATE / DEPARTMENT
            # -------------------------------------------------

            for department in departments:

                try:

                    print()
                    print("=" * 70)
                    print(
                        f"PROCESSING: {department}"
                    )
                    print("=" * 70)

                    # -----------------------------------------
                    # NAVIGATOR
                    # -----------------------------------------

                    html = self.navigator.run(
                        department
                    )

                    logger.log_step(
                        run.id,
                        "navigator",
                        "run",
                        "success",
                        department,
                    )

                    # -----------------------------------------
                    # EXTRACTOR
                    # -----------------------------------------

                    cases = self.extractor.run(
                        html=html,
                        department=department,
                        cause_list_date=date.today().isoformat(),
                        source_url=settings.search_page_url,
                    )

                    cases_found += len(cases)

                    logger.log_step(
                        run.id,
                        "extractor",
                        "run",
                        "success",
                        department,
                    )

                    print(
                        f"Cases extracted: {len(cases)}"
                    )

                    # -----------------------------------------
                    # MATCHER
                    # -----------------------------------------

                    matches = matcher.run(
                        cases,
                        department,
                    )

                    new_cases += len(matches)

                    logger.log_step(
                        run.id,
                        "matcher",
                        "run",
                        "success",
                        department,
                    )

                    # -----------------------------------------
                    # REPORT + EMAIL
                    # -----------------------------------------

                    if cases:

                        recipient_email = (
                            settings.report_recipient_email
                        )

                        excel_file = (
                            self.notifier.run(
                                cases=cases,
                                advocate_name=department,
                                recipient_email=recipient_email,
                            )
                        )

                        if excel_file:

                            notifications_sent += 1

                            logger.log_step(
                                run.id,
                                "notifier",
                                "excel_email",
                                "success",
                                department,
                            )

                    else:

                        print(
                            "No cases found. "
                            "Skipping Excel/email."
                        )

                except AgentError as exc:

                    failures.append(
                        f"{department}: {exc}"
                    )

                    logger.log_step(
                        run.id,
                        "orchestrator",
                        "department",
                        "failed",
                        str(exc),
                    )

                except Exception as exc:

                    failures.append(
                        f"{department}: {exc}"
                    )

                    logger.log_step(
                        run.id,
                        "orchestrator",
                        "department",
                        "failed",
                        str(exc),
                    )

            # -------------------------------------------------
            # FINAL STATUS
            # -------------------------------------------------

            if failures:

                status = RunStatus.PARTIAL

            else:

                status = RunStatus.SUCCESS

            logger.finish_run(
                run,
                status,
                cases_found,
                new_cases,
                notifications_sent,
                "; ".join(failures)
                if failures
                else None,
            )

            return run