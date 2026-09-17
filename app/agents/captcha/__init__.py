"""CAPTCHA solver factory -- chooses an implementation based on config so
the rest of the app never imports a concrete solver class directly."""
from app.agents.captcha.base_solver import CaptchaSolver
from app.agents.captcha.ocr_solver import OCRCaptchaSolver
from app.config import settings


def get_captcha_solver() -> CaptchaSolver:
    if settings.captcha_solver == "ocr":
        return OCRCaptchaSolver()
    raise ValueError(f"Unknown CAPTCHA_SOLVER '{settings.captcha_solver}'")