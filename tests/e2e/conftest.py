"""Playwright browser test fixtures for unfold_fobi.

Handles the async/sync compatibility between Playwright and Django's ORM,
and provides login and form-entry helpers for e2e tests.
"""
import os

import pytest

# Playwright runs an async event loop; Django blocks DB calls from async
# contexts by default. Allow it for the e2e test process.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture()
def admin_login(page, live_server, admin_user):
    """Log in as admin via the Django admin login page."""
    # With i18n_patterns the admin lives under /en/admin/.
    login_url = f"{live_server.url}/en/admin/login/?next=/en/admin/"
    page.goto(login_url)
    page.fill("#id_username", "admin")
    page.fill("#id_password", "testpass123")
    page.click("[type=submit]")
    # Wait for the exact admin index URL to confirm authenticated redirect.
    page.wait_for_url(f"{live_server.url}/en/admin/", timeout=10000)
    return page
