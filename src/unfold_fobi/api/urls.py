"""URL configuration for unfold_fobi DRF API endpoints."""

from django.urls import path

from . import views

urlpatterns = [
    path(
        "fobi-form-fields/<str:slug>/",
        views.get_form_fields,
        name="fobi-form-fields",
    ),
]
