"""
Business validation rules.
"""

from __future__ import annotations


class ValidationRules:
    """
    Validate extracted case information.
    """

    REQUIRED_FIELDS = (
        "case_number",
        "advocate_name",
        "court_hall",
    )

    @classmethod
    def validate_case(cls, data: dict) -> bool:
        """
        Returns True if the extracted case
        contains all required information.
        """

        for field in cls.REQUIRED_FIELDS:
            value = data.get(field)

            if value is None:
                return False

            if str(value).strip() == "":
                return False

        return True