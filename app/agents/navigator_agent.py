"""
Navigator Agent.

Drives Playwright through the AP High Court portal.

CAPTCHA workflow:
1. Open AP High Court website.
2. Open Daily Cause List.
3. Open Advocate Wise search.
4. Enter advocate name.
5. Wait for CAPTCHA.
6. User manually enters CAPTCHA in the browser.
7. User manually submits the form.
8. Wait for the cause-list table.
9. Return the page HTML.

No CAPTCHA is emailed.
No CAPTCHA is solved automatically.
"""

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

from app.agents.base_agent import BaseAgent
from app.core.exceptions import NavigationError


class NavigatorAgent(BaseAgent):

    def __init__(self):
        super().__init__()

    def run(self, advocate_name: str) -> str:
        return self._navigate_and_fetch(advocate_name)

    def _navigate_and_fetch(self, advocate_name: str) -> str:

        try:
            with sync_playwright() as p:

                browser = p.chromium.launch(
                    headless=False,
                    slow_mo=500,
                )

                context = browser.new_context(
                    viewport={
                        "width": 1366,
                        "height": 768,
                    }
                )

                page = context.new_page()

                try:

                    # -------------------------------------------------
                    # STEP 1: OPEN AP HIGH COURT
                    # -------------------------------------------------

                    print("=" * 60)
                    print("Opening AP High Court...")
                    print("=" * 60)

                    page.goto(
                        "https://aphc.gov.in/Hcdbs/search.jsp",
                        wait_until="networkidle",
                        timeout=60000,
                    )

                    # -------------------------------------------------
                    # STEP 2: DAILY CAUSE LIST
                    # -------------------------------------------------

                    print("=" * 60)
                    print("Opening Daily Cause List...")
                    print("=" * 60)

                    page.wait_for_selector(
                        "button:has-text('DAILY CAUSE LIST')",
                        timeout=60000,
                    )

                    page.locator(
                        "button:has-text('DAILY CAUSE LIST')"
                    ).click()

                    page.wait_for_url(
                        "**/searchdates.action",
                        timeout=60000,
                    )

                    page.wait_for_load_state("networkidle")

                    # -------------------------------------------------
                    # STEP 3: ADVOCATE WISE
                    # -------------------------------------------------

                    print("=" * 60)
                    print("Opening Advocate Wise...")
                    print("=" * 60)

                    page.wait_for_selector(
                        "button:has-text('ADVOCATE WISE')",
                        timeout=60000,
                    )

                    page.locator(
                        "button:has-text('ADVOCATE WISE')"
                    ).click()

                    page.wait_for_url(
                        "**/searchtypeinput.action",
                        timeout=60000,
                    )

                    page.wait_for_load_state("networkidle")

                    # -------------------------------------------------
                    # STEP 4: ENTER ADVOCATE NAME
                    # -------------------------------------------------

                    print("=" * 60)
                    print(f"Entering advocate: {advocate_name}")
                    print("=" * 60)

                    page.wait_for_selector(
                        "#svalue",
                        timeout=60000,
                    )

                    page.fill(
                        "#svalue",
                        advocate_name,
                    )

                    # -------------------------------------------------
                    # STEP 5: WAIT FOR CAPTCHA
                    # -------------------------------------------------

                    page.wait_for_selector(
                        "#capImg",
                        state="visible",
                        timeout=60000,
                    )

                    print()
                    print("=" * 60)
                    print("CAPTCHA DETECTED")
                    print("=" * 60)
                    print()
                    print("Please enter the CAPTCHA manually")
                    print("in the AP High Court browser window.")
                    print()
                    print("After entering the CAPTCHA,")
                    print("click the Submit/Search button manually.")
                    print()
                    print("The program is waiting for the")
                    print("cause-list results...")
                    print()
                    print("=" * 60)

                    # -------------------------------------------------
                    # STEP 6: WAIT FOR RESULT TABLE
                    # -------------------------------------------------

                    page.wait_for_selector(
                        "#clisttable",
                        state="visible",
                        timeout=300000,
                    )

                    page.wait_for_timeout(1000)

                    print()
                    print("=" * 60)
                    print("CAUSE-LIST RESULT LOADED")
                    print("=" * 60)

                    # -------------------------------------------------
                    # STEP 7: BASIC VALIDATION
                    # -------------------------------------------------

                    rows = page.locator(
                        "#clisttable tbody tr"
                    )

                    total_rows = rows.count()

                    print(
                        f"Total table rows detected: {total_rows}"
                    )

                    if total_rows == 0:
                        raise NavigationError(
                            "Cause-list table loaded, "
                            "but no rows were found."
                        )

                    # -------------------------------------------------
                    # STEP 8: RETURN HTML
                    # -------------------------------------------------

                    html = page.content()

                    return html

                finally:
                    browser.close()

        except PlaywrightTimeoutError as exc:

            raise NavigationError(
                "Timed out while navigating for "
                f"advocate_name={advocate_name}: {exc}"
            ) from exc

        except NavigationError:
            raise

        except Exception as exc:

            raise NavigationError(
                "Unexpected navigation failure for "
                f"advocate_name={advocate_name}: {exc}"
            ) from exc