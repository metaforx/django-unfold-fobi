"""
Add test form submissions via the Fobi REST API.

Submits form data to PUT /api/fobi-form-entry/{slug}/ so that entries
appear in the admin (db_store SavedFormDataEntry) for the given form.

Usage:
  python manage.py add_rest_api_form_data
  python manage.py add_rest_api_form_data --form-entry-id=4 --count=10
  python manage.py add_rest_api_form_data --base-url=http://localhost:8080
"""
import json
import urllib.error
import urllib.request
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from fobi.models import FormEntry


def _sample_value_for_field(field_info, index):
    """Return a valid sample value for the field type (for submission index 0..count-1)."""
    name = field_info.get("name", "")
    field_type = field_info.get("type", "CharField")
    required = field_info.get("required", False)

    if field_type == "EmailField":
        return f"testuser{index + 1}@example.com"
    if field_type == "IntegerField":
        min_v = field_info.get("min_value")
        max_v = field_info.get("max_value")
        val = 20 + index
        if min_v is not None and val < min_v:
            val = min_v
        if max_v is not None and val > max_v:
            val = max_v
        return val
    if field_type == "BooleanField":
        return (index % 2) == 0
    if field_type == "DateField":
        d = date(1990, 1, 1) + timedelta(days=index * 100)
        return d.isoformat()
    if field_type == "NullBooleanField":
        return (index % 3) == 0  # True/False/None pattern
    if field_type == "ChoiceField" or field_type == "TypedChoiceField":
        choices = field_info.get("choices", [])
        if isinstance(choices, list) and choices:
            # choices can be [{"value": "x", "label": "y"}, ...]
            first = choices[0]
            if isinstance(first, dict) and "value" in first:
                values = [c["value"] for c in choices]
            else:
                values = list(choices) if not isinstance(choices[0], (list, tuple)) else [c[0] for c in choices]
            return values[index % len(values)] if values else ""
        return "USA"
    if field_type in ("TextField", "TextareaField", "CharField"):
        return f"Sample value {index + 1} for {name}"
    return f"value_{index + 1}"


def _build_payload(fields, index):
    """Build one JSON payload for the form from field definitions."""
    return {f["name"]: _sample_value_for_field(f, index) for f in fields}


def _get_form_fields(base_url, slug):
    """GET /api/fobi-form-fields/{slug}/ and return parsed JSON."""
    url = f"{base_url.rstrip('/')}/api/fobi-form-fields/{slug}/"
    req = urllib.request.Request(url, method="GET", headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def _put_form_submission(base_url, slug, payload):
    """PUT /api/fobi-form-entry/{slug}/ with JSON body. Returns (success, message)."""
    url = f"{base_url.rstrip('/')}/api/fobi-form-entry/{slug}/"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="PUT",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return True, resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return False, f"HTTP {e.code}: {body[:200]}"
    except urllib.error.URLError as e:
        return False, str(e.reason)


class Command(BaseCommand):
    help = "Add test form submissions via the Fobi REST API (PUT /api/fobi-form-entry/{slug}/)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--form-entry-id",
            type=int,
            default=4,
            help="FormEntry PK (admin edit URL uses this). Default: 4.",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Number of test submissions to send. Default: 10.",
        )
        parser.add_argument(
            "--base-url",
            type=str,
            default="http://localhost:8080",
            help="Base URL of the running app. Default: http://localhost:8080",
        )

    def handle(self, *args, **options):
        form_entry_id = options["form_entry_id"]
        count = options["count"]
        base_url = options["base_url"].rstrip("/")

        try:
            form_entry = FormEntry.objects.get(pk=form_entry_id)
        except FormEntry.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"FormEntry with pk={form_entry_id} does not exist."))
            return

        slug = form_entry.slug
        self.stdout.write(f"Form: {form_entry.name} (slug={slug}, id={form_entry_id})")
        self.stdout.write(f"Fetching fields from {base_url}/api/fobi-form-fields/{slug}/ ...")

        try:
            form_structure = _get_form_fields(base_url, slug)
        except urllib.error.URLError as e:
            self.stderr.write(
                self.style.ERROR(
                    f"Cannot reach {base_url}. Is the server running? {e.reason}"
                )
            )
            return
        except urllib.error.HTTPError as e:
            self.stderr.write(self.style.ERROR(f"GET form fields failed: {e.code} {e.reason}"))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to get form fields: {e}"))
            return

        fields = form_structure.get("fields", [])
        if not fields:
            self.stdout.write(self.style.WARNING("No fields returned; submitting empty payloads."))

        ok = 0
        for i in range(count):
            payload = _build_payload(fields, i)
            success, msg = _put_form_submission(base_url, slug, payload)
            if success:
                ok += 1
                self.stdout.write(self.style.SUCCESS(f"  [{i + 1}/{count}] submitted"))
            else:
                self.stdout.write(self.style.ERROR(f"  [{i + 1}/{count}] failed: {msg}"))

        self.stdout.write(
            self.style.SUCCESS(f"Done: {ok}/{count} submissions sent. Check form entries in admin.")
        )
