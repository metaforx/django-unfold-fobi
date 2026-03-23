"""Shared admin-only fixtures."""

import pytest
from django.contrib.auth.models import User
from django.test import Client

from helpers import get_admin_edit_url


@pytest.fixture()
def change_html(admin_client, form_entry):
    """Render the change view HTML for the default form fixture."""
    response = admin_client.get(get_admin_edit_url(form_entry.pk))
    return response.content.decode()


@pytest.fixture()
def other_admin(db):
    """Secondary superuser for non-owner permission checks."""
    return User.objects.create_superuser(
        username="other_admin", email="other@test.local", password="pass"
    )


@pytest.fixture()
def other_admin_client(other_admin):
    """Client authenticated as a secondary superuser."""
    client = Client()
    client.login(username="other_admin", password="pass")
    return client
