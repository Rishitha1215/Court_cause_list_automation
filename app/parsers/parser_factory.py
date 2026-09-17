from .html_parser import HTMLParser
from .pdf_text_extractor import PDFTextExtractor


class ParserFactory:

    @staticmethod
    def html():
        return HTMLParser()

    @staticmethod
    def pdf():
        return PDFTextExtractor()