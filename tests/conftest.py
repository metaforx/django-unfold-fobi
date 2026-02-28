"""Shared pytest fixtures for unfold_fobi tests."""
import json
import sys

import pytest
from django.contrib.auth.models import User
from django.test import Client

# Prevent __pycache__ writes during test runs.
sys.dont_write_bytecode = True


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
    FormHandlerEntry.objects.get_or_create(
        form_entry=entry,
        plugin_uid="db_store",
    )
    return entry


@pytest.fixture()
def rest_submitted_form_data(admin_client, form_entry):
    """Create one saved form entry via DRF PUT endpoint used by the UI flow."""
    from fobi.contrib.plugins.form_handlers.db_store.models import (
        SavedFormDataEntry,
    )

    payload = {"full_name": "Alice Example"}
    response = admin_client.put(
        f"/api/fobi-form-entry/{form_entry.slug}/",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 200

    saved_entry = SavedFormDataEntry.objects.filter(
        form_entry=form_entry
    ).order_by("-pk").first()
    assert saved_entry is not None

    return {
        "payload": payload,
        "response": response,
        "saved_entry": saved_entry,
    }
