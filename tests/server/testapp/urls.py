"""URL configuration for the unfold_fobi test server."""

from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path


# Non-localised endpoints (no language prefix)
urlpatterns = [
    # Language switching endpoint (must NOT be inside i18n_patterns)
    path("i18n/", include("django.conf.urls.i18n")),
    # DRF integration endpoints
    path("api/", include("fobi.contrib.apps.drf_integration.urls")),
    path("api/", include("unfold_fobi.api.urls")),
    # Public Fobi views and handlers (packaged integration)
    path("fobi/", include("unfold_fobi.urls.public")),
]

# Language-prefixed admin URLs
urlpatterns += i18n_patterns(
    # Fobi edit + legacy compatibility routes from unfold_fobi package.
    # Must be before admin.site.urls so catch_all_view doesn't shadow them.
    path("admin/fobi/", include("unfold_fobi.urls.admin")),
    # Admin (last, so its catch_all_view doesn't shadow /admin/fobi/* routes)
    path("admin/", admin.site.urls),
)
