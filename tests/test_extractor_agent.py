"""Extractor agent tests: pure parsing, no network, no browser."""
from pathlib import Path

from app.agents.extractor_agent import ExtractorAgent

FIXTURE = Path(__file__).parent / "fixtures" / "sample_cause_list.html"


def test_extracts_all_rows():
    html = FIXTURE.read_text()
    agent = ExtractorAgent()
    cases = agent.run(
        html, department="Social Welfare", cause_list_date="2026-07-21",
        source_url="https://aphc.gov.in",
    )
    assert len(cases) == 2
    assert cases[0].case_number == "WP/12345/2026"
    assert cases[0].pdf_url == "https://aphc.gov.in/docs/WP12345.pdf"
    assert cases[1].pdf_url is None


def test_skips_malformed_row_without_failing():
    html = "<table class='cause-list-table'><tbody><tr><td class='case-type'>No number</td></tr></tbody></table>"
    agent = ExtractorAgent()
    cases = agent.run(
        html, department="Social Welfare", cause_list_date="2026-07-21",
        source_url="https://aphc.gov.in",
    )
    assert cases == []