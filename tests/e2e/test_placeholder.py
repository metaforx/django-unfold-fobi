"""Placeholder Playwright test to verify the scaffold is usable.

Full browser tests will be added in T04.
"""
import pytest


@pytest.mark.skip(reason="Playwright browser tests deferred to T04")
def test_admin_login_loads(page, live_server):
    """Verify the admin login page loads in a real browser."""
    page.goto(f"{live_server.url}/admin/login/")
    assert "Log in" in page.content()
