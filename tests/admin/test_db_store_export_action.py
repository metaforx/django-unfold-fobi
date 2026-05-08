"""T27/T28 – db_store export action: regression tests.

T27 (inline button):
- Asserts the inline button targets the project-owned admin endpoint
  (not upstream Fobi's owner-filtered view), the endpoint correctly
  delegates to the same ``export_data`` admin action that powers the
  changelist's bulk action, permissions are enforced, input is
  validated, and the endpoint honors the project's opt-in site scoping
  via ``self.get_queryset(request)``.

T28 (mixed-form guard):
- Asserts the changelist bulk action rejects querysets spanning more
  than one ``form_entry`` parent and otherwise delegates to upstream
  unchanged. The mixin override is on the shared ``export_data``
  method; T27 patching swaps it out at the consumer-class level, so
  T28 patches one level up (``BaseSavedFormDataEntryAdmin``) to keep
  the override in the codepath under test.

The underlying ``DataExporter`` uses PostgreSQL-only ``DISTINCT ON``;
Fobi's SQLite fallback only catches ``NotImplementedError`` (not Django's
``NotSupportedError``), so the actual CSV-rendering path can't run on the
SQLite test DB. Tests therefore patch ``export_data`` to capture the
queryset our endpoint hands it — that is the contract T27 is enforcing.
"""

import json
from contextlib import contextmanager

import pytest
from django.contrib.auth.models import Permission, User
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
from helpers import get_admin_edit_url


EXPORT_URL_NAME = "admin:unfold_fobi_savedformdataentry_export"
UPSTREAM_FOBI_EXPORT_PATH = "/admin/fobi/db-store/export/"


