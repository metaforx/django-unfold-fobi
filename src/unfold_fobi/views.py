"""
Unfold custom views wrapping fobi class-based views.
"""
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from unfold.views import UnfoldModelAdminViewMixin

from fobi.views.class_based import (
    CreateFormEntryView as FobiCreateFormEntryView,
    EditFormEntryView as FobiEditFormEntryView,
)


class FormEntryCreateView(UnfoldModelAdminViewMixin, FobiCreateFormEntryView):
    title = _("Create form")
    permission_required = ("fobi.add_formentry",)


class FormEntryEditView(UnfoldModelAdminViewMixin, FobiEditFormEntryView):
    title = _("Edit form")
    permission_required = ("fobi.change_formentry",)


class FormWizardsDashboardView(UnfoldModelAdminViewMixin, RedirectView):
    title = _("Wizards")
    permission_required = ("fobi.view_formwizardentry",)
    pattern_name = "fobi.form_wizards_dashboard"


class FormEntryImportView(UnfoldModelAdminViewMixin, RedirectView):
    title = _("Import form")
    permission_required = ("fobi.add_formentry",)
    pattern_name = "fobi.import_form_entry"
