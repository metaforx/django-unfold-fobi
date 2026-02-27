from django.contrib import admin
from django.utils.translation import gettext_lazy as _


FOBI_TITLES = {
    "fobi.dashboard": _("Forms"),
    "fobi.create_form_entry": _("Create form"),
    "fobi.edit_form_entry": _("Edit form"),
    "fobi.import_form_entry": _("Import form"),
    "fobi.create_form_wizard_entry": _("Create wizard"),
    "fobi.edit_form_wizard_entry": _("Edit wizard"),
    "fobi.form_wizards_dashboard": _("Wizards"),
    "fobi.import_form_wizard_entry": _("Import wizard"),
    "fobi.export_form_entry": _("Export form"),
    "fobi.export_form_wizard_entry": _("Export wizard"),
}


def admin_site(request):
    """
    Inject Unfold admin context (logo, sidebar state, etc.) into Fobi templates
    and set a sensible title so the header shows breadcrumbs instead of Welcome.
    """
    context = admin.site.each_context(request)
    # Unfold only renders the navigation header when `branding` is set.
    # Fall back to the admin site header (or a default string) so the icon renders.
    default_brand = admin.site.site_header or _("Django administration")
    context.setdefault("site_header", default_brand)
    context.setdefault("branding", default_brand)
    # Ensure a symbol exists so the default settings icon renders when no logo/icon.
    context.setdefault("site_symbol", "settings")

    match = getattr(request, "resolver_match", None)
    if match:
        view_name = match.view_name or ""
        content_title = FOBI_TITLES.get(view_name)
        if content_title:
            context.setdefault("content_title", content_title)

    return context
