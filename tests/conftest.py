"""Shared pytest fixtures for unfold_fobi tests."""
import json

import pytest
from django.contrib.auth.models import User
from django.test import Client


@pytest.fixture()
def admin_user(db):
    """Create and return a superuser for admin access."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@test.local",
        password="testpass123",
    )


@pytest.fixture()
def admin_client(admin_user):
    """Return a Django test client logged in as the admin user."""
    client = Client()
    client.login(username="admin", password="testpass123")
    return client


@pytest.fixture()
def form_entry(db, admin_user):
    """Create a FormEntry with one element and one handler for builder tests."""
    from fobi.models import FormElementEntry, FormEntry, FormHandlerEntry

    entry = FormEntry.objects.create(
        user=admin_user,
        name="Test Form",
        slug="test-form",
        is_public=True,
        is_cloneable=True,
    )
    # Add a text input element
    FormElementEntry.objects.create(
        form_entry=entry,
        plugin_uid="text",
        plugin_data=json.dumps(
            {
                "label": "Full Name",
                "name": "full_name",
                "required": True,
                "placeholder": "Enter your name",
            }
        ),
        position=1,
    )
    # Add db_store handler
    FormHandlerEntry.objects.create(
        form_entry=entry,
        plugin_uid="db_store",
    )
    return entry
