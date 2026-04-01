"""T21: Safe form delete — unlink saved entries, app-level permissions."""

import json

import pytest
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory
from django.urls import reverse
from fobi.contrib.plugins.form_handlers.db_store.models import SavedFormDataEntry
from fobi.models import FormElementEntry, FormEntry, FormHandlerEntry

from unfold_fobi.models import FormEntryProxy


@pytest.fixture()
def staff_user(db):
    """Non-superuser staff with delete permission on FormEntry."""
    user = User.objects.create_user(
        username="staff", password="staffpass", is_staff=True
    )
    ct = ContentType.objects.get_for_model(FormEntry)
    perm = Permission.objects.get(codename="delete_formentry", content_type=ct)
    user.user_permissions.add(perm)
    return user


@pytest.fixture()
def staff_user_no_delete(db):
    """Non-superuser staff without delete permission on FormEntry."""
    return User.objects.create_user(
        username="staff_no_delete", password="staffpass", is_staff=True
    )


@pytest.fixture()
def staff_client(staff_user):
    from django.test import Client

    client = Client()
    client.login(username="staff", password="staffpass")
    return client


@pytest.fixture()
def staff_form(db, staff_user):
    """Form owned by staff_user."""
    entry = FormEntry.objects.create(
        user=staff_user,
        name="Staff Form",
        slug="staff-form",
        is_public=True,
    )
    FormElementEntry.objects.create(
        form_entry=entry,
        plugin_uid="text",
        plugin_data=json.dumps({"label": "Q", "name": "q", "required": False}),
        position=1,
    )
    FormHandlerEntry.objects.get_or_create(form_entry=entry, plugin_uid="db_store")
    return entry


@pytest.fixture()
def form_with_submissions(form_entry, admin_client):
    """form_entry with two saved submissions."""
    for i in range(2):
        admin_client.put(
            f"/api/fobi-form-entry/{form_entry.slug}/",
            data=json.dumps({"full_name": f"User {i}"}),
            content_type="application/json",
        )
    assert SavedFormDataEntry.objects.filter(form_entry=form_entry).count() == 2
    return form_entry


def _get_admin_instance():
    from django.contrib.admin.sites import AdminSite
    from unfold_fobi.admin import FormEntryProxyAdmin

    return FormEntryProxyAdmin(FormEntryProxy, AdminSite())


class TestSafeDeletePreservesData:
    """Deleting a form must preserve submitted data."""

    def test_bulk_safe_delete_preserves_saved_entries(
        self, admin_client, form_with_submissions
    ):
        entry = form_with_submissions
        saved_ids = list(
            SavedFormDataEntry.objects.filter(form_entry=entry).values_list(
                "id", flat=True
            )
        )
        assert len(saved_ids) == 2

        url = reverse("admin:unfold_fobi_formentryproxy_changelist")
        admin_client.post(
            url,
            {
                "action": "safe_delete_selected",
                "_selected_action": [entry.pk],
            },
            follow=True,
        )

        assert not FormEntry.objects.filter(pk=entry.pk).exists()
        surviving = SavedFormDataEntry.objects.filter(id__in=saved_ids)
        assert surviving.count() == 2
        for row in surviving:
            assert row.form_entry is None

    def test_delete_model_preserves_saved_entries(
        self, admin_user, form_with_submissions
    ):
        entry = form_with_submissions
        saved_ids = list(
            SavedFormDataEntry.objects.filter(form_entry=entry).values_list(
                "id", flat=True
            )
        )

        ma = _get_admin_instance()
        request = RequestFactory().post("/")
        request.user = admin_user
        request._messages = FakeMessages()
        ma.delete_model(request, entry)

        assert not FormEntry.objects.filter(pk=entry.pk).exists()
        surviving = SavedFormDataEntry.objects.filter(id__in=saved_ids)
        assert surviving.count() == 2

    def test_delete_form_without_submissions(self, admin_client, form_entry):
        url = reverse("admin:unfold_fobi_formentryproxy_changelist")
        admin_client.post(
            url,
            {
                "action": "safe_delete_selected",
                "_selected_action": [form_entry.pk],
            },
            follow=True,
        )
        assert not FormEntry.objects.filter(pk=form_entry.pk).exists()


