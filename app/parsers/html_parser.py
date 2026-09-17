from __future__ import annotations

from bs4 import BeautifulSoup

from .base_parser import BaseParser


class HTMLParser(BaseParser):
    """
    Parses downloaded HTML pages.
    """

    def parse(self, html: str):

        soup = BeautifulSoup(html, "html.parser")

        return soup