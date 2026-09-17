"""
Extract text from PDF bytes.

This parser works completely in memory without
saving the PDF to disk.
"""

from __future__ import annotations

from io import BytesIO

import pdfplumber

from .base_parser import BaseParser


class PDFTextExtractor(BaseParser):
    """
    Extract text from PDF bytes.
    """

    def parse(self, pdf_bytes: bytes) -> str:
        """
        Extract all text from a PDF represented
        as bytes.

        Args:
            pdf_bytes: Raw PDF content.

        Returns:
            Extracted text.
        """

        pages = []

        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:

            for page in pdf.pages:

                text = page.extract_text()

                if text:
                    pages.append(text)

        return "\n".join(pages)