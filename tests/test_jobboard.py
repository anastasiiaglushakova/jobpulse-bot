"""
End-to-end tests for JobBoard Demo site.
"""

import pytest
from pages.jobboard_page import JobBoardPage
from utils.logger import logger


@pytest.mark.jobboard
class TestJobBoardDemo:
    """Test suite for JobBoard Demo site."""

    @pytest.mark.smoke
    def test_page_loads(self, page):
        jobboard = JobBoardPage(page)

        jobboard.load()

        assert "JobBoard" in page.title()
        assert jobboard.search_input.is_visible()
        assert jobboard.search_button.is_visible()

        logger.info("Page loaded successfully")

    @pytest.mark.e2e
    @pytest.mark.parametrize("query", ["Python", "QA"])
    def test_search_jobs(self, page, query):
        jobboard = JobBoardPage(page)

        jobboard.load()
        jobboard.search_jobs(query)

        count = jobboard.get_results_count()
        assert count > 0

        titles = jobboard.get_job_titles()
        assert any(query in title for title in titles)

        logger.info(f"Search works for: {query}")

    @pytest.mark.e2e
    def test_search_no_results(self, page):
        jobboard = JobBoardPage(page)

        jobboard.load()
        jobboard.search_jobs("NonExistentJob123XYZ")

        count = jobboard.get_results_count()

        assert count == 0
        assert not jobboard.has_jobs()

        logger.info("No results handled correctly")

    @pytest.mark.e2e
    def test_job_card_structure(self, page):
        jobboard = JobBoardPage(page)

        jobboard.load()
        jobboard.search_jobs("Python")

        jobs = jobboard.get_all_job_data()

        assert len(jobs) > 0

        required_fields = {"title", "company", "location", "type"}

        for job in jobs:
            assert required_fields.issubset(job.keys())

        logger.info(f"Verified {len(jobs)} job cards structure")

    @pytest.mark.e2e
    def test_sort_jobs(self, page):
        jobboard = JobBoardPage(page)

        jobboard.load()

        jobboard.sort_by("newest")
        newest = jobboard.get_job_titles()

        jobboard.sort_by("oldest")
        oldest = jobboard.get_job_titles()

        jobboard.sort_by("title")
        titles = jobboard.get_job_titles()

        assert newest != oldest
        assert titles == sorted(titles)

        logger.info("Sorting works correctly")

    @pytest.mark.e2e
    @pytest.mark.parametrize("query", ["Python@#$%", "123456", ""])
    def test_search_edge_cases(self, page, query):
        jobboard = JobBoardPage(page)

        jobboard.load()
        jobboard.search_jobs(query)

        assert "JobBoard" in page.title()

        count = jobboard.get_results_count()

        if count == 0:
            assert not jobboard.has_jobs()
        else:
            assert jobboard.has_jobs()

        logger.info(f"Edge case handled: {query}")
