"""JSON import form used by FormEntryProxy changelist action."""

import json

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Fieldset, Layout, Row
from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from unfold.layout import Submit as UnfoldSubmit
from unfold.widgets import UnfoldAdminFileFieldWidget


class ImportFormEntryJsonForm(forms.Form):
    """Upload form for importing form entries from exported JSON payloads."""

    file = forms.FileField(widget=UnfoldAdminFileFieldWidget())

    def __init__(self, *args, **kwargs):
        cancel_url = kwargs.pop(
            "cancel_url",
            reverse("admin:unfold_fobi_formentryproxy_changelist"),
        )
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                None,
                "file",
            ),
            Row(
                Column(
                    HTML(
                        f'<a href="{cancel_url}" class="cursor-pointer border border-base-200 font-medium px-3 py-2 rounded-default transition-all hover:bg-base-50 dark:border-base-700 dark:hover:text-base-200 dark:hover:bg-base-900">Cancel</a>'
                    ),
                    UnfoldSubmit("submit", "Import"),
                    css_class="lg:flex-row lg:gap-2 justify-end",
                ),
                css_class="mt-8 justify-end",
            ),
        )

    def clean_file(self):
        uploaded = self.cleaned_data["file"]
        try:
            payload = json.loads(uploaded.read().decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise forms.ValidationError(
                _("Invalid JSON file: {err}").format(err=exc)
            ) from exc
        except json.JSONDecodeError as exc:
            raise forms.ValidationError(
                _("Invalid JSON file: {err}").format(err=exc)
            ) from exc
        finally:
            uploaded.seek(0)

        if isinstance(payload, dict):
            entries = [payload]
        elif isinstance(payload, list):
            entries = payload
        else:
            raise forms.ValidationError(
                _("Invalid JSON payload: expected an object or an array.")
            )

        if not entries:
            raise forms.ValidationError(
                _("Invalid JSON payload: expected at least one form entry.")
            )
        if not all(isinstance(item, dict) for item in entries):
            raise forms.ValidationError(
                _("Invalid JSON payload: array items must be form entry objects.")
            )

        self.cleaned_data["entries_payload"] = entries
        return uploaded
