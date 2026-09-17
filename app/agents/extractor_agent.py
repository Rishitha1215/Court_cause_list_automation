"""
Extractor Agent.

Extracts cause-list case information from the HTML returned
by NavigatorAgent.
"""

from datetime import datetime
from urllib.parse import quote
import re

from bs4 import BeautifulSoup

from app.agents.base_agent import BaseAgent


class ExtractorAgent(BaseAgent):

    def __init__(self):
        super().__init__()

    def run(
        self,
        html: str,
        department: str = "",
        cause_list_date: str = "",
        source_url: str = "",
    ) -> list:

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        table = soup.find(
            "table",
            id="clisttable",
        )

        if table is None:
            print("Cause-list table not found.")

            return []

        cases = []

        current_court = ""
        current_judge = ""
        current_date = cause_list_date
        current_time = ""
        current_stage = ""

        rows = table.find_all("tr")

        for row in rows:

            # -------------------------------------------------
            # HEADER / INFORMATION ROWS
            # -------------------------------------------------

            th = row.find("th")

            if th:

                text = " ".join(
                    th.stripped_strings
                )

                upper_text = text.upper()

                # COURT NUMBER
                if "COURT NO." in upper_text:

                    match = re.search(
                        r"COURT\s*NO\.?\s*(\d+)",
                        text,
                        re.IGNORECASE,
                    )

                    if match:
                        current_court = match.group(1)

                # JUDGE
                elif "HONOURABLE" in upper_text:

                    current_judge = text

                # DATE AND TIME
                elif "TO BE HEARD" in upper_text:

                    date_match = re.search(
                        r"(\d{1,2})"
                        r"(?:st|nd|rd|th)?"
                        r"\s+day\s+of\s+"
                        r"([A-Za-z]+)"
                        r"\s+(\d{4})",
                        text,
                        re.IGNORECASE,
                    )

                    if date_match:

                        day = date_match.group(1)
                        month = date_match.group(2)
                        year = date_match.group(3)

                        try:

                            dt = datetime.strptime(
                                f"{day} {month} {year}",
                                "%d %B %Y",
                            )

                            current_date = dt.strftime(
                                "%d %b %Y"
                            )

                        except ValueError:

                            current_date = (
                                f"{day} "
                                f"{month} "
                                f"{year}"
                            )

                    time_match = re.search(
                        r"AT\s*"
                        r"([0-9]{1,2}:[0-9]{2}"
                        r"\s*[AP]M)",
                        text,
                        re.IGNORECASE,
                    )

                    if time_match:

                        current_time = (
                            time_match.group(1)
                            .strip()
                        )

                # LIST / STAGE
                elif "LIST" in upper_text:

                    current_stage = text

                continue

            # -------------------------------------------------
            # CASE ROW
            # -------------------------------------------------

            cols = row.find_all("td")

            if len(cols) < 6:
                continue

            # -------------------------------------------------
            # CASE DETAILS
            # -------------------------------------------------

            case_lines = (
                cols[1]
                .get_text(
                    "\n",
                    strip=True,
                )
                .split("\n")
            )

            case_type = ""
            case_number = ""
            ia_details = ""
            purpose = ""

            if len(case_lines) > 0:

                first_line = case_lines[0].strip()

                if "/" in first_line:

                    parts = first_line.split(
                        "/",
                        1,
                    )

                    case_type = parts[0].strip()
                    case_number = parts[1].strip()

            if len(case_lines) > 1:

                ia_details = (
                    case_lines[1]
                    .strip()
                )

            if len(case_lines) > 2:

                purpose = "\n".join(
                    line.strip()
                    for line in case_lines[2:]
                    if line.strip()
                )

            # -------------------------------------------------
            # COMPLETE CASE NUMBER
            # -------------------------------------------------

            case_details = ""

            if case_type and case_number:

                case_details = (
                    f"{case_type}/{case_number}"
                )

            # -------------------------------------------------
            # CASE DETAILS LINK
            # -------------------------------------------------

            case_link = ""

            if case_details:

                case_link = (
                    "https://aphc.gov.in/Hcdbs/"
                    "caseDetails1.jsp?casedet="
                    + quote(
                        case_details,
                        safe="/",
                    )
                )

            # -------------------------------------------------
            # CASE OBJECT
            # -------------------------------------------------

            case = {

                "sno": cols[0].get_text(
                    strip=True
                ),

                "court_no": current_court,

                "judge": current_judge,

                "cause_list_date": current_date,

                "hearing_time": current_time,

                "stage": current_stage,

                "case_details": case_details,

                "case_link": case_link,

                "ia_details": ia_details,

                "purpose": purpose,

                "party": cols[2].get_text(
                    "\n",
                    strip=True,
                ),

                "pet_adv": cols[3].get_text(
                    "\n",
                    strip=True,
                ),

                "res_adv": cols[4].get_text(
                    "\n",
                    strip=True,
                ),

                "district": cols[5].get_text(
                    strip=True
                ),

                # Additional metadata
                "department": department,

                "source_url": source_url,
            }

            cases.append(case)

        print(
            f"Extractor found {len(cases)} cases."
        )

        return cases