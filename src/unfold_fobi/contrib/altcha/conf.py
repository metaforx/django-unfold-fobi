"""ALTCHA configuration resolved from Django settings."""

from django.conf import settings


def get_hmac_secret():
    return getattr(settings, "UNFOLD_FOBI_ALTCHA_HMAC_SECRET", None)


def get_max_number():
    return getattr(settings, "UNFOLD_FOBI_ALTCHA_MAX_NUMBER", 100_000)


def get_algorithm():
    return getattr(settings, "UNFOLD_FOBI_ALTCHA_ALGORITHM", "SHA-256")


def get_field_name():
    return getattr(settings, "UNFOLD_FOBI_ALTCHA_FIELD_NAME", "altcha")


def get_cache_alias():
    return getattr(settings, "UNFOLD_FOBI_ALTCHA_CACHE_ALIAS", "default")


def get_challenge_expiry():
    return getattr(settings, "UNFOLD_FOBI_ALTCHA_CHALLENGE_EXPIRY", 300)


def is_enabled():
    """ALTCHA is enabled when the app is installed and a secret is configured."""
    from django.apps import apps

    return (
        apps.is_installed("unfold_fobi.contrib.altcha")
        and get_hmac_secret() is not None
    )
