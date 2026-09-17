from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseParser(ABC):
    """
    Abstract parser interface.

    Every parser must implement parse().
    """

    @abstractmethod
    def parse(self, source: Any):
        """
        Parse the source and return structured data.
        """
        raise NotImplementedError