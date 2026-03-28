"""T07/T10/T20 – DB Store Entries: admin routing, readonly contract, pretty JSON.

Verifies:
- "View entries" action in handler inline links to admin changelist (not /fobi/<id>/).
- Filtered admin changelist is accessible for staff.
- Non-superuser staff can view but cannot modify saved entries.
- Superusers retain full edit access to saved entries.
- Staff readonly access works without explicit permission assignment.
- Detail view shows submitted data (JSON) as an HTML template without raw duplication.
"""

import pytest
from django.contrib.auth.models import Permission, User
from django.test import Client
from django.urls import reverse


@pytest.fixture()
def staff_user(db):
    """Create a non-superuser staff member with view-only permissions."""
    user = User.objects.create_user(
        username="staffuser",
        email="staff@test.local",
        password="staffpass123",
        is_staff=True,
    )
    from django.contrib.contenttypes.models import ContentType
    from fobi.contrib.plugins.form_handlers.db_store.models import (
        SavedFormDataEntry,
    )

    ct = ContentType.objects.get_for_model(SavedFormDataEntry)
    for codename in ("view_savedformdataentry",):
        perm = Permission.objects.get(content_type=ct, codename=codename)
        user.user_permissions.add(perm)
    from fobi.models import FormEntry

    ct_form = ContentType.objects.get_for_model(FormEntry)
    for codename in (
        "view_formentry",
        "change_formentry",
        "add_formentry",
    ):
        try:
            perm = Permission.objects.get(content_type=ct_form, codename=codename)
            user.user_permissions.add(perm)
        except Permission.DoesNotExist:
            pass
    return user


@pytest.fixture()
def staff_client(staff_user):
    """Return a Django test client logged in as the staff user."""
    client = Client()
    client.login(username="staffuser", password="staffpass123")
    return client


CHANGELIST_URL_NAME = (
    "admin:fobi_contrib_plugins_form_handlers_db_store_savedformdataentry_changelist"
)
CHANGE_URL_NAME = (
    "admin:fobi_contrib_plugins_form_handlers_db_store_savedformdataentry_change"
)
ADD_URL_NAME = (
    "admin:fobi_contrib_plugins_form_handlers_db_store_savedformdataentry_add"
)


class TestViewEntriesActionLink:
    """T07/T10: handler inline 'View entries' must link to admin changelist."""

    def test_view_entries_links_to_admin_changelist(self, admin_client, form_entry):
        """The handler inline action 'View entries' must point to the admin
        changelist with form_entry filter."""
        url = reverse("admin:unfold_fobi_formentryproxy_change", args=[form_entry.pk])
        response = admin_client.get(url)
        html = response.content.decode()
        changelist_url = reverse(CHANGELIST_URL_NAME)
        assert changelist_url in html
        assert f"form_entry__id__exact={form_entry.pk}" in html

    def test_view_entries_does_not_link_to_fobi_frontend(
        self, admin_client, form_entry
    ):
        """The old /fobi/<id>/ URL must not appear as an action link."""
        url = reverse("admin:unfold_fobi_formentryproxy_change", args=[form_entry.pk])
        response = admin_client.get(url)
        html = response.content.decode()
        old_url = f"/fobi/{form_entry.pk}/"
        assert f'href="{old_url}"' not in html


class TestFilteredChangelist:
    """T07: admin changelist for saved entries with form filter."""

    def test_changelist_accessible_for_admin(
        self, admin_client, form_entry, rest_submitted_form_data
    ):
        url = reverse(CHANGELIST_URL_NAME) + f"?form_entry__id__exact={form_entry.pk}"
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_changelist_shows_filtered_entry(
        self, admin_client, form_entry, rest_submitted_form_data
    ):
        url = reverse(CHANGELIST_URL_NAME) + f"?form_entry__id__exact={form_entry.pk}"
        response = admin_client.get(url)
        html = response.content.decode()
        # Pretty JSON preview shows submitted field values
        assert "Alice Example" in html

    def test_changelist_accessible_for_staff(
        self, staff_client, form_entry, rest_submitted_form_data
    ):
        url = reverse(CHANGELIST_URL_NAME) + f"?form_entry__id__exact={form_entry.pk}"
        response = staff_client.get(url)
        assert response.status_code == 200


class TestReadonlyForNonSuperuser:
    """T07: non-superuser staff cannot modify saved form data entries."""

    def test_staff_cannot_access_add_form(self, staff_client):
        response = staff_client.get(reverse(ADD_URL_NAME))
        assert response.status_code == 403

    def test_staff_sees_readonly_change_form(
        self, staff_client, form_entry, rest_submitted_form_data
    ):
        """Staff with view perm can open the detail page but it is readonly."""
        saved_entry = rest_submitted_form_data["saved_entry"]
        url = reverse(CHANGE_URL_NAME, args=[saved_entry.pk])
        response = staff_client.get(url)
        assert response.status_code == 200
        html = response.content.decode()
        assert '_save"' not in html

    def test_staff_post_change_is_forbidden(
        self, staff_client, form_entry, rest_submitted_form_data
    ):
        """POST to the change form must be rejected for non-superusers."""
        saved_entry = rest_submitted_form_data["saved_entry"]
        url = reverse(CHANGE_URL_NAME, args=[saved_entry.pk])
        response = staff_client.post(url, data={})
        assert response.status_code == 403

    def test_staff_cannot_delete_entry(
        self, staff_client, form_entry, rest_submitted_form_data
    ):
        saved_entry = rest_submitted_form_data["saved_entry"]
        url = reverse(CHANGE_URL_NAME, args=[saved_entry.pk]) + "delete/"
        response = staff_client.get(url)
        assert response.status_code == 403


