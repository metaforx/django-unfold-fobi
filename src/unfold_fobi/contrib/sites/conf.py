"""Configuration helpers for the optional Sites integration."""

from django.contrib.sites.models import Site


def default_sites_for_user(user):
    """Default implementation: superuser sees all sites, others see none.

    Projects should provide their own implementation via the
    ``UNFOLD_FOBI_SITES_FOR_USER`` setting to map users to sites
    based on group membership, roles, or other project-specific logic.
    """
    if user.is_superuser:
        return Site.objects.all()
    return Site.objects.none()


def get_sites_for_user_func():
    """Resolve the ``sites_for_user`` callable from settings or return the default."""
    from django.conf import settings
    from django.utils.module_loading import import_string

    path = getattr(settings, "UNFOLD_FOBI_SITES_FOR_USER", None)
    if path:
        return import_string(path)
    return default_sites_for_user
