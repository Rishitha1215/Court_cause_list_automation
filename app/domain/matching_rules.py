"""
Business rules for advocate name matching.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher


class MatchingRules:
    """
    Provides reusable matching rules for advocate names.
    """

    MIN_SIMILARITY = 0.90

    @staticmethod
    def normalize(name: str) -> str:
        """
        Normalize an advocate name.

        Example:
            "Mr. A.B.C Rao"
            -> "ABC RAO"
        """

        if not name:
            return ""

        name = name.upper()

        # Remove common prefixes
        prefixes = [
            "MR",
            "MRS",
            "MS",
            "ADV",
            "ADVOCATE",
            "SRI",
            "SMT",
        ]

        words = []

        for word in re.split(r"\s+", name):
            clean = re.sub(r"[^A-Z0-9]", "", word)

            if clean in prefixes:
                continue

            if clean:
                words.append(clean)

        return " ".join(words)

    @classmethod
    def similarity(cls, first: str, second: str) -> float:
        """
        Return similarity score between two names.
        """

        first = cls.normalize(first)
        second = cls.normalize(second)

        return SequenceMatcher(None, first, second).ratio()

    @classmethod
    def is_match(cls, first: str, second: str) -> bool:
        """
        Return True if names are considered equal.
        """

        return cls.similarity(first, second) >= cls.MIN_SIMILARITY