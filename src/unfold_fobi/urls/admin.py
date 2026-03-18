"""Admin/Fobi compatibility routes for unfold_fobi integrations."""

from django.shortcuts import redirect
from django.urls import include, path, reverse
from django.views.generic import RedirectView


def _edit_form_entry_redirect(request, form_entry_id):
    """Map legacy fobi.edit_form_entry to native Unfold admin change URL."""
    return redirect(
        reverse("admin:unfold_fobi_formentryproxy_change", args=[form_entry_id])
    )


urlpatterns = [
    path(
        "forms/create/",
        RedirectView.as_view(pattern_name="admin:unfold_fobi_formentryproxy_add"),
        name="fobi.create_form_entry",
    ),
    path(
        "forms/edit/<int:form_entry_id>/",
        _edit_form_entry_redirect,
        name="fobi.edit_form_entry",
    ),
    path("", include("fobi.urls.class_based.edit")),
]

