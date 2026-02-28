"""URL configuration for the unfold_fobi test server."""
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path, re_path, reverse
from django.views.generic import RedirectView

import unfold_fobi.views


def _edit_form_entry_redirect(request, form_entry_id):
    """Map fobi.edit_form_entry (form_entry_id kwarg) to native admin change URL."""
    return redirect(reverse("admin:unfold_fobi_formentryproxy_change", args=[form_entry_id]))

# Non-localised endpoints (no language prefix)
urlpatterns = [
    # Language switching endpoint (must NOT be inside i18n_patterns)
    path("i18n/", include("django.conf.urls.i18n")),
    # DRF integration endpoints
    path("api/", include("fobi.contrib.apps.drf_integration.urls")),
    path(
        "api/fobi-form-fields/<str:slug>/",
        unfold_fobi.views.get_form_fields,
        name="fobi-form-fields",
    ),
    # Public Fobi views and handlers
    re_path(r"^fobi/", include("fobi.urls.class_based.view")),
    re_path(
        r"^fobi/",
        include("fobi.contrib.plugins.form_handlers.db_store.urls"),
    ),
]

# Language-prefixed admin URLs
urlpatterns += i18n_patterns(
    # Redirect legacy Fobi admin routes to the Unfold admin views.
    # These must come before admin.site.urls so they are not swallowed
    # by the Django admin catch_all_view.
    path(
        "admin/fobi/forms/create/",
        RedirectView.as_view(
            pattern_name="admin:unfold_fobi_formentryproxy_add"
        ),
        name="fobi.create_form_entry",
    ),
    path(
        "admin/fobi/forms/edit/<int:form_entry_id>/",
        _edit_form_entry_redirect,
        name="fobi.edit_form_entry",
    ),
    # Fobi edit views — must be before admin.site.urls for the same reason.
    re_path(r"^admin/fobi/", include("fobi.urls.class_based.edit")),
    # Admin (last, so its catch_all_view doesn't shadow /admin/fobi/* routes)
    path("admin/", admin.site.urls),
)