@contextmanager
def _capture_export_data(monkeypatch):
    """Patch the registered admin's ``export_data`` to capture its queryset.

    Yields a dict that, after the patched view runs, holds:
      - ``queryset``: the QuerySet the endpoint passed in
      - ``ids``: a list of pks materialized from that queryset
    """
    from django.contrib import admin as django_admin
    from fobi.contrib.plugins.form_handlers.db_store.models import SavedFormDataEntry

    captured = {}
    registered = django_admin.site._registry[SavedFormDataEntry]

    def fake_export(self, request, queryset):
        captured["queryset"] = queryset
        captured["ids"] = list(queryset.values_list("pk", flat=True))
        response = HttpResponse(b"stub", content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=db_store_export_data.csv"
        return response

    monkeypatch.setattr(type(registered), "export_data", fake_export, raising=True)
    yield captured


@pytest.fixture()
def saved_entries(db, admin_user, form_entry):
    """Two saved submissions for ``form_entry``."""
    from fobi.contrib.plugins.form_handlers.db_store.models import SavedFormDataEntry

    headers = json.dumps({"full_name": "Full Name"})
    return [
        SavedFormDataEntry.objects.create(
            form_entry=form_entry,
            user=admin_user,
            saved_data=json.dumps({"full_name": "Alice"}),
            form_data_headers=headers,
        ),
        SavedFormDataEntry.objects.create(
            form_entry=form_entry,
            user=admin_user,
            saved_data=json.dumps({"full_name": "Bob"}),
            form_data_headers=headers,
        ),
    ]


@pytest.fixture()
def view_only_staff_user(db):
    """Staff user with view permission on SavedFormDataEntry only."""
    from django.contrib.contenttypes.models import ContentType
    from fobi.contrib.plugins.form_handlers.db_store.models import SavedFormDataEntry

    user = User.objects.create_user(
        username="viewstaff",
        email="viewstaff@test.local",
        password="pw",
        is_staff=True,
    )
    ct = ContentType.objects.get_for_model(SavedFormDataEntry)
    user.user_permissions.add(
        Permission.objects.get(content_type=ct, codename="view_savedformdataentry")
    )
    return user


@pytest.fixture()
def view_only_staff_client(view_only_staff_user):
    client = Client()
    client.login(username="viewstaff", password="pw")
    return client


@pytest.fixture()
def non_staff_user(db):
    """Authenticated user without is_staff."""
    return User.objects.create_user(
        username="plainuser", email="plain@test.local", password="pw"
    )


@pytest.fixture()
def non_staff_client(non_staff_user):
    client = Client()
    client.login(username="plainuser", password="pw")
    return client


class TestInlineButtonUrl:
    """Inline "Export entries" button must point to the project endpoint."""

    def test_inline_button_targets_project_export_url(
        self, admin_client, form_entry, saved_entries
    ):
        response = admin_client.get(get_admin_edit_url(form_entry.pk))
        html = response.content.decode()
        expected = reverse(EXPORT_URL_NAME) + f"?form_entry_id={form_entry.pk}"
        assert expected in html

    def test_inline_button_does_not_link_to_upstream_fobi_export(
        self, admin_client, form_entry, saved_entries
    ):
        response = admin_client.get(get_admin_edit_url(form_entry.pk))
        html = response.content.decode()
        assert UPSTREAM_FOBI_EXPORT_PATH not in html

    def test_view_entries_redirect_unchanged(self, admin_client, form_entry):
        """T07's "View entries" redirect must not regress."""
        response = admin_client.get(get_admin_edit_url(form_entry.pk))
        html = response.content.decode()
        changelist = reverse(
            "admin:fobi_contrib_plugins_form_handlers_db_store_savedformdataentry_changelist"
        )
        assert f"{changelist}?form_entry__id__exact={form_entry.pk}" in html


class TestExportEndpointDelegation:
    """The endpoint delegates to ``export_data`` with a correctly filtered queryset."""

    def test_delegates_with_form_entry_filtered_queryset(
        self, monkeypatch, admin_client, form_entry, saved_entries
    ):
        url = reverse(EXPORT_URL_NAME) + f"?form_entry_id={form_entry.pk}"
        with _capture_export_data(monkeypatch) as captured:
            response = admin_client.get(url)
        assert response.status_code == 200
        assert "db_store_export_data" in response["Content-Disposition"]
        assert set(captured["ids"]) == {entry.pk for entry in saved_entries}

    def test_other_admin_non_owner_gets_data(
        self, monkeypatch, other_admin_client, form_entry, saved_entries
    ):
        """The whole point of T27: a non-owner staff user gets the rows."""
        url = reverse(EXPORT_URL_NAME) + f"?form_entry_id={form_entry.pk}"
        with _capture_export_data(monkeypatch) as captured:
            response = other_admin_client.get(url)
        assert response.status_code == 200
        assert set(captured["ids"]) == {entry.pk for entry in saved_entries}

    def test_form_with_no_saved_entries_passes_empty_queryset(
        self, monkeypatch, admin_client, db, admin_user
    ):
        from fobi.models import FormEntry

        empty_form = FormEntry.objects.create(
            user=admin_user, name="Empty", slug="empty-form"
        )
        url = reverse(EXPORT_URL_NAME) + f"?form_entry_id={empty_form.pk}"
        with _capture_export_data(monkeypatch) as captured:
            response = admin_client.get(url)
        assert response.status_code == 200
        assert captured["ids"] == []

    def test_unrelated_form_entries_excluded(
        self, monkeypatch, admin_client, form_entry, saved_entries, db, admin_user
    ):
        """Saved entries on *other* forms must not leak into the export queryset."""
        from fobi.contrib.plugins.form_handlers.db_store.models import (
            SavedFormDataEntry,
        )
        from fobi.models import FormEntry

        other_form = FormEntry.objects.create(
            user=admin_user, name="Other", slug="other-form"
        )
        SavedFormDataEntry.objects.create(
            form_entry=other_form,
            user=admin_user,
            saved_data=json.dumps({"full_name": "Carol"}),
            form_data_headers=json.dumps({"full_name": "Full Name"}),
        )
        url = reverse(EXPORT_URL_NAME) + f"?form_entry_id={form_entry.pk}"
        with _capture_export_data(monkeypatch) as captured:
            response = admin_client.get(url)
        assert response.status_code == 200
        assert set(captured["ids"]) == {entry.pk for entry in saved_entries}


class TestExportEndpointPermissions:
    def test_anonymous_user_redirected_to_login(self, db, form_entry):
        url = reverse(EXPORT_URL_NAME) + f"?form_entry_id={form_entry.pk}"
        response = Client().get(url)
        assert response.status_code in (302, 403)
        assert response.status_code != 200

    def test_non_staff_user_blocked(self, non_staff_client, form_entry):
        url = reverse(EXPORT_URL_NAME) + f"?form_entry_id={form_entry.pk}"
        response = non_staff_client.get(url)
        assert response.status_code != 200

    def test_staff_with_view_permission_succeeds(
        self, monkeypatch, view_only_staff_client, form_entry, saved_entries
    ):
        url = reverse(EXPORT_URL_NAME) + f"?form_entry_id={form_entry.pk}"
        with _capture_export_data(monkeypatch):
            response = view_only_staff_client.get(url)
        assert response.status_code == 200


class TestExportEndpointInputValidation:
    def test_missing_form_entry_id_returns_400(self, admin_client):
        url = reverse(EXPORT_URL_NAME)
        response = admin_client.get(url)
        assert response.status_code == 400

    def test_non_integer_form_entry_id_returns_400(self, admin_client):
        url = reverse(EXPORT_URL_NAME) + "?form_entry_id=not-a-number"
        response = admin_client.get(url)
        assert response.status_code == 400


class TestExportEndpointSiteScopeInheritance:
    """The endpoint must build its queryset from ``self.get_queryset(request)``
    so any project-level site scoping (e.g. ``RelationSiteScopeAdminMixin``)
    is honored.

    URL routing caches the originally-registered admin instance's bound
    methods, so swapping ``admin.site._registry`` mid-test does not redirect
    requests to the new instance. Instead, these tests instantiate a
    ScopedAdmin directly and invoke ``export_for_form_entry`` against a
    hand-built request — exactly the codepath URL routing would take, with
    none of the cache surprises.
    """

    @pytest.fixture()
    def scoped_admin_factory(self, db):
        """Return a callable building a ScopedAdmin instance with a
        configurable allowed-site set."""
        from django.contrib import admin as django_admin
        from fobi.contrib.plugins.form_handlers.db_store.models import (
            SavedFormDataEntry,
        )
        from unfold_fobi.contrib.sites.admin import RelationSiteScopeAdminMixin

        registered_class = django_admin.site._registry[SavedFormDataEntry].__class__

        def _make(allowed_site_ids):
            from django.contrib.sites.models import Site

            class ScopedAdmin(RelationSiteScopeAdminMixin, registered_class):
                site_relation_lookup = "form_entry__site_binding__sites"

                def get_sites_for_user(self, user):
                    return Site.objects.filter(pk__in=allowed_site_ids)

            return ScopedAdmin(SavedFormDataEntry, django_admin.site)

        return _make

    @pytest.fixture()
    def site_bound_form(self, db, form_entry, saved_entries):
        from django.contrib.sites.models import Site
        from unfold_fobi.contrib.sites.services import ensure_binding

        site = Site.objects.first() or Site.objects.create(
            domain="t27.test", name="t27"
        )
        binding, _ = ensure_binding(form_entry)
        binding.sites.set([site])
        return form_entry, site

    def _invoke(self, admin_instance, user, form_entry_id):
        """Call ``export_for_form_entry`` directly and capture its queryset."""
        from django.test import RequestFactory

        captured = {}

        def fake_export(self, request, queryset):
            captured["ids"] = list(queryset.values_list("pk", flat=True))
            return HttpResponse(b"stub", content_type="text/csv")

        # Bind on the class so ``self.export_data`` resolves to fake_export
        # even though export_for_form_entry calls it via ``self``.
        admin_instance.__class__.export_data = fake_export
        request = RequestFactory().get(f"/?form_entry_id={form_entry_id}")
        request.user = user
        response = admin_instance.export_for_form_entry(request)
        return response, captured

    def test_user_without_site_access_gets_empty_queryset(
        self,
        view_only_staff_user,
        scoped_admin_factory,
        site_bound_form,
    ):
        form_entry, _site = site_bound_form
        admin_instance = scoped_admin_factory(allowed_site_ids=set())
        response, captured = self._invoke(
            admin_instance, view_only_staff_user, form_entry.pk
        )
        assert response.status_code == 200
        assert captured["ids"] == [], (
            "Site-scope filter was bypassed — endpoint must use "
            "self.get_queryset(request), not the default manager."
        )

    def test_user_granted_site_gets_queryset_with_rows(
        self,
        view_only_staff_user,
        scoped_admin_factory,
        site_bound_form,
        saved_entries,
    ):
        form_entry, site = site_bound_form
        admin_instance = scoped_admin_factory(allowed_site_ids={site.pk})
        response, captured = self._invoke(
            admin_instance, view_only_staff_user, form_entry.pk
        )
        assert response.status_code == 200
        assert set(captured["ids"]) == {entry.pk for entry in saved_entries}


# ---------------------------------------------------------------------------
# T28 – mixed-form guard on the changelist bulk export action.
# ---------------------------------------------------------------------------


@contextmanager
def _capture_super_export_data(monkeypatch):
    """Patch upstream ``BaseSavedFormDataEntryAdmin.export_data``.

    T27's ``_capture_export_data`` swaps the consumer admin's
    ``export_data`` at the class level, which masks the T28 mixin
    override. Patching one level up (the upstream class) keeps the
    override in the codepath under test: the mixin's ``super()`` call
    lands on this fake instead of the real ``DataExporter``-backed
    method.
    """
    from fobi.contrib.plugins.form_handlers.db_store.admin import (
        BaseSavedFormDataEntryAdmin,
    )

    captured = {"calls": 0, "queryset_ids": []}

    def fake_super_export(self, request, queryset):
        captured["calls"] += 1
        captured["queryset_ids"] = list(queryset.values_list("pk", flat=True))
        response = HttpResponse(b"stub", content_type="text/csv")
        response["Content-Disposition"] = (
            "attachment; filename=db_store_export_data.csv"
        )
        return response

    monkeypatch.setattr(
        BaseSavedFormDataEntryAdmin, "export_data", fake_super_export, raising=True
    )
    yield captured


def _build_request(method, path, user):
    """Hand-built request with messages storage attached."""
    from django.contrib.messages.storage.fallback import FallbackStorage
    from django.test import RequestFactory

    request = getattr(RequestFactory(), method)(path)
    request.user = user
    request.session = {}
    request._messages = FallbackStorage(request)
    return request


@pytest.fixture()
def saved_entries_two_forms(db, admin_user, form_entry, saved_entries):
    """Two saved entries on ``form_entry`` plus one saved entry on a second form."""
    from fobi.contrib.plugins.form_handlers.db_store.models import SavedFormDataEntry
    from fobi.models import FormEntry

    other_form = FormEntry.objects.create(
        user=admin_user, name="Second Form", slug="second-form"
    )
    other_entry = SavedFormDataEntry.objects.create(
        form_entry=other_form,
        user=admin_user,
        saved_data=json.dumps({"q": "v"}),
        form_data_headers=json.dumps({"q": "Q"}),
    )
    return {"primary": saved_entries, "other": other_entry}


class TestMixedFormGuard:
    """Bulk ``export_data`` rejects mixed-form querysets and otherwise delegates."""

    def _registered_admin(self):
        from django.contrib import admin as django_admin
        from fobi.contrib.plugins.form_handlers.db_store.models import (
            SavedFormDataEntry,
        )

        return django_admin.site._registry[SavedFormDataEntry]

    def test_mixed_form_queryset_redirects_and_skips_super(
        self, monkeypatch, admin_user, saved_entries_two_forms
    ):
        from fobi.contrib.plugins.form_handlers.db_store.models import (
            SavedFormDataEntry,
        )

        ids = [
            saved_entries_two_forms["primary"][0].pk,
            saved_entries_two_forms["other"].pk,
        ]
        queryset = SavedFormDataEntry.objects.filter(pk__in=ids)
        request = _build_request("post", "/admin/saved-form-data-entry/", admin_user)

        with _capture_super_export_data(monkeypatch) as captured:
            response = self._registered_admin().export_data(request, queryset)

        assert response.status_code == 302
        assert captured["calls"] == 0
        emitted = [str(m) for m in request._messages]
        assert len(emitted) == 1
        assert "multiple forms" in emitted[0].lower()

    def test_mixed_form_redirect_preserves_query_string(
        self, monkeypatch, admin_user, form_entry, saved_entries_two_forms
    ):
        from fobi.contrib.plugins.form_handlers.db_store.models import (
            SavedFormDataEntry,
        )

        ids = [
            saved_entries_two_forms["primary"][0].pk,
            saved_entries_two_forms["other"].pk,
        ]
        queryset = SavedFormDataEntry.objects.filter(pk__in=ids)
        path = (
            f"/admin/saved-form-data-entry/"
            f"?form_entry__id__exact={form_entry.pk}&q=foo"
        )
        request = _build_request("post", path, admin_user)

        with _capture_super_export_data(monkeypatch):
            response = self._registered_admin().export_data(request, queryset)

        assert response.status_code == 302
        assert f"form_entry__id__exact={form_entry.pk}" in response["Location"]
        assert "q=foo" in response["Location"]

    def test_single_form_queryset_delegates_to_super(
        self, monkeypatch, admin_user, saved_entries
    ):
        from fobi.contrib.plugins.form_handlers.db_store.models import (
            SavedFormDataEntry,
        )

        queryset = SavedFormDataEntry.objects.filter(
            pk__in=[entry.pk for entry in saved_entries]
        )
        request = _build_request("post", "/admin/saved-form-data-entry/", admin_user)

        with _capture_super_export_data(monkeypatch) as captured:
            response = self._registered_admin().export_data(request, queryset)

        assert response.status_code == 200
        assert captured["calls"] == 1
        assert set(captured["queryset_ids"]) == {entry.pk for entry in saved_entries}

    def test_empty_queryset_delegates_to_super(
        self, monkeypatch, admin_user
    ):
        from fobi.contrib.plugins.form_handlers.db_store.models import (
            SavedFormDataEntry,
        )

        queryset = SavedFormDataEntry.objects.none()
        request = _build_request("post", "/admin/saved-form-data-entry/", admin_user)

        with _capture_super_export_data(monkeypatch) as captured:
            response = self._registered_admin().export_data(request, queryset)

        assert response.status_code == 200
        assert captured["calls"] == 1
        assert captured["queryset_ids"] == []

    def test_inline_endpoint_path_unaffected_by_guard(
        self, monkeypatch, admin_client, form_entry, saved_entries
    ):
        """Inline endpoint always passes a single-form queryset, so the guard
        is a no-op there. End-to-end check that hits the override (no
        consumer-class patching that would mask it)."""
        url = reverse(EXPORT_URL_NAME) + f"?form_entry_id={form_entry.pk}"
        with _capture_super_export_data(monkeypatch) as captured:
            response = admin_client.get(url)

        assert response.status_code == 200
        assert captured["calls"] == 1
        assert set(captured["queryset_ids"]) == {entry.pk for entry in saved_entries}
