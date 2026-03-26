"""Reject REST API submissions for inactive forms.

Fobi's ``FobiFormEntryViewSet.update`` accepts PUT requests regardless
of ``active_date_from`` / ``active_date_to``.  This patch wraps the
``update`` method to check ``form_entry.is_active`` before processing
the submission, returning HTTP 403 when the form is outside its active
window.
"""

from django.utils.translation import gettext_lazy as _


def apply():
    """Patch FobiFormEntryViewSet.update for active-date enforcement — idempotent."""
    try:
        from fobi.contrib.apps.drf_integration.views import (
            FobiFormEntryViewSet,
        )
    except ImportError:
        return

    original_update = FobiFormEntryViewSet.update

    if getattr(original_update, "_unfold_active_date_patched", False):
        return

    def update_with_active_check(self, request, *args, **kwargs):
        from rest_framework import status
        from rest_framework.response import Response

        instance = self.get_object()
        if not instance.is_active:
            return Response(
                {"detail": _("This form is not currently accepting submissions.")},
                status=status.HTTP_403_FORBIDDEN,
            )
        return original_update(self, request, *args, **kwargs)

    update_with_active_check._unfold_active_date_patched = True
    FobiFormEntryViewSet.update = update_with_active_check
