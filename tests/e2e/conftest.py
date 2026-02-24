"""Playwright browser test fixtures for unfold_fobi.

This scaffold provides the base configuration for T04 browser tests.
The live_server fixture from pytest-django is used with Playwright.
"""
import pytest


@pytest.fixture()
def admin_login(page, live_server, admin_user):
    """Log in as admin via the Django admin login page."""
    page.goto(f"{live_server.url}/admin/login/")
    page.fill("#id_username", "admin")
    page.fill("#id_password", "testpass123")
    page.click("[type=submit]")
    page.wait_for_url(f"{live_server.url}/admin/")
    return page
