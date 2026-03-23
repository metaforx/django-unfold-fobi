"""
Unfold custom views — redirect views for admin integration.

DRF API endpoints are in unfold_fobi.api.views.
"""

from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from unfold.views import UnfoldModelAdminViewMixin


class FormWizardsDashboardView(UnfoldModelAdminViewMixin, RedirectView):
    title = _("Wizards")
    permission_required = ("fobi.view_formwizardentry",)
    pattern_name = "fobi.form_wizards_dashboard"


class FormEntryImportView(UnfoldModelAdminViewMixin, RedirectView):
    title = _("Import form")
    permission_required = ("fobi.add_formentry",)
    pattern_name = "fobi.import_form_entry"
