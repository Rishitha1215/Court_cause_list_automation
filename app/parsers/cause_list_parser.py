from __future__ import annotations

import re


class CauseListParser:
    """
    Converts extracted PDF text into
    structured case dictionaries.
    """

    CASE_PATTERN = re.compile(
        r"(?P<case_number>WP\s*\d+/\d+).*?(?P<advocate>[A-Za-z .]+)",
        re.IGNORECASE,
    )

    def parse_cases(self, text: str):

        cases = []

        for match in self.CASE_PATTERN.finditer(text):

            cases.append(
                {
                    "case_number": match.group("case_number").strip(),
                    "advocate_name": match.group("advocate").strip(),
                }
            )

        return cases