"""App configuration for unfold_fobi."""

from django.apps import AppConfig


class UnfoldFobiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "unfold_fobi"

    def ready(self):
        # DRF compatibility shim — must run before any fobi import.
        # Re-register fobi admin classes with Unfold ModelAdmin.
        from unfold_fobi import (
            fobi_admin,  # noqa: F401
            fobi_compat,  # noqa: F401
        )

        # Register DRF integration db_store handler.
        try:
            import fobi.contrib.apps.drf_integration.form_handlers.db_store.fobi_integration_form_handlers  # noqa: F401
        except ImportError:
            pass

        # Apply monkey-patches (widgets, owner filtering, popup response).
        from unfold_fobi.patches import apply_all

        apply_all()

        # Connect signal handlers (db_store auto-attach, dedup).
        from unfold_fobi.signals import connect as connect_signals

        connect_signals()
