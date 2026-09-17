"""Abstract CAPTCHA solver interface. The Navigator agent depends only on
this interface, so the solving implementation can be swapped (a different
OCR engine, a paid solving service, an ML model) without touching
navigation code at all."""
from abc import ABC, abstractmethod


class CaptchaSolver(ABC):
    @abstractmethod
    def solve(self, image_bytes: bytes) -> str:
        """Returns the solved CAPTCHA text. Raises CaptchaSolveError on failure."""
        raise NotImplementedError