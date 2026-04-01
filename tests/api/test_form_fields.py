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

    def test_existing_form_entry_fixture_works(self, admin_client, form_entry):
        """The shared form_entry fixture (text element) returns valid data."""
        response = admin_client.get(f"/api/fobi-form-fields/{form_entry.slug}/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["fields"]) >= 1
        assert data["fields"][0]["widget"] == "TextInput"


class TestFormFieldsPreviewAccess:
    """Preview access for non-public forms."""

    @pytest.fixture()
    def private_form(self, db, admin_user):
        from django.contrib.sites.models import Site
        from unfold_fobi.contrib.sites.services import ensure_binding

        entry = FormEntry.objects.create(
            user=admin_user,
            name="Private Form",
            slug="private-form",
            is_public=False,
        )
        FormElementEntry.objects.create(
            form_entry=entry,
            plugin_uid="text",
            plugin_data=json.dumps(
                {"label": "Name", "name": "name", "required": True}
            ),
            position=1,
        )
        FormHandlerEntry.objects.get_or_create(
            form_entry=entry, plugin_uid="db_store"
        )
        binding, _ = ensure_binding(entry)
        site, _ = Site.objects.get_or_create(
            id=1, defaults={"domain": "testserver", "name": "Test"}
        )
        binding.sites.add(site)
        return entry

    @pytest.fixture()
    def staff_with_perm(self, db, settings):
        from django.contrib.auth.models import Permission, User
        from django.contrib.contenttypes.models import ContentType
        from fobi.models import FormEntry

        # Configure sites_for_user to return site 1 for this user
        settings.UNFOLD_FOBI_SITES_FOR_USER = (
            "tests.api.test_form_fields._sites_for_previewer"
        )
        user = User.objects.create_user(
            username="previewer", password="pass", is_staff=True
        )
        ct = ContentType.objects.get_for_model(FormEntry)
        perm = Permission.objects.get(
            codename="view_formentry", content_type=ct
        )
        user.user_permissions.add(perm)
        return user

    @pytest.fixture()
    def staff_without_perm(self, db):
        from django.contrib.auth.models import User

        return User.objects.create_user(
            username="noperm", password="pass", is_staff=True
        )

    def test_public_form_anonymous_gets_200(self, client, multi_field_form):
        response = client.get(f"/api/fobi-form-fields/{multi_field_form.slug}/")
        assert response.status_code == 200
        assert response.json()["is_preview"] is False

    def test_public_form_staff_gets_200_not_preview(self, admin_client, multi_field_form):
        response = admin_client.get(f"/api/fobi-form-fields/{multi_field_form.slug}/")
        assert response.status_code == 200
        assert response.json()["is_preview"] is False

    def test_private_form_anonymous_gets_404(self, client, private_form):
        response = client.get(f"/api/fobi-form-fields/{private_form.slug}/")
        assert response.status_code == 404

    def test_private_form_staff_without_perm_gets_404(
        self, staff_without_perm, private_form
    ):
        from django.test import Client

        c = Client()
        c.login(username="noperm", password="pass")
        response = c.get(f"/api/fobi-form-fields/{private_form.slug}/")
        assert response.status_code == 404

    def test_private_form_staff_with_perm_gets_200(
        self, staff_with_perm, private_form
    ):
        from django.test import Client

        c = Client()
        c.login(username="previewer", password="pass")
        response = c.get(f"/api/fobi-form-fields/{private_form.slug}/")
        assert response.status_code == 200
        data = response.json()
        assert data["is_preview"] is True
        assert len(data["fields"]) >= 1

    def test_private_form_superuser_gets_preview(
        self, admin_client, private_form
    ):
        response = admin_client.get(f"/api/fobi-form-fields/{private_form.slug}/")
        assert response.status_code == 200
        assert response.json()["is_preview"] is True


class TestPreviewSiteScope:
    """T23a: Site-scoped preview when unfold_fobi.contrib.sites is installed."""

    @pytest.fixture()
    def site_a(self, db):
        from django.contrib.sites.models import Site

        return Site.objects.get_or_create(
            id=1, defaults={"domain": "a.example.com", "name": "Site A"}
        )[0]

    @pytest.fixture()
    def site_b(self, db):
        from django.contrib.sites.models import Site

        return Site.objects.create(domain="b.example.com", name="Site B")

    @pytest.fixture()
    def private_form_on_site_a(self, db, admin_user, site_a):
        from unfold_fobi.contrib.sites.services import ensure_binding

        entry = FormEntry.objects.create(
            user=admin_user,
            name="Site A Form",
            slug="site-a-form",
            is_public=False,
        )
        FormElementEntry.objects.create(
            form_entry=entry,
            plugin_uid="text",
            plugin_data=json.dumps(
                {"label": "Name", "name": "name", "required": True}
            ),
            position=1,
        )
        FormHandlerEntry.objects.get_or_create(
            form_entry=entry, plugin_uid="db_store"
        )
        binding, _ = ensure_binding(entry)
        binding.sites.add(site_a)
        return entry

    @pytest.fixture()
    def private_form_no_binding(self, db, admin_user):
        entry = FormEntry.objects.create(
            user=admin_user,
            name="Unbound Form",
            slug="unbound-form",
            is_public=False,
        )
        FormElementEntry.objects.create(
            form_entry=entry,
            plugin_uid="text",
            plugin_data=json.dumps(
                {"label": "Name", "name": "name", "required": True}
            ),
            position=1,
        )
        FormHandlerEntry.objects.get_or_create(
            form_entry=entry, plugin_uid="db_store"
        )
        return entry

    @pytest.fixture()
    def staff_on_site_a(self, db, site_a, settings):
        from django.contrib.auth.models import Permission, User
        from django.contrib.contenttypes.models import ContentType

        # Point sites_for_user to a test helper that returns site_a for this user
        settings.UNFOLD_FOBI_SITES_FOR_USER = (
            "tests.api.test_form_fields._sites_for_staff_a"
        )
        user = User.objects.create_user(
            username="staff_a", password="pass", is_staff=True
        )
        ct = ContentType.objects.get_for_model(FormEntry)
        perm = Permission.objects.get(codename="view_formentry", content_type=ct)
        user.user_permissions.add(perm)
        return user

    def test_staff_on_matching_site_gets_preview(
        self, staff_on_site_a, private_form_on_site_a
    ):
        from django.test import Client

        c = Client()
        c.login(username="staff_a", password="pass")
        response = c.get(f"/api/fobi-form-fields/{private_form_on_site_a.slug}/")
        assert response.status_code == 200
        assert response.json()["is_preview"] is True

    def test_staff_on_different_site_gets_404(
        self, staff_on_site_a, private_form_on_site_a, site_a, site_b
    ):
        from django.test import Client
        from unfold_fobi.contrib.sites.services import ensure_binding

        # Move form to site_b only
        binding, _ = ensure_binding(private_form_on_site_a)
        binding.sites.set([site_b])

        c = Client()
        c.login(username="staff_a", password="pass")
        response = c.get(f"/api/fobi-form-fields/{private_form_on_site_a.slug}/")
        assert response.status_code == 404

    def test_form_without_binding_denied(
        self, staff_on_site_a, private_form_no_binding
    ):
        from django.test import Client

        c = Client()
        c.login(username="staff_a", password="pass")
        response = c.get(f"/api/fobi-form-fields/{private_form_no_binding.slug}/")
        assert response.status_code == 404

    def test_superuser_bypasses_site_check(
        self, admin_client, private_form_on_site_a
    ):
        response = admin_client.get(
            f"/api/fobi-form-fields/{private_form_on_site_a.slug}/"
        )
        assert response.status_code == 200
        assert response.json()["is_preview"] is True


def _sites_for_staff_a(user):
    """Test helper: return site id=1 for staff_a, empty for others."""
    from django.contrib.sites.models import Site

    if user.username == "staff_a":
        return Site.objects.filter(id=1)
    return Site.objects.none()


def _sites_for_previewer(user):
    """Test helper: return site id=1 for previewer, empty for others."""
    from django.contrib.sites.models import Site

    if user.username == "previewer":
        return Site.objects.filter(id=1)
    return Site.objects.none()
