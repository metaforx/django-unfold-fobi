"""Reusable helpers for site binding CRUD and propagation."""

from .models import FobiFormSiteBinding


def ensure_binding(form_entry):
    """Ensure a FobiFormSiteBinding exists for the given form entry.

    Returns the (binding, created) tuple.
    """
    return FobiFormSiteBinding.objects.get_or_create(form_entry=form_entry)


def get_form_sites(form_entry):
    """Return the Site queryset for the given form entry, or empty qs."""
    from django.contrib.sites.models import Site

    try:
        return form_entry.site_binding.sites.all()
    except FobiFormSiteBinding.DoesNotExist:
        return Site.objects.none()


def copy_site_bindings(source_entry, target_entry):
    """Copy site bindings from source to target form entry.

    Creates a binding for the target if it doesn't exist.
    Returns the target binding.
    """
    target_binding, _ = FobiFormSiteBinding.objects.get_or_create(
        form_entry=target_entry
    )
    try:
        source_site_ids = list(
            source_entry.site_binding.sites.values_list("id", flat=True)
        )
    except FobiFormSiteBinding.DoesNotExist:
        source_site_ids = []
    if source_site_ids:
        target_binding.sites.set(source_site_ids)
    return target_binding
