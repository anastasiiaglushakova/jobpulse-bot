"""
Page Object Model for JobBoard Demo site.
"""

from playwright.sync_api import Page


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
        """Navigate to the page."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")

    def search_jobs(self, query: str):
        """Search for jobs by query."""
        self.search_input.fill(query)
        self.search_button.click()
        self.page.wait_for_timeout(500)  # Wait for results to update

    def get_results_count(self) -> int:
        """Get number of results displayed."""
        text = self.results_count.inner_text()
        # Extract number from "Результатов: X"
        try:
            return int(text.split(":")[1].strip())
        except (IndexError, ValueError):
            return 0

    def get_job_titles(self) -> list:
        """Get list of job titles from results."""
        job_cards = self.page.locator(".job-card")
        count = job_cards.count()
        titles = []

        for i in range(count):
            title = job_cards.nth(i).locator(".job-title").inner_text()
            titles.append(title)

        return titles

    def is_job_card_visible(self, title: str) -> bool:
        """Check if job card with specific title is visible."""
        try:
            self.page.locator(f".job-card:has-text('{title}')").wait_for(
                state="visible", timeout=2000
            )
            return True
        except:
            return False

    def get_all_job_data(self) -> list:
        """Get all job data from cards."""
        jobs = []
        job_cards = self.page.locator(".job-card")
        count = job_cards.count()

        for i in range(count):
            card = job_cards.nth(i)
            job = {
                "title": card.locator(".job-title").inner_text(),
                "company": card.locator(".job-company").inner_text(),
                "location": card.locator(".job-location").inner_text(),
                "type": card.locator(".job-type").inner_text(),
            }
            jobs.append(job)

        return jobs