class TestSuperuserRetainsAccess:
    """T07: superusers must retain edit access but no manual add access."""

    def test_superuser_cannot_access_add_form(self, admin_client):
        response = admin_client.get(reverse(ADD_URL_NAME))
        assert response.status_code == 403

    def test_superuser_can_access_change_form(
        self, admin_client, form_entry, rest_submitted_form_data
    ):
        saved_entry = rest_submitted_form_data["saved_entry"]
        url = reverse(CHANGE_URL_NAME, args=[saved_entry.pk])
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_superuser_sees_save_button(
        self, admin_client, form_entry, rest_submitted_form_data
    ):
        saved_entry = rest_submitted_form_data["saved_entry"]
        url = reverse(CHANGE_URL_NAME, args=[saved_entry.pk])
        response = admin_client.get(url)
        html = response.content.decode()
        assert "submit" in html.lower()

    def test_programmatic_entry_creation_still_works(self, admin_client, form_entry):
        from fobi.contrib.plugins.form_handlers.db_store.models import (
            SavedFormDataEntry,
        )

        before = SavedFormDataEntry.objects.filter(form_entry=form_entry).count()
        response = admin_client.put(
            f"/api/fobi-form-entry/{form_entry.slug}/",
            data='{"full_name":"Alice Example"}',
            content_type="application/json",
        )

        after = SavedFormDataEntry.objects.filter(form_entry=form_entry).count()
        assert response.status_code == 200
        assert after == before + 1


class TestStaffReadonlyWithoutExplicitPerms:
    """T20: staff can view entries without an explicit view_savedformdataentry perm."""

    @pytest.fixture()
    def bare_staff_user(self, db):
        """Staff user with NO explicit model permissions."""
        return User.objects.create_user(
            username="barestaff",
            email="bare@test.local",
            password="barepass",
            is_staff=True,
        )

    @pytest.fixture()
    def bare_staff_client(self, bare_staff_user):
        client = Client()
        client.login(username="barestaff", password="barepass")
        return client

    def test_bare_staff_can_view_changelist(
        self, bare_staff_client, form_entry, rest_submitted_form_data
    ):
        """Staff without explicit perm assignment can view the changelist."""
        url = reverse(CHANGELIST_URL_NAME)
        response = bare_staff_client.get(url)
        assert response.status_code == 200

    def test_bare_staff_can_view_detail(
        self, bare_staff_client, form_entry, rest_submitted_form_data
    ):
        """Staff without explicit perm assignment can view the detail page."""
        saved_entry = rest_submitted_form_data["saved_entry"]
        url = reverse(CHANGE_URL_NAME, args=[saved_entry.pk])
        response = bare_staff_client.get(url)
        assert response.status_code == 200

    def test_bare_staff_cannot_change(
        self, bare_staff_client, form_entry, rest_submitted_form_data
    ):
        saved_entry = rest_submitted_form_data["saved_entry"]
        url = reverse(CHANGE_URL_NAME, args=[saved_entry.pk])
        response = bare_staff_client.post(url, data={})
        assert response.status_code == 403

    def test_bare_staff_cannot_delete(
        self, bare_staff_client, form_entry, rest_submitted_form_data
    ):
        saved_entry = rest_submitted_form_data["saved_entry"]
        url = reverse(CHANGE_URL_NAME, args=[saved_entry.pk]) + "delete/"
        response = bare_staff_client.get(url)
        assert response.status_code == 403


class TestPrettyJsonRendering:
    """T20: detail view shows submitted data as pretty JSON, no raw duplication."""

    def test_detail_shows_labeled_fields(
        self, admin_client, form_entry, rest_submitted_form_data
    ):
        """Detail page must render each submitted field with its label."""
        saved_entry = rest_submitted_form_data["saved_entry"]
        url = reverse(CHANGE_URL_NAME, args=[saved_entry.pk])
        response = admin_client.get(url)
        html = response.content.decode()
        # Field label from form_data_headers
        assert "Full Name" in html
        # Field value
        assert "Alice Example" in html
        # Each value should be selectable (select-all CSS class)
        assert "select-all" in html

    def test_detail_shows_submitted_data_fieldset(
        self, admin_client, form_entry, rest_submitted_form_data
    ):
        """Detail page must show 'Submitted data' fieldset."""
        saved_entry = rest_submitted_form_data["saved_entry"]
        url = reverse(CHANGE_URL_NAME, args=[saved_entry.pk])
        response = admin_client.get(url)
        html = response.content.decode()
        assert "Submitted data" in html

    def test_detail_hides_raw_fields(
        self, admin_client, form_entry, rest_submitted_form_data
    ):
        """Detail page must NOT show raw 'saved_data' or 'form_data_headers' fields."""
        saved_entry = rest_submitted_form_data["saved_entry"]
        url = reverse(CHANGE_URL_NAME, args=[saved_entry.pk])
        response = admin_client.get(url)
        html = response.content.decode()
        # Raw fields should not appear as editable form fields
        assert 'name="saved_data"' not in html
        assert 'name="form_data_headers"' not in html

    def test_mixin_is_reusable(self):
        """The integration mixin must be importable from the admin package."""
        from unfold_fobi.admin.saved_data_entry import (
            SavedFormDataEntryAdminIntegrationMixin,
        )

        assert hasattr(
            SavedFormDataEntryAdminIntegrationMixin, "pretty_saved_data_display"
        )
        assert hasattr(SavedFormDataEntryAdminIntegrationMixin, "has_view_permission")
