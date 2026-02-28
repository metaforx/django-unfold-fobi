"""Smoke tests for unfold_fobi test infrastructure.

Verifies that:
- Django settings load correctly
- unfold_fobi app is configured
- Admin URLs resolve
- Admin views respond for authenticated users
- Seed fixtures create valid data
"""
import pytest
from django.apps import apps
from django.test import RequestFactory
from django.urls import NoReverseMatch, reverse


class TestDjangoSetup:
    """Verify the Django test project is wired correctly."""

    def test_unfold_fobi_app_installed(self):
        assert apps.is_installed("unfold_fobi")

    def test_fobi_app_installed(self):
        assert apps.is_installed("fobi")

    def test_unfold_app_installed(self):
        assert apps.is_installed("unfold")

    def test_fobi_theme_is_unfold(self, settings):
        assert settings.FOBI_THEME == "unfold"

    def test_crispy_pack_is_unfold(self, settings):
        assert settings.CRISPY_TEMPLATE_PACK == "unfold_crispy"


class TestAdminURLs:
    """Verify admin URL patterns resolve."""

    def test_changelist_url(self):
        url = reverse("admin:unfold_fobi_formentryproxy_changelist")
        assert url == "/en/admin/unfold_fobi/formentryproxy/"

    def test_add_url(self):
        url = reverse("admin:unfold_fobi_formentryproxy_add")
        assert url == "/en/admin/unfold_fobi/formentryproxy/add/"

    def test_change_url(self):
        """T10: native change view URL resolves."""
        url = reverse("admin:unfold_fobi_formentryproxy_change", args=[1])
        assert url == "/en/admin/unfold_fobi/formentryproxy/1/change/"


class TestAdminViews:
    """Verify admin views respond correctly."""

    def test_changelist_accessible(self, admin_client):
        url = reverse("admin:unfold_fobi_formentryproxy_changelist")
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_add_view_accessible(self, admin_client):
        url = reverse("admin:unfold_fobi_formentryproxy_add")
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_change_view_accessible(self, admin_client, form_entry):
        """T10: native change view renders 200."""
        url = reverse(
            "admin:unfold_fobi_formentryproxy_change", args=[form_entry.pk]
        )
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_unauthenticated_redirects(self, client):
        url = reverse("admin:unfold_fobi_formentryproxy_changelist")
        response = client.get(url)
        assert response.status_code == 302


class TestSeedData:
    """Verify seed fixtures produce valid test data."""

    def test_form_entry_exists(self, form_entry):
        assert form_entry.pk is not None
        assert form_entry.name == "Test Form"
        assert form_entry.slug == "test-form"

    def test_form_entry_has_element(self, form_entry):
        assert form_entry.formelemententry_set.count() == 1
        element = form_entry.formelemententry_set.first()
        assert element.plugin_uid == "text"

    def test_form_entry_has_handler(self, form_entry):
        from fobi.models import FormHandlerEntry

        assert FormHandlerEntry.objects.filter(
            form_entry=form_entry, plugin_uid="db_store"
        ).exists()
