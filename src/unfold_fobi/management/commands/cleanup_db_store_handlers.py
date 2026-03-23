"""
Remove duplicate db_store handlers so only one remains per form.

Usage:
  python manage.py cleanup_db_store_handlers
  python manage.py cleanup_db_store_handlers --dry-run
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from fobi.models import FormHandlerEntry

DB_STORE_UID = "db_store"


class Command(BaseCommand):
    help = "Remove duplicate db_store handlers, keeping the oldest per form."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without deleting.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        duplicates = (
            FormHandlerEntry.objects.filter(plugin_uid=DB_STORE_UID)
            .values("form_entry_id")
            .annotate(count=Count("id"))
            .filter(count__gt=1)
        )

        total_deleted = 0
        for item in duplicates:
            form_entry_id = item["form_entry_id"]
            handlers = FormHandlerEntry.objects.filter(
                form_entry_id=form_entry_id, plugin_uid=DB_STORE_UID
            ).order_by("id")
            keep = handlers.first()
            to_delete = handlers.exclude(id=keep.id)
            delete_count = to_delete.count()
            total_deleted += delete_count

            if dry_run:
                self.stdout.write(
                    f"Form {form_entry_id}: keep {keep.id}, delete {delete_count}"
                )
            else:
                to_delete.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Form {form_entry_id}: kept {keep.id}, deleted {delete_count}"
                    )
                )

        if total_deleted == 0:
            self.stdout.write("No duplicate db_store handlers found.")
        elif dry_run:
            self.stdout.write(f"Dry run complete. Would delete {total_deleted} rows.")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Done. Deleted {total_deleted} duplicate handlers.")
            )
