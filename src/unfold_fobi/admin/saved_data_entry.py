import json

from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


class SavedFormDataEntryAdminIntegrationMixin:
    """
    - Staff users get readonly view access without explicit permission assignment.
    - Add is disabled for everyone (entries are created via fobi form submission only).
    - Only superusers can change or delete entries.
    - Detail view shows submitted data (JSON) as HTML table instead of raw fields.
    """

    list_display = ("form_entry", "user", "pretty_saved_data_short", "created")
    list_filter = ("form_entry", "user")
    search_fields = ("form_entry__name", "saved_data")
    readonly_fields = ("created", "pretty_saved_data_display")

    def get_readonly_fields(self, request, obj=None):
        """Non-superusers see everything readonly. Superusers can edit model fields."""
        ro = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            ro.extend(["form_entry", "user"])
        return ro

    fieldsets = (
        (None, {"fields": ("form_entry", "user", "created")}),
        (
            _("Submitted data"),
            {"fields": ("pretty_saved_data_display",)},
        ),
    )

    # --- Permissions ---
    def has_add_permission(self, request):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    # --- Pretty rendering ---
    @staticmethod
    def _parse_json_field(raw):
        """Parse a JSON string or dict, returning a dict."""
        if not raw:
            return {}
        if isinstance(raw, dict):
            return raw
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}
        if not isinstance(data, dict):
            return {}
        return data

    @staticmethod
    def _format_value(value):
        """Format a saved value for display."""
        if value in (None, ""):
            return "-"
        if isinstance(value, list):
            return ", ".join(str(v) for v in value)
        if isinstance(value, dict):
            formatted = json.dumps(value, indent=2, ensure_ascii=False, default=str)
            return mark_safe(f"<pre>{formatted}</pre>")
        return str(value)

    @admin.display(description="")
    def pretty_saved_data_display(self, obj):
        """Render each submitted field as a table row via template."""
        data = self._parse_json_field(obj.saved_data)
        headers = self._parse_json_field(obj.form_data_headers)
        if not data:
            return "-"
        items = [
            {
                "label": headers.get(key, key),
                "value": self._format_value(value),
            }
            for key, value in data.items()
        ]
        html = render_to_string(
            "admin/unfold_fobi/saved_data_display.html", {"data": items}
        )
        return mark_safe(html)

    @admin.display(description=_("Data"))
    def pretty_saved_data_short(self, obj):
        """Truncated preview for list_display."""
        data = self._parse_json_field(obj.saved_data)
        headers = self._parse_json_field(obj.form_data_headers)
        if not data:
            return "-"
        parts = [f"{headers.get(k, k)}: {v}" for k, v in data.items()]
        flat = " | ".join(parts)
        return flat[:120] + ("…" if len(flat) > 120 else "")
