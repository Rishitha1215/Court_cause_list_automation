"""Downloads and stores PDFs associated with cases, with a safe fallback
to storing just the URL if the download fails."""
import os
import re
from typing import Optional

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _safe_filename(case_number: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "_", case_number)
    return f"{cleaned}.pdf"


def download_pdf(pdf_url: str, case_number: str) -> Optional[str]:
    """
    Attempts to download `pdf_url` into PDF_STORAGE_DIR.
    Returns the local file path on success, or None on failure
    (caller should fall back to storing the URL only).
    """
    os.makedirs(settings.pdf_storage_dir, exist_ok=True)
    destination = os.path.join(settings.pdf_storage_dir, _safe_filename(case_number))

    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(pdf_url)
            response.raise_for_status()
            with open(destination, "wb") as f:
                f.write(response.content)
        logger.info("Downloaded PDF for case %s to %s", case_number, destination)
        return destination
    except Exception as exc:  # noqa: BLE001 - deliberately broad, this is a best-effort download
        logger.warning("PDF download failed for case %s (%s); storing URL only", case_number, exc)
        return None