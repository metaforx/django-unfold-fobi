"""T24: django CMS plugin for site-aware Fobi form reference.

Since django CMS is not installed in the test environment, these tests
verify the non-CMS aspects: FK target, import safety, queryset filtering
logic, and base package isolation.
"""

import pytest


class TestBasePackageIsolation:
    """Base unfold_fobi must work without the djangocms contrib installed."""

    def test_base_package_has_no_cms_dependency(self):
        """No top-level CMS import in base unfold_fobi package."""
        import pathlib

        base_pkg = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "unfold_fobi"
        violations = [
            f"{py.relative_to(base_pkg)}"
            for py in base_pkg.rglob("*.py")
            if "contrib" not in py.parts
            and any(line.startswith(("from cms.", "import cms")) for line in py.read_text().splitlines())
        ]
        assert not violations, f"CMS imports in base package: {violations}"

    def test_admin_changelist_works_without_cms(self, admin_client):
        from django.urls import reverse

        url = reverse("admin:unfold_fobi_formentryproxy_changelist")
        response = admin_client.get(url)
        assert response.status_code == 200


class TestPluginModelDefinition:
    """Verify the plugin model's FK targets the concrete FormEntry."""

    def test_model_fk_targets_formentry(self):
        """FobiFormPlugin.form_entry FK must point to fobi.FormEntry (concrete)."""
        try:
            from unfold_fobi.contrib.cms.models import FobiFormPluginModel
        except ImportError:
            pytest.skip("django CMS not installed")

        fk = FobiFormPluginModel._meta.get_field("form_entry")
        assert fk.related_model._meta.app_label == "fobi"
        assert fk.related_model._meta.model_name == "formentry"

    def test_model_fk_uses_protect(self):
        """FK should use PROTECT to prevent accidental form deletion."""
        try:
            from unfold_fobi.contrib.cms.models import FobiFormPluginModel
        except ImportError:
            pytest.skip("django CMS not installed")

        from django.db import models

        fk = FobiFormPluginModel._meta.get_field("form_entry")
        assert fk.remote_field.on_delete is models.PROTECT


class TestQuerysetFilteringLogic:
    """Test _get_form_queryset without a live CMS, using the function directly."""

    def test_without_sites_returns_all_forms(self, settings, form_entry):
        """When contrib.sites is not in INSTALLED_APPS, all forms returned."""
        try:
            from unfold_fobi.contrib.cms.cms_plugins import _get_form_queryset
        except ImportError:
            pytest.skip("django CMS not installed")

        # Remove sites contrib to test base behavior
        apps = list(settings.INSTALLED_APPS)
        if "unfold_fobi.contrib.sites" in apps:
            apps.remove("unfold_fobi.contrib.sites")
            settings.INSTALLED_APPS = apps

        from django.test import RequestFactory
        from django.contrib.auth.models import User

        request = RequestFactory().get("/")
        request.user = User(is_superuser=True)

        qs = _get_form_queryset(request)
        assert form_entry.pk in qs.values_list("pk", flat=True)
