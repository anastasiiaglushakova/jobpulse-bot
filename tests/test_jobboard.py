"""
End-to-end tests for JobBoard Demo site.
"""

import pytest
from pages.jobboard_page import JobBoardPage
from utils.logger import logger


class TestJobBoardDemo:
    """Test suite for JobBoard Demo site."""

    @pytest.mark.smoke
    @pytest.mark.e2e
    @pytest.mark.jobboard
    def test_page_loads(self, page):
        """Test that the page loads successfully."""
        logger.info("📝 Test: page load")
        jobboard = JobBoardPage(page)
        jobboard.load()

        # Verify page title
        assert "JobBoard" in page.title()
        logger.info("✅ Page loaded, title verified")

        # Verify search input is visible
        assert jobboard.search_input.is_visible()

        # Verify search button is visible
        assert jobboard.search_button.is_visible()
        logger.info("✅ Search elements are visible")

    @pytest.mark.e2e
    @pytest.mark.jobboard
    def test_search_python_jobs(self, page):
        """Test searching for Python jobs."""
        logger.info("📝 Test: search for 'Python' jobs")
        jobboard = JobBoardPage(page)
        jobboard.load()

        # Search for "Python"
        jobboard.search_jobs("Python")

        # Verify results are displayed
        results_count = jobboard.get_results_count()
        logger.info(f"🔍 Found {results_count} jobs")
        assert results_count > 0, "Should have at least one Python job"

        # Verify job titles contain "Python"
        job_titles = jobboard.get_job_titles()
        assert any(
            "Python" in title for title in job_titles
        ), "At least one job should contain 'Python' in title"
        logger.info("✅ Search for 'Python' works correctly")

    @pytest.mark.e2e
    @pytest.mark.jobboard
    def test_search_qa_jobs(self, page):
        """Test searching for QA jobs."""
        logger.info("📝 Test: search for 'QA' jobs")
        jobboard = JobBoardPage(page)
        jobboard.load()

        # Search for "QA"
        jobboard.search_jobs("QA")

        # Verify results are displayed
        results_count = jobboard.get_results_count()
        logger.info(f"🔍 Found {results_count} jobs")
        assert results_count > 0, "Should have at least one QA job"
        logger.info("✅ Search for 'QA' works correctly")

    @pytest.mark.e2e
    @pytest.mark.jobboard
    def test_search_no_results(self, page):
        """Test searching for non-existent job."""
        logger.info("📝 Test: search for non-existent job")
        jobboard = JobBoardPage(page)
        jobboard.load()

        # Search for something that doesn't exist
        jobboard.search_jobs("NonExistentJob123XYZ")

        # Verify no results
        results_count = jobboard.get_results_count()
        logger.info(f"🔍 Results: {results_count}")
        assert results_count == 0, "Should have no results"
        logger.info("✅ Empty search works correctly")

    @pytest.mark.e2e
    @pytest.mark.jobboard
    def test_job_card_structure(self, page):
        """Test that job cards have proper structure."""
        logger.info("📝 Test: job card structure")
        jobboard = JobBoardPage(page)
        jobboard.load()

        # Search for Python jobs
        jobboard.search_jobs("Python")

        # Get job data
        jobs = jobboard.get_all_job_data()

        # Verify at least one job exists
        assert len(jobs) > 0

        # Verify each job has required fields
        for job in jobs:
            assert "title" in job
            assert "company" in job
            assert "location" in job
            assert "type" in job

        logger.info(f"✅ Verified {len(jobs)} cards, all fields present")

    @pytest.mark.e2e
    @pytest.mark.jobboard
    def test_sort_jobs(self, page):
        """Test sorting jobs by different criteria."""
        logger.info("📝 Test: job sorting")
        jobboard = JobBoardPage(page)
        jobboard.load()

        # Sort by newest
        jobboard.sort_by("newest")
        jobs_newest = jobboard.get_job_titles()
        logger.info(f"🔍 'newest' sort: {jobs_newest[:3]}")

        # Sort by oldest
        jobboard.sort_by("oldest")
        jobs_oldest = jobboard.get_job_titles()
        logger.info(f"🔍 'oldest' sort: {jobs_oldest[:3]}")

        # Sort by title
        jobboard.sort_by("title")
        jobs_title = jobboard.get_job_titles()
        logger.info(f"🔍 'title' sort: {jobs_title[:3]}")

        # Verify that sorting changed the order
        assert (
            jobs_newest != jobs_oldest
        ), "'newest' and 'oldest' sorting should produce different order"
        assert len(jobs_newest) > 0, "Should have jobs after sorting"

        # Verify that title sorting is alphabetical
        titles_sorted = sorted(jobs_title)
        assert jobs_title == titles_sorted, "Title sorting should be alphabetical"

        logger.info("✅ Sorting works correctly")