class TestDeletePermissions:
    """Delete permission follows app-level auth permission only."""

    def test_superuser_can_delete_any_form(self, admin_user, staff_form):
        ma = _get_admin_instance()
        request = RequestFactory().get("/")
        request.user = admin_user
        assert ma.has_delete_permission(request, staff_form) is True

    def test_owner_can_delete_own_form(self, staff_user, staff_form):
        # Refetch to clear permission cache
        user = User.objects.get(pk=staff_user.pk)
        ma = _get_admin_instance()
        request = RequestFactory().get("/")
        request.user = user
        assert ma.has_delete_permission(request, staff_form) is True

    def test_staff_without_delete_perm_cannot_delete_any_form(
        self, staff_user_no_delete, form_entry
    ):
        user = User.objects.get(pk=staff_user_no_delete.pk)
        ma = _get_admin_instance()
        request = RequestFactory().get("/")
        request.user = user
        assert ma.has_delete_permission(request, form_entry) is False

    def test_staff_can_delete_foreign_form_with_delete_perm(self, staff_user, form_entry):
        """Object ownership does not gate delete when app delete perm exists."""
        user = User.objects.get(pk=staff_user.pk)
        ma = _get_admin_instance()
        request = RequestFactory().get("/")
        request.user = user
        assert ma.has_delete_permission(request, form_entry) is True

    def test_safe_delete_action_deletes_all_selected_forms_with_delete_perm(
        self, staff_user, staff_form, form_entry
    ):
        """Bulk action deletes selected forms regardless of ownership."""
        user = User.objects.get(pk=staff_user.pk)
        ma = _get_admin_instance()
        request = RequestFactory().post("/")
        request.user = user
        request._messages = FakeMessages()

        qs = FormEntryProxy.objects.filter(
            pk__in=[staff_form.pk, form_entry.pk]
        )
        ma.safe_delete_selected(request, qs)

        # Both forms deleted because permission is app-level.
        assert not FormEntry.objects.filter(pk=staff_form.pk).exists()
        assert not FormEntry.objects.filter(pk=form_entry.pk).exists()

    def test_safe_delete_action_skips_all_forms_without_delete_perm(
        self, staff_user_no_delete, staff_form, form_entry
    ):
        user = User.objects.get(pk=staff_user_no_delete.pk)
        ma = _get_admin_instance()
        request = RequestFactory().post("/")
        request.user = user
        request._messages = FakeMessages()

        qs = FormEntryProxy.objects.filter(pk__in=[staff_form.pk, form_entry.pk])
        ma.safe_delete_selected(request, qs)

        assert FormEntry.objects.filter(pk=staff_form.pk).exists()
        assert FormEntry.objects.filter(pk=form_entry.pk).exists()


class TestUnlinkService:
    """Unit tests for the unlink_saved_entries service function."""

    def test_unlink_nullifies_fk(self, form_with_submissions):
        from unfold_fobi.services import unlink_saved_entries

        count = unlink_saved_entries(form_with_submissions)
        assert count == 2

        for row in SavedFormDataEntry.objects.all():
            assert row.form_entry_id is None

    def test_unlink_returns_zero_for_no_submissions(self, form_entry):
        from unfold_fobi.services import unlink_saved_entries

        assert unlink_saved_entries(form_entry) == 0

    def test_unlink_is_idempotent(self, form_with_submissions):
        from unfold_fobi.services import unlink_saved_entries

        unlink_saved_entries(form_with_submissions)
        assert unlink_saved_entries(form_with_submissions) == 0


class FakeMessages:
    """Minimal messages backend for RequestFactory requests."""

    def __init__(self):
        self.messages = []

    def add(self, level, message, extra_tags=""):
        self.messages.append(message)
