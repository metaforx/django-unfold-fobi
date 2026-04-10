from django.urls import path

from . import views

urlpatterns = [
    path(
        "altcha-challenge/",
        views.altcha_challenge,
        name="altcha-challenge",
    ),
]
