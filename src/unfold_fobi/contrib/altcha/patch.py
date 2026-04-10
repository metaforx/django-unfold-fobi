"""Patch FobiFormEntryViewSet.update to require ALTCHA verification."""

from . import conf


def apply():
    """Patch fobi DRF update for ALTCHA validation — idempotent."""
    if not conf.is_enabled():
        return

    try:
        from fobi.contrib.apps.drf_integration.views import (
            FobiFormEntryViewSet,
        )
    except ImportError:
        return

    original_update = FobiFormEntryViewSet.update

    if getattr(original_update, "_unfold_altcha_patched", False):
        return

    def update_with_altcha(self, request, *args, **kwargs):
        # Re-check at runtime so tests/settings changes are respected
        if not conf.is_enabled():
            return original_update(self, request, *args, **kwargs)

        # Only enforce ALTCHA on public forms
        instance = self.get_object()
        if not instance.is_public:
            return original_update(self, request, *args, **kwargs)

        from rest_framework.response import Response

        from .challenge import verify_payload

        field_name = conf.get_field_name()
        payload = request.data.get(field_name)

        is_valid, error = verify_payload(payload)
        if not is_valid:
            return Response({"detail": error}, status=400)

        # Remove ALTCHA field before Fobi processing
        if hasattr(request.data, "_mutable"):
            request.data._mutable = True
        request.data.pop(field_name, None)

        return original_update(self, request, *args, **kwargs)

    update_with_altcha._unfold_altcha_patched = True
    FobiFormEntryViewSet.update = update_with_altcha
