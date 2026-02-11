"""
Pytest configuration and fixtures for JobPulse project.
"""

import pytest
from playwright.sync_api import sync_playwright, Browser, Page
import os
import shutil
import time


@pytest.fixture(scope="session")
def browser_context_args():
    """Configure browser context."""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "locale": "ru-RU",
    }


@pytest.fixture(scope="session")
def browser(browser_context_args):
    """Create browser instance."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        yield browser
        browser.close()


@pytest.fixture
def page(browser, browser_context_args, request):
    """Create new page for each test with screenshot on failure."""
    # Очищаем папку скриншотов перед тестами
    if not hasattr(request.session, "_screenshots_cleared"):
        shutil.rmtree("screenshots", ignore_errors=True)
        os.makedirs("screenshots", exist_ok=True)
        request.session._screenshots_cleared = True

    context = browser.new_context(**browser_context_args)
    page = context.new_page()
    yield page

    # Делаем скриншот при падении
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        screenshot_name = f"{request.node.name}_{int(time.time())}.png"
        screenshot_path = os.path.join("screenshots", screenshot_name)
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n📸 Скриншот сохранён: {screenshot_path}")

    page.close()
    context.close()


@pytest.fixture(scope="session")
def jobboard_url():
    """URL of the demo job board."""
    return os.getenv(
        "JOBSITE_URL", "https://anastasiiaglushakova.github.io/jobboard-demo/"
    )


@pytest.fixture(scope="session")
def telegram_bot_token():
    """Telegram bot token."""
    return os.getenv("TELEGRAM_BOT_TOKEN", "")


# Импортируем кастомные хуки для отчётов
from utils.conftest_hooks import (
    pytest_runtest_protocol,
    pytest_runtest_makereport,
    pytest_sessionfinish,
)
