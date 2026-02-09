"""
Test suite for the-internet.herokuapp.com login page.
"""

import pytest
from pages.internet_page import InternetPage


class TestInternetLogin:
    """Test suite for login functionality on the-internet."""

    def test_successful_login(self, page):
        """Test successful login with valid credentials."""
        internet = InternetPage(page)
        internet.load()

        # Valid credentials for the demo site
        internet.login(username="tomsmith", password="SuperSecretPassword!")

        # Verify success message
        assert internet.is_success_message_visible()

        # Verify logout button is visible
        assert internet.is_logout_button_visible()

        print("✅ Login successful")

    def test_failed_login_wrong_password(self, page):
        """Test login failure with wrong password."""
        internet = InternetPage(page)
        internet.load()

        # Invalid credentials
        internet.login(username="tomsmith", password="WrongPassword")

        # Verify error message
        assert internet.is_error_message_visible()

        print("✅ Error message shown for wrong password")

    def test_failed_login_wrong_username(self, page):
        """Test login failure with wrong username."""
        internet = InternetPage(page)
        internet.load()

        # Invalid credentials
        internet.login(username="wronguser", password="SuperSecretPassword!")

        # Verify error message
        assert internet.is_error_message_visible()

        print("✅ Error message shown for wrong username")
