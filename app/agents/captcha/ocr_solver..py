"""OCR-based CAPTCHA solver: simple image preprocessing (grayscale,
threshold) followed by Tesseract OCR. Good enough for simple, low-noise
CAPTCHAs -- swap for a different CaptchaSolver implementation if the
court site's CAPTCHA gets more complex."""
import io

import cv2
import numpy as np
import pytesseract
from PIL import Image

from app.agents.captcha.base_solver import CaptchaSolver
from app.core.exceptions import CaptchaSolveError


class OCRCaptchaSolver(CaptchaSolver):
    def solve(self, image_bytes: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("L")
            np_image = np.array(image)
            _, thresholded = cv2.threshold(np_image, 150, 255, cv2.THRESH_BINARY)
            text = pytesseract.image_to_string(
                thresholded,
                config="--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            )
            cleaned = "".join(text.split())
            if not cleaned:
                raise CaptchaSolveError("OCR produced empty result")
            return cleaned
        except CaptchaSolveError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise CaptchaSolveError(str(exc)) from exc