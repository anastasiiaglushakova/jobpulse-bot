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
        logger.info("📝 Тест: загрузка страницы")
        jobboard = JobBoardPage(page)
        jobboard.load()

        # Verify page title
        assert "JobBoard" in page.title()
        logger.info("✅ Страница загружена, заголовок проверен")

        # Verify search input is visible
        assert jobboard.search_input.is_visible()

        # Verify search button is visible
        assert jobboard.search_button.is_visible()
        logger.info("✅ Элементы поиска видны")

    @pytest.mark.e2e
    @pytest.mark.jobboard
    def test_search_python_jobs(self, page):
        """Test searching for Python jobs."""
        logger.info("📝 Тест: поиск вакансий 'Python'")
        jobboard = JobBoardPage(page)
        jobboard.load()

        # Search for "Python"
        jobboard.search_jobs("Python")

        # Verify results are displayed
        results_count = jobboard.get_results_count()
        logger.info(f"🔍 Найдено вакансий: {results_count}")
        assert results_count > 0, "Should have at least one Python job"

        # Verify job titles contain "Python"
        job_titles = jobboard.get_job_titles()
        assert any(
            "Python" in title for title in job_titles
        ), "At least one job should contain 'Python' in title"
        logger.info("✅ Поиск 'Python' работает корректно")

    @pytest.mark.e2e
    @pytest.mark.jobboard
    def test_search_qa_jobs(self, page):
        """Test searching for QA jobs."""
        logger.info("📝 Тест: поиск вакансий 'QA'")
        jobboard = JobBoardPage(page)
        jobboard.load()

        # Search for "QA"
        jobboard.search_jobs("QA")

        # Verify results are displayed
        results_count = jobboard.get_results_count()
        logger.info(f"🔍 Найдено вакансий: {results_count}")
        assert results_count > 0, "Should have at least one QA job"
        logger.info("✅ Поиск 'QA' работает корректно")

    @pytest.mark.e2e
    @pytest.mark.jobboard
    def test_search_no_results(self, page):
        """Test searching for non-existent job."""
        logger.info("📝 Тест: поиск несуществующей вакансии")
        jobboard = JobBoardPage(page)
        jobboard.load()

        # Search for something that doesn't exist
        jobboard.search_jobs("NonExistentJob123XYZ")

        # Verify no results
        results_count = jobboard.get_results_count()
        logger.info(f"🔍 Результатов: {results_count}")
        assert results_count == 0, "Should have no results"
        logger.info("✅ Пустой поиск работает корректно")

    @pytest.mark.e2e
    @pytest.mark.jobboard
    def test_job_card_structure(self, page):
        """Test that job cards have proper structure."""
        logger.info("📝 Тест: структура карточек вакансий")
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

        logger.info(f"✅ Проверено {len(jobs)} карточек, все поля присутствуют")

    @pytest.mark.e2e
    @pytest.mark.jobboard
    def test_sort_jobs(self, page):
        """Test sorting jobs by different criteria."""
        logger.info("📝 Тест: сортировка вакансий")
        jobboard = JobBoardPage(page)
        jobboard.load()

        # Сортировка по новизне
        jobboard.sort_by("newest")
        jobs_newest = jobboard.get_job_titles()
        logger.info(f"🔍 Сортировка 'новые': {jobs_newest[:3]}")

        # Сортировка по старизне
        jobboard.sort_by("oldest")
        jobs_oldest = jobboard.get_job_titles()
        logger.info(f"🔍 Сортировка 'старые': {jobs_oldest[:3]}")

        # Сортировка по названию
        jobboard.sort_by("title")
        jobs_title = jobboard.get_job_titles()
        logger.info(f"🔍 Сортировка 'по названию': {jobs_title[:3]}")

        # Проверяем, что сортировка изменила порядок
        assert (
            jobs_newest != jobs_oldest
        ), "Сортировка 'новые' и 'старые' должна давать разный порядок"
        assert len(jobs_newest) > 0, "Должны быть вакансии после сортировки"

        # Проверяем, что сортировка по названию упорядочена
        titles_sorted = sorted(jobs_title)
        assert (
            jobs_title == titles_sorted
        ), "Сортировка по названию должна быть алфавитной"

        logger.info("✅ Сортировка работает корректно")
