"""Monkey-patches applied to django-fobi at startup.

Each submodule exposes an idempotent ``apply()`` function called from
``UnfoldFobiConfig.ready()``.
"""

from .owner_filtering import apply as apply_owner_filtering
from .popup_response import apply as apply_popup_response
from .widgets import apply as apply_widgets
from .mail_sender import apply as apply_mail_sender


def apply_all():
    """Apply every fobi patch in the correct order."""
    apply_widgets()
    apply_mail_sender()
    apply_owner_filtering()
    apply_popup_response()


__all__ = [
    "apply_all",
    "apply_mail_sender",
    "apply_owner_filtering",
    "apply_popup_response",
    "apply_widgets",
]
