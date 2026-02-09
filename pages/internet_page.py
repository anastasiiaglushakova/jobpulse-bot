"""
Page Object Model for the-internet.herokuapp.com login page.
"""

from playwright.sync_api import Page


class InternetPage:
    """Page Object for the-internet login page."""

    URL = "https://the-internet.herokuapp.com/login"

    def __init__(self, page: Page):
        self.page = page

        # Locators
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.login_button = page.locator("button[type='submit']")
        self.success_message = page.locator("#flash.success")
        self.error_message = page.locator("#flash.error")
        self.logout_button = page.locator("a[href='/logout']")

    def load(self):
        """Navigate to the login page."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")

    def login(self, username: str, password: str):
        """Perform login with given credentials."""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
        self.page.wait_for_load_state("networkidle")

    def is_success_message_visible(self) -> bool:
        """Check if success message is visible."""
        return self.success_message.is_visible()

    def is_error_message_visible(self) -> bool:
        """Check if error message is visible."""
        return self.error_message.is_visible()

    def is_logout_button_visible(self) -> bool:
        """Check if logout button is visible."""
        return self.logout_button.is_visible()

    def get_flash_message_text(self) -> str:
        """Get the text of flash message (success or error)."""
        flash = self.page.locator("#flash")
        return flash.inner_text() if flash.is_visible() else ""
