"""GET /api/fobi-form-fields/{slug}/ endpoint tests.

Covers response structure, field metadata, widget disambiguation, and error handling.
"""

import json

import pytest
from fobi.models import FormElementEntry, FormEntry, FormHandlerEntry


@pytest.fixture()
def multi_field_form(db, admin_user):
    """Form with text, textarea, and select elements for full endpoint coverage."""
    entry = FormEntry.objects.create(
        user=admin_user,
        name="Multi Field Form",
        slug="multi-field-form",
        is_public=True,
    )
    FormElementEntry.objects.create(
        form_entry=entry,
        plugin_uid="text",
        plugin_data=json.dumps(
            {"label": "Short Text", "name": "short_text", "required": True}
        ),
        position=1,
    )
    FormElementEntry.objects.create(
        form_entry=entry,
        plugin_uid="textarea",
        plugin_data=json.dumps(
            {"label": "Long Text", "name": "long_text", "required": False}
        ),
        position=2,
    )
    FormElementEntry.objects.create(
        form_entry=entry,
        plugin_uid="select",
        plugin_data=json.dumps(
            {
                "label": "Color",
                "name": "color",
                "required": False,
                "choices": "red\ngreen\nblue",
            }
        ),
        position=3,
    )
    FormHandlerEntry.objects.get_or_create(
        form_entry=entry, plugin_uid="db_store"
    )
    return entry


class TestFormFieldsResponseStructure:
    """Top-level response shape and envelope keys."""

    def test_returns_200(self, admin_client, multi_field_form):
        response = admin_client.get(f"/api/fobi-form-fields/{multi_field_form.slug}/")
        assert response.status_code == 200

    def test_envelope_keys(self, admin_client, multi_field_form):
        data = admin_client.get(f"/api/fobi-form-fields/{multi_field_form.slug}/").json()
        assert "id" in data
        assert "slug" in data
        assert "title" in data
        assert "fields" in data
        assert isinstance(data["fields"], list)

    def test_envelope_values(self, admin_client, multi_field_form):
        data = admin_client.get(f"/api/fobi-form-fields/{multi_field_form.slug}/").json()
        assert data["id"] == multi_field_form.id
        assert data["slug"] == multi_field_form.slug
        assert data["title"] == multi_field_form.name

    def test_field_count_matches_elements(self, admin_client, multi_field_form):
        data = admin_client.get(f"/api/fobi-form-fields/{multi_field_form.slug}/").json()
        assert len(data["fields"]) == 3


class TestFormFieldsMetadata:
    """Each field object must carry required metadata keys."""

    def _get_fields(self, client, slug):
        return {
            f["name"]: f
            for f in client.get(f"/api/fobi-form-fields/{slug}/").json()["fields"]
        }

    def test_every_field_has_required_keys(self, admin_client, multi_field_form):
        fields = self._get_fields(admin_client, multi_field_form.slug)
        for name, info in fields.items():
            for key in ("name", "type", "widget", "label", "required", "help_text"):
                assert key in info, f"Field '{name}' missing key '{key}'"

    def test_text_field_metadata(self, admin_client, multi_field_form):
        fields = self._get_fields(admin_client, multi_field_form.slug)
        f = fields["short_text"]
        assert f["type"] == "CharField"
        assert f["label"] == "Short Text"
        assert f["required"] is True

    def test_select_field_has_choices(self, admin_client, multi_field_form):
        fields = self._get_fields(admin_client, multi_field_form.slug)
        f = fields["color"]
        assert "choices" in f
        values = [c["value"] for c in f["choices"]]
        assert "red" in values
        assert "green" in values
        assert "blue" in values


class TestFormFieldsWidgetDisambiguation:
    """Widget key distinguishes ambiguous field types."""

    def _get_fields(self, client, slug):
        return {
            f["name"]: f
            for f in client.get(f"/api/fobi-form-fields/{slug}/").json()["fields"]
        }

    def test_text_input_widget(self, admin_client, multi_field_form):
        fields = self._get_fields(admin_client, multi_field_form.slug)
        assert fields["short_text"]["type"] == "CharField"
        assert fields["short_text"]["widget"] == "TextInput"

    def test_textarea_widget(self, admin_client, multi_field_form):
        fields = self._get_fields(admin_client, multi_field_form.slug)
        assert fields["long_text"]["type"] == "CharField"
        assert fields["long_text"]["widget"] == "Textarea"

    def test_select_widget(self, admin_client, multi_field_form):
        fields = self._get_fields(admin_client, multi_field_form.slug)
        assert fields["color"]["type"] == "ChoiceField"
        assert fields["color"]["widget"] == "Select"


class TestFormFieldsErrorHandling:
    """404 and edge cases."""

    def test_nonexistent_slug_returns_404(self, admin_client):
        response = admin_client.get("/api/fobi-form-fields/does-not-exist/")
        assert response.status_code == 404

    def test_private_form_returns_404(self, db, admin_user, admin_client):
        FormEntry.objects.create(
            user=admin_user,
            name="Private Form",
            slug="private-form",
            is_public=False,
        )
        response = admin_client.get("/api/fobi-form-fields/private-form/")
        assert response.status_code == 404

    def test_existing_form_entry_fixture_works(self, admin_client, form_entry):
        """The shared form_entry fixture (text element) returns valid data."""
        response = admin_client.get(f"/api/fobi-form-fields/{form_entry.slug}/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["fields"]) >= 1
        assert data["fields"][0]["widget"] == "TextInput"
