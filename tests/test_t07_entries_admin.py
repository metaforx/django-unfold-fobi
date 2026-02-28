"""T07/T10 – DB Store Entries: admin routing and readonly contract.

Verifies:
- "View entries" action in handler inline links to admin changelist (not /fobi/<id>/).
- Filtered admin changelist is accessible for staff.
- Non-superuser staff can view but cannot modify saved entries.
- Superusers retain full edit access to saved entries.
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
        assert "Full Name" in html

    def test_changelist_accessible_for_staff(
        self, staff_client, form_entry, rest_submitted_form_data
    ):
        url = reverse(CHANGELIST_URL_NAME) + f"?form_entry__id__exact={form_entry.pk}"
        response = staff_client.get(url)
        assert response.status_code == 200


class TestReadonlyForNonSuperuser:
    """T07: non-superuser staff cannot modify saved form data entries."""

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
    """T07: superusers must retain full edit access."""

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
