"""
Page Object Model for JobBoard Demo site (stable version).
"""

import re
from playwright.sync_api import Page, TimeoutError


class JobBoardPage:
    """Page Object for JobBoard Demo."""

    URL = "https://anastasiiaglushakova.github.io/jobboard-demo/"

    def __init__(self, page: Page):
        self.page = page

        # Locators
        self.search_input = page.locator("#search-input")
        self.search_button = page.locator("#search-button")
        self.jobs_container = page.locator("#jobs-container")
        self.job_cards = page.locator(".job-card")
        self.results_count = page.locator("#results-count")
        self.sort_select = page.locator("#sort-select")

    def load(self):
        self.page.goto(self.URL)
        self.page.wait_for_load_state("domcontentloaded")
        self.jobs_container.wait_for(state="visible")

    def search_jobs(self, query: str):
        self.search_input.fill(query)
        self.search_button.click()

        self.results_count.wait_for(state="visible", timeout=5000)

        self.page.wait_for_timeout(300)

    def get_results_count(self) -> int:
        """
        Robust parsing of results count from UI text.
        Supports:
        - 'Results: 5'
        - '5 jobs found'
        - 'No jobs found'
        """
        text = self.results_count.inner_text()
        match = re.search(r"\d+", text)
        return int(match.group()) if match else 0

    def get_results_count_text(self) -> str:
        return self.results_count.inner_text()

    def has_jobs(self) -> bool:
        """Safe check if any job cards exist."""
        return self.job_cards.count() > 0

    def get_job_titles(self) -> list[str]:
        """Safe job titles getter (handles empty state)."""
        if self.job_cards.count() == 0:
            return []
        return self.page.locator(".job-title").all_inner_texts()

    def get_all_job_data(self) -> list[dict]:
        """Get all job cards data safely."""
        jobs = []

        count = self.job_cards.count()
        for i in range(count):
            card = self.job_cards.nth(i)

            jobs.append(
                {
                    "title": card.locator(".job-title").inner_text(),
                    "company": card.locator(".job-company").inner_text(),
                    "location": card.locator(".job-location").inner_text(),
                    "type": card.locator(".job-type").inner_text(),
                }
            )

        return jobs

    def is_job_card_visible(self, title: str) -> bool:
        try:
            self.page.locator(f".job-card:has-text('{title}')").wait_for(
                state="visible", timeout=2000
            )
            return True
        except TimeoutError:
            return False

    def sort_by(self, sort_option: str):
        self.sort_select.select_option(sort_option)

        self.page.wait_for_timeout(300)

    def get_job_dates(self) -> list[str]:
        if self.job_cards.count() == 0:
            return []
        return self.page.locator(".job-date").all_inner_texts()
