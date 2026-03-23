"""Public Fobi routes for unfold_fobi integrations."""

from django.urls import include, path

urlpatterns = [
    path("", include("fobi.urls.class_based.view")),
    path("", include("fobi.contrib.plugins.form_handlers.db_store.urls")),
]

