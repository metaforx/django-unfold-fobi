"""GET /api/fobi-form-fields/{slug}/ endpoint tests.

Covers response structure, field metadata, widget disambiguation, and error handling.
"""

import json

import pytest
from fobi.models import FormElementEntry, FormEntry, FormHandlerEntry

# -- Plugin UID → (field name, plugin_data, expected_type, expected_widget) --
# Covers all standard fobi field plugins except model-object selects (need ContentType)
# and input (uses bare django.forms.fields.Field).
PLUGIN_SPECS = [
    ("boolean", "agree", {"label": "Agree", "name": "agree"}, "BooleanField", "CheckboxInput"),
    ("checkbox_select_multiple", "colors", {"label": "Colors", "name": "colors", "choices": "r\ng\nb"}, "MultipleChoiceField", "CheckboxSelectMultiple"),
    ("date", "birth_date", {"label": "Birth", "name": "birth_date"}, "DateField", "DateInput"),
    ("date_drop_down", "start_date", {"label": "Start", "name": "start_date", "year_min": 2000, "year_max": 2030}, "DateField", "SelectDateWidget"),
    ("datetime", "event_at", {"label": "Event", "name": "event_at"}, "DateTimeField", "DateTimeInput"),
    ("decimal", "price", {"label": "Price", "name": "price", "initial": 0, "max_value": 9999, "min_value": 0, "max_digits": 6, "decimal_places": 2}, "DecimalField", "NumberInput"),
    ("email", "e_mail", {"label": "Email", "name": "e_mail"}, "EmailField", "EmailInput"),
    ("file", "attachment", {"label": "File", "name": "attachment"}, "FileField", "ClearableFileInput"),
    ("float", "weight", {"label": "Weight", "name": "weight"}, "FloatField", "NumberInput"),
    ("hidden", "token", {"label": "Token", "name": "token"}, "HiddenField", "HiddenInput"),
    ("integer", "age", {"label": "Age", "name": "age"}, "IntegerField", "NumberInput"),
    ("ip_address", "ip", {"label": "IP", "name": "ip"}, "IPAddressField", "TextInput"),
    ("null_boolean", "maybe", {"label": "Maybe", "name": "maybe"}, "BooleanField", "NullBooleanSelect"),
    ("password", "secret", {"label": "Secret", "name": "secret"}, "CharField", "PasswordInput"),
    ("radio", "size", {"label": "Size", "name": "size", "choices": "S\nM\nL"}, "ChoiceField", "RadioSelect"),
    ("regex", "code", {"label": "Code", "name": "code", "regex": r"^\d+$"}, "RegexField", "TextInput"),
    ("select", "color", {"label": "Color", "name": "color", "choices": "r\ng\nb"}, "ChoiceField", "Select"),
    ("select_multiple", "tags", {"label": "Tags", "name": "tags", "choices": "a\nb\nc"}, "MultipleChoiceField", "SelectMultiple"),
    ("slug", "page_slug", {"label": "Slug", "name": "page_slug"}, "SlugField", "TextInput"),
    ("text", "short_text", {"label": "Short", "name": "short_text", "required": True}, "CharField", "TextInput"),
    ("textarea", "long_text", {"label": "Long", "name": "long_text"}, "CharField", "Textarea"),
    ("time", "start_time", {"label": "Time", "name": "start_time"}, "TimeField", "TextInput"),
    ("url", "website", {"label": "URL", "name": "website"}, "URLField", "URLInput"),
]


@pytest.fixture()
def multi_field_form(db, admin_user):
    """Form with all standard fobi field plugins."""
    entry = FormEntry.objects.create(
        user=admin_user,
        name="Multi Field Form",
        slug="multi-field-form",
        is_public=True,
    )
    for pos, (uid, name, data, *_) in enumerate(PLUGIN_SPECS, start=1):
        FormElementEntry.objects.create(
            form_entry=entry,
            plugin_uid=uid,
            plugin_data=json.dumps(data),
            position=pos,
        )
    FormHandlerEntry.objects.get_or_create(form_entry=entry, plugin_uid="db_store")
    return entry


def _get_fields(client, slug):
    return {
        f["name"]: f
        for f in client.get(f"/api/fobi-form-fields/{slug}/").json()["fields"]
    }


class TestFormFieldsResponseStructure:
    """Top-level response shape and envelope keys."""

    def test_returns_200(self, admin_client, multi_field_form):
        response = admin_client.get(f"/api/fobi-form-fields/{multi_field_form.slug}/")
        assert response.status_code == 200

    def test_envelope_keys(self, admin_client, multi_field_form):
        data = admin_client.get(f"/api/fobi-form-fields/{multi_field_form.slug}/").json()
        for key in (
            "id", "slug", "title", "is_active",
            "active_date_from", "active_date_to",
            "success_page_title", "success_page_message", "fields",
        ):
            assert key in data, f"Missing envelope key '{key}'"
        for key in ("id", "slug", "title", "csrf_token", "fields"):
            assert key in data, f"Missing envelope key '{key}'"
        assert isinstance(data["fields"], list)

    def test_envelope_values(self, admin_client, multi_field_form):
        data = admin_client.get(f"/api/fobi-form-fields/{multi_field_form.slug}/").json()
        assert data["id"] == multi_field_form.id
        assert data["slug"] == multi_field_form.slug
        assert data["title"] == multi_field_form.name
        assert data["is_active"] is True

    def test_csrf_token_is_non_empty_string(self, admin_client, multi_field_form):
        data = admin_client.get(f"/api/fobi-form-fields/{multi_field_form.slug}/").json()
        assert isinstance(data["csrf_token"], str)
        assert len(data["csrf_token"]) > 0

    def test_field_count_matches_elements(self, admin_client, multi_field_form):
        data = admin_client.get(f"/api/fobi-form-fields/{multi_field_form.slug}/").json()
        assert len(data["fields"]) == len(PLUGIN_SPECS)


class TestFormFieldsMetadata:
    """Each field object must carry required metadata keys."""

    def test_every_field_has_required_keys(self, admin_client, multi_field_form):
        fields = _get_fields(admin_client, multi_field_form.slug)
        for name, info in fields.items():
            for key in ("name", "type", "widget", "label", "required", "help_text"):
                assert key in info, f"Field '{name}' missing key '{key}'"

    def test_select_field_has_choices(self, admin_client, multi_field_form):
        fields = _get_fields(admin_client, multi_field_form.slug)
        f = fields["color"]
        assert "choices" in f
        values = [c["value"] for c in f["choices"]]
        assert "r" in values


class TestFormFieldsWidgetDisambiguation:
    """Widget key is correct for every registered fobi field plugin."""

    @pytest.mark.parametrize(
        "field_name, expected_type, expected_widget",
        [
            (name, exp_type, exp_widget)
            for (_uid, name, _data, exp_type, exp_widget) in PLUGIN_SPECS
        ],
        ids=[uid for (uid, *_rest) in PLUGIN_SPECS],
    )
    def test_widget(
        self, admin_client, multi_field_form, field_name, expected_type, expected_widget
    ):
        fields = _get_fields(admin_client, multi_field_form.slug)
        assert fields[field_name]["type"] == expected_type
        assert fields[field_name]["widget"] == expected_widget


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
