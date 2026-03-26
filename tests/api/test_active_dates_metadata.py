"""T18: Active-date enforcement and form metadata in REST API."""

import json
from datetime import timedelta

import pytest
from django.utils import timezone
from fobi.models import FormElementEntry, FormEntry, FormHandlerEntry


@pytest.fixture()
def active_form(db, admin_user):
    """Public form with no date constraints (always active)."""
    entry = FormEntry.objects.create(
        user=admin_user,
        name="Active Form",
        slug="active-form",
        is_public=True,
        success_page_title="Thank you",
        success_page_message="Your submission has been received.",
    )
    FormElementEntry.objects.create(
        form_entry=entry,
        plugin_uid="text",
        plugin_data=json.dumps({"label": "Name", "name": "name", "required": True}),
        position=1,
    )
    FormHandlerEntry.objects.get_or_create(form_entry=entry, plugin_uid="db_store")
    return entry


@pytest.fixture()
def future_form(db, admin_user):
    """Public form that opens in the future."""
    entry = FormEntry.objects.create(
        user=admin_user,
        name="Future Form",
        slug="future-form",
        is_public=True,
        active_date_from=timezone.now() + timedelta(days=7),
    )
    FormElementEntry.objects.create(
        form_entry=entry,
        plugin_uid="text",
        plugin_data=json.dumps({"label": "Name", "name": "name", "required": True}),
        position=1,
    )
    FormHandlerEntry.objects.get_or_create(form_entry=entry, plugin_uid="db_store")
    return entry


@pytest.fixture()
def expired_form(db, admin_user):
    """Public form that closed in the past."""
    entry = FormEntry.objects.create(
        user=admin_user,
        name="Expired Form",
        slug="expired-form",
        is_public=True,
        active_date_from=timezone.now() - timedelta(days=30),
        active_date_to=timezone.now() - timedelta(days=1),
    )
    FormElementEntry.objects.create(
        form_entry=entry,
        plugin_uid="text",
        plugin_data=json.dumps({"label": "Name", "name": "name", "required": True}),
        position=1,
    )
    FormHandlerEntry.objects.get_or_create(form_entry=entry, plugin_uid="db_store")
    return entry


class TestGetFormFieldsMetadata:
    """GET /api/fobi-form-fields/{slug}/ returns metadata envelope."""

    def test_active_form_has_metadata_keys(self, admin_client, active_form):
        data = admin_client.get(f"/api/fobi-form-fields/{active_form.slug}/").json()
        assert data["is_active"] is True
        assert data["active_date_from"] is None
        assert data["active_date_to"] is None
        assert data["success_page_title"] == "Thank you"
        assert data["success_page_message"] == "Your submission has been received."

    def test_expired_form_returns_200_with_inactive_flag(self, admin_client, expired_form):
        response = admin_client.get(f"/api/fobi-form-fields/{expired_form.slug}/")
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert data["active_date_from"] is not None
        assert data["active_date_to"] is not None

    def test_future_form_returns_200_with_inactive_flag(self, admin_client, future_form):
        response = admin_client.get(f"/api/fobi-form-fields/{future_form.slug}/")
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert data["active_date_from"] is not None

    def test_empty_success_page_fields(self, admin_client, expired_form):
        data = admin_client.get(f"/api/fobi-form-fields/{expired_form.slug}/").json()
        assert data["success_page_title"] == ""
        assert data["success_page_message"] == ""


class TestPutActiveDateEnforcement:
    """PUT /api/fobi-form-entry/{slug}/ respects active dates."""

    def _put(self, client, slug, payload=None):
        return client.put(
            f"/api/fobi-form-entry/{slug}/",
            data=json.dumps(payload or {"name": "test"}),
            content_type="application/json",
        )

    def test_active_form_accepts_submission(self, admin_client, active_form):
        response = self._put(admin_client, active_form.slug)
        assert response.status_code == 200

    def test_no_dates_accepts_submission(self, admin_client, active_form):
        """Form with no active_date_from/to is always active."""
        assert active_form.active_date_from is None
        assert active_form.active_date_to is None
        response = self._put(admin_client, active_form.slug)
        assert response.status_code == 200

    def test_expired_form_returns_403(self, admin_client, expired_form):
        response = self._put(admin_client, expired_form.slug)
        assert response.status_code == 403
        assert "not currently accepting" in response.json()["detail"]

    def test_future_form_returns_403(self, admin_client, future_form):
        response = self._put(admin_client, future_form.slug)
        assert response.status_code == 403

    def test_form_within_window_accepts(self, db, admin_user, admin_client):
        """Form with active_date_from in past and active_date_to in future."""
        entry = FormEntry.objects.create(
            user=admin_user,
            name="Window Form",
            slug="window-form",
            is_public=True,
            active_date_from=timezone.now() - timedelta(days=1),
            active_date_to=timezone.now() + timedelta(days=1),
        )
        FormElementEntry.objects.create(
            form_entry=entry,
            plugin_uid="text",
            plugin_data=json.dumps({"label": "Name", "name": "name", "required": True}),
            position=1,
        )
        FormHandlerEntry.objects.get_or_create(form_entry=entry, plugin_uid="db_store")
        response = self._put(admin_client, entry.slug)
        assert response.status_code == 200
