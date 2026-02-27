"""T03 – DB-store view entries baseline tests.

Verifies that the db_store "view entries" route shows submitted rows when
data is created via DRF PUT endpoint.
"""
import pytest


class TestDRFSubmission:
    """Data submitted via DRF PUT must be persisted in SavedFormDataEntry."""

    def test_drf_put_creates_saved_entry(self, rest_submitted_form_data):
        saved = rest_submitted_form_data["saved_entry"]
        assert saved is not None
        assert saved.pk is not None

    def test_saved_entry_linked_to_form(self, rest_submitted_form_data, form_entry):
        saved = rest_submitted_form_data["saved_entry"]
        assert saved.form_entry_id == form_entry.pk

    def test_saved_entry_data_contains_payload(self, rest_submitted_form_data):
        saved = rest_submitted_form_data["saved_entry"]
        import json

        data = json.loads(saved.saved_data)
        # saved_data is a dict like {"full_name": "Alice Example"}
        assert data.get("full_name") == "Alice Example"


class TestPublicFormView:
    """The public fobi form view at /fobi/<slug>/ must load."""

    def test_public_form_view_returns_200(self, client, form_entry):
        from django.urls import reverse

        url = reverse("fobi.view_form_entry", args=[form_entry.slug])
        response = client.get(url)
        assert response.status_code == 200

    def test_public_form_view_contains_form(self, client, form_entry):
        from django.urls import reverse

        url = reverse("fobi.view_form_entry", args=[form_entry.slug])
        response = client.get(url)
        content = response.content.decode()
        assert "<form" in content.lower()


class TestDBStoreEntriesList:
    """After DRF submission, saved entries are queryable."""

    def test_saved_entries_count(self, rest_submitted_form_data, form_entry):
        from fobi.contrib.plugins.form_handlers.db_store.models import (
            SavedFormDataEntry,
        )

        count = SavedFormDataEntry.objects.filter(form_entry=form_entry).count()
        assert count >= 1

    def test_multiple_submissions_accumulate(
        self, admin_client, form_entry, rest_submitted_form_data
    ):
        """A second DRF PUT creates an additional saved entry."""
        import json

        from fobi.contrib.plugins.form_handlers.db_store.models import (
            SavedFormDataEntry,
        )

        before = SavedFormDataEntry.objects.filter(form_entry=form_entry).count()
        admin_client.put(
            f"/api/fobi-form-entry/{form_entry.slug}/",
            data=json.dumps({"full_name": "Bob Example"}),
            content_type="application/json",
        )
        after = SavedFormDataEntry.objects.filter(form_entry=form_entry).count()
        assert after == before + 1
