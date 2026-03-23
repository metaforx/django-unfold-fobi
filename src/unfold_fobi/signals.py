"""Signal handlers for unfold_fobi.

Auto-attaches a db_store handler to every new FormEntry and deduplicates
when JSON import creates a second db_store row.
"""

from django.db.models.signals import post_save


def ensure_db_store_handler(sender, instance, **kwargs):
    """Attach a db_store handler to every saved FormEntry."""
    from fobi.models import FormHandlerEntry

    FormHandlerEntry.objects.get_or_create(
        form_entry=instance,
        plugin_uid="db_store",
    )


def deduplicate_db_store_handler(sender, instance, **kwargs):
    """Keep only one db_store handler per form entry.

    JSON import can create a form (triggering FormEntry post_save auto-attach)
    and then import handlers including db_store.  Keep the latest saved row
    and delete older duplicates.
    """
    if instance.plugin_uid != "db_store":
        return
    from fobi.models import FormHandlerEntry

    FormHandlerEntry.objects.filter(
        form_entry=instance.form_entry,
        plugin_uid="db_store",
    ).exclude(pk=instance.pk).delete()


def connect():
    """Register signal handlers — safe to call multiple times."""
    from fobi.models import FormEntry, FormHandlerEntry

    post_save.connect(
        ensure_db_store_handler,
        sender=FormEntry,
        dispatch_uid="unfold_fobi.ensure_db_store_handler",
    )
    post_save.connect(
        deduplicate_db_store_handler,
        sender=FormHandlerEntry,
        dispatch_uid="unfold_fobi.deduplicate_db_store_handler",
    )
