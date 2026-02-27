"""T03 – i18n baseline tests.

Verifies that core translated labels and messages exist for custom admin
and view strings used by unfold_fobi.
"""
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
