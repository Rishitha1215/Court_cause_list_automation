"""
Business rules for duplicate detection.
"""

from __future__ import annotations

import hashlib


class DuplicateRules:
    """
    Utility methods for duplicate checking.
    """

    @staticmethod
    def build_case_key(
        case_number: str,
        advocate_name: str,
        hearing_date: str,
    ) -> str:
        """
        Build a unique fingerprint for a case.
        """

        raw = (
            f"{case_number}|"
            f"{advocate_name.upper()}|"
            f"{hearing_date}"
        )

        return hashlib.sha256(raw.encode()).hexdigest()