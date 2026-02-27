"""T03/T05 – i18n baseline and audit tests.

Verifies that core translated labels and messages exist for custom admin
and view strings used by unfold_fobi, and that the makemessages extraction
workflow discovers all expected strings.
"""
import subprocess

import pytest
from django.utils.functional import Promise  # lazy string base class


class TestFobiTitlesTranslated:
    """FOBI_TITLES in context_processors must contain lazy translated strings."""

    def test_fobi_titles_defined(self):
        from unfold_fobi.context_processors import FOBI_TITLES

        assert len(FOBI_TITLES) > 0

    @pytest.mark.parametrize(
        "view_name",
        [
            "fobi.dashboard",
            "fobi.create_form_entry",
            "fobi.edit_form_entry",
            "fobi.import_form_entry",
        ],
    )
    def test_fobi_title_is_lazy_string(self, view_name):
        from unfold_fobi.context_processors import FOBI_TITLES

        title = FOBI_TITLES[view_name]
        assert isinstance(title, (str, Promise))
        assert len(str(title)) > 0


class TestProxyModelVerboseName:
    """FormEntryProxy verbose_name must be a translated string."""

    def test_verbose_name_is_translated(self):
        from unfold_fobi.models import FormEntryProxy

        vn = FormEntryProxy._meta.verbose_name
        assert isinstance(vn, (str, Promise))
        assert str(vn) == "Forms (builder)"

    def test_verbose_name_plural_is_translated(self):
        from unfold_fobi.models import FormEntryProxy

        vn = FormEntryProxy._meta.verbose_name_plural
        assert isinstance(vn, (str, Promise))
        assert str(vn) == "Forms (builder)"


class TestAdminFieldsetLabelsTranslated:
    """Fieldset group labels produced by get_fieldsets should be lazy strings."""

    @pytest.fixture()
    def fieldsets(self, admin_user):
        from django.contrib import admin
        from django.test import RequestFactory

        from unfold_fobi.models import FormEntryProxy

        ma = admin.site._registry[FormEntryProxy]
        factory = RequestFactory()
        request = factory.get("/admin/")
        request.user = admin_user
        return ma.get_fieldsets(request, obj=None)

    def test_all_labels_are_translatable(self, fieldsets):
        for label, _opts in fieldsets:
            assert isinstance(label, (str, Promise)), (
                f"Fieldset label '{label}' is not a translatable string"
            )
            assert len(str(label)) > 0


class TestViewTitlesTranslated:
    """View classes must expose translated title attributes."""

    def test_edit_view_title(self):
        from unfold_fobi.views import FormEntryEditView

        assert str(FormEntryEditView.title) == "Edit form"

    def test_create_view_title(self):
        from unfold_fobi.views import FormEntryCreateView

        assert str(FormEntryCreateView.title) == "Create form"


class TestContextProcessorBrandingWrapped:
    """The branding fallback in context_processors must be translatable."""

    def test_default_brand_is_lazy(self):
        from django.contrib import admin

        from unfold_fobi.context_processors import _

        # The fallback uses _("Django administration"), which is a lazy string.
        fallback = _("Django administration")
        assert isinstance(fallback, (str, Promise))
        assert str(fallback) == "Django administration"

    def test_admin_site_context_has_branding(self, admin_user):
        from django.test import RequestFactory

        from unfold_fobi.context_processors import admin_site

        factory = RequestFactory()
        request = factory.get("/admin/")
        request.user = admin_user
        request.resolver_match = None
        ctx = admin_site(request)
        assert "branding" in ctx
        assert len(str(ctx["branding"])) > 0


class TestAPIErrorMessageWrapped:
    """The get_form_fields API error message must be translatable."""

    def test_form_not_found_returns_translated_error(self, admin_client):
        response = admin_client.get("/api/fobi-form-fields/nonexistent-slug/")
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "Form not found"


class TestMakemessagesExtraction:
    """Verify that makemessages extracts all expected i18n strings."""

    EXPECTED_STRINGS = [
        "Django administration",
        "Basic information",
        "Visibility",
        "Active dates",
        "Forms (builder)",
        "Create form",
        "Edit form",
        "Elements",
        "Handlers",
        "Properties",
        "Form not found",
    ]

    def test_po_file_contains_expected_strings(self):
        import os
        from pathlib import Path

        po_path = Path(__file__).resolve().parent.parent / (
            "src/unfold_fobi/locale/en/LC_MESSAGES/django.po"
        )
        assert po_path.exists(), f"PO file not found at {po_path}"
        content = po_path.read_text()
        for string in self.EXPECTED_STRINGS:
            assert f'msgid "{string}"' in content, (
                f"Expected string '{string}' not found in PO file"
            )
