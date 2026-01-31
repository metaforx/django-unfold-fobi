"""
Attach the DB store handler to all form entries that don't have it.

Submissions via the REST API are only saved to SavedFormDataEntry when
the form has the db_store handler. Run this so existing/imported forms
start saving submissions.

Usage:
  python manage.py attach_db_store_handler
  python manage.py attach_db_store_handler --form-entry-id=4
"""
from django.core.management.base import BaseCommand
from fobi.models import FormEntry, FormHandlerEntry

DB_STORE_UID = "db_store"


class Command(BaseCommand):
    help = "Attach the DB store handler to form entries so REST API submissions are saved."

    def add_arguments(self, parser):
        parser.add_argument(
            "--form-entry-id",
            type=int,
            default=None,
            help="Only attach to this FormEntry PK. If omitted, attach to all forms.",
        )

    def handle(self, *args, **options):
        form_entry_id = options.get("form_entry_id")
        if form_entry_id is not None:
            try:
                form_entries = [FormEntry.objects.get(pk=form_entry_id)]
            except FormEntry.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f"FormEntry with pk={form_entry_id} does not exist.")
                )
                return
        else:
            form_entries = FormEntry.objects.all()

        added = 0
        for form_entry in form_entries:
            _, created = FormHandlerEntry.objects.get_or_create(
                form_entry=form_entry,
                plugin_uid=DB_STORE_UID,
            )
            if created:
                added += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Attached DB store handler to form: {form_entry.name} (id={form_entry.pk})"
                    )
                )

        if added == 0:
            self.stdout.write(
                "No forms were missing the handler; nothing to do."
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Done. Attached handler to {added} form(s). "
                    "Submissions via REST API will now be saved. View at: "
                    "/admin/fobi_contrib_plugins_form_handlers_db_store/savedformdataentry/"
                )
            )
