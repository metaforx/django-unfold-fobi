"""URL configuration for the unfold_fobi test server."""
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView

import unfold_fobi.views

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
            pattern_name="admin:unfold_fobi_formentryproxy_create"
        ),
        name="fobi.create_form_entry",
    ),
    path(
        "admin/fobi/forms/edit/<int:form_entry_id>/",
        RedirectView.as_view(
            pattern_name="admin:unfold_fobi_formentryproxy_edit"
        ),
        name="fobi.edit_form_entry",
    ),
    # Fobi edit views — must be before admin.site.urls for the same reason.
    re_path(r"^admin/fobi/", include("fobi.urls.class_based.edit")),
    # Admin (last, so its catch_all_view doesn't shadow /admin/fobi/* routes)
    path("admin/", admin.site.urls),
)
