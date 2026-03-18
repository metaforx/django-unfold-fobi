"""Patch the Fobi mail_sender handler to use a constrained email-field select."""

import json

from django import forms
from django.forms.utils import ErrorList
from django.template import TemplateDoesNotExist
from django.utils.translation import gettext_lazy as _


def _remove_form_field(form_class, field_name):
    """Remove a declarative form field from future form instances."""
    for attr_name in ("base_fields", "declared_fields"):
        fields = getattr(form_class, attr_name, None)
        if fields and field_name in fields:
            fields.pop(field_name, None)

    field_order = getattr(form_class, "field_order", None)
    if field_order:
        form_class.field_order = [
            name for name in field_order if name != field_name
        ]


def _get_form_entry_from_request(request):
    """Resolve the target FormEntry from the current add/edit handler request."""
    if not request:
        return None

    resolver_match = getattr(request, "resolver_match", None)
    kwargs = getattr(resolver_match, "kwargs", {}) or {}

    try:
        from fobi.models import FormEntry, FormHandlerEntry
    except ImportError:
        return None

    form_entry_id = kwargs.get("form_entry_id")
    if form_entry_id:
        return FormEntry._default_manager.filter(pk=form_entry_id).first()

    form_handler_entry_id = kwargs.get("form_handler_entry_id")
    if form_handler_entry_id:
        handler_entry = (
            FormHandlerEntry._default_manager.select_related("form_entry")
            .filter(pk=form_handler_entry_id)
            .first()
        )
        if handler_entry:
            return handler_entry.form_entry

    return None


def _get_email_field_choices(request):
    """Build select choices from email-type form elements only."""
    form_entry = _get_form_entry_from_request(request)
    if not form_entry:
        return []

    choices = []
    elements = form_entry.formelemententry_set.order_by("position", "pk")
    for element in elements:
        if element.plugin_uid != "email":
            continue

        try:
            plugin_data = json.loads(element.plugin_data or "{}")
        except (TypeError, ValueError):
            plugin_data = {}

        field_name = plugin_data.get("name")
        if not field_name:
            continue

        field_label = plugin_data.get("label") or field_name
        if field_label == field_name:
            display_label = field_name
        else:
            display_label = f"{field_label} ({field_name})"
        choices.append((field_name, display_label))

    return choices


def _set_email_field_dropdown(form, request):
    """Replace the free-text email-field selector with a validated dropdown."""
    if not form:
        return form

    original_field = form.fields.get("form_field_name_to_email")
    if not original_field:
        return form

    choices = _get_email_field_choices(request)
    if choices:
        select_choices = [("", _("Choose email field")), *choices]
        help_text = _("Select one of the email fields defined on this form.")
    else:
        select_choices = [
            (
                "",
                _("No email fields are available on this form. Add an email field first."),
            )
        ]
        help_text = _("No email fields are available on this form. Add an email field first.")

    form.fields["form_field_name_to_email"] = forms.ChoiceField(
        label=original_field.label,
        required=True,
        help_text=help_text,
        choices=select_choices,
        widget=forms.Select(attrs=original_field.widget.attrs),
    )

    initial = form.initial.get("form_field_name_to_email")
    if initial and all(value != initial for value, _label in choices):
        form.initial["form_field_name_to_email"] = ""

    return form


def _build_plugin_data_repr(render_to_string, safe_text):
    """Return a plugin_data_repr implementation without the legacy to_name."""

    def plugin_data_repr(self):
        context = {
            "form_field_name_to_email": safe_text(
                self.data.form_field_name_to_email
            ),
            "subject": safe_text(self.data.subject),
        }
        try:
            return render_to_string("mail_sender/plugin_data_repr.html", context)
        except TemplateDoesNotExist:
            return (
                "<p><strong>To</strong>: Form field name to email: "
                f"&quot;{context['form_field_name_to_email']}&quot;</p>"
                f"<p><strong>Subject</strong>: {context['subject']}</p>"
            )

    return plugin_data_repr


def _patch_form_initialisers(plugin_class):
    """Patch plugin form initialisers so the email selector becomes dynamic."""
    if getattr(plugin_class, "_unfold_mail_sender_form_patched", False):
        return

    original_create = plugin_class.get_initialised_create_form
    original_edit = plugin_class.get_initialised_edit_form

    def patched_create(self, data=None, files=None, initial_data=None):
        form = original_create(
            self,
            data=data,
            files=files,
            initial_data=initial_data,
        )
        return _set_email_field_dropdown(form, getattr(self, "request", None))

    def patched_edit(
        self,
        data=None,
        files=None,
        auto_id="id_%s",
        prefix=None,
        initial=None,
        error_class=ErrorList,
        label_suffix=":",
        empty_permitted=False,
        instance=None,
    ):
        form = original_edit(
            self,
            data=data,
            files=files,
            auto_id=auto_id,
            prefix=prefix,
            initial=initial,
            error_class=error_class,
            label_suffix=label_suffix,
            empty_permitted=empty_permitted,
            instance=instance,
        )
        return _set_email_field_dropdown(form, getattr(self, "request", None))

    plugin_class.get_initialised_create_form = patched_create
    plugin_class.get_initialised_edit_form = patched_edit
    plugin_class._unfold_mail_sender_form_patched = True


def apply():
    """Patch the mail_sender handler form to remove dead fields and constrain email selection."""
    try:
        from fobi.contrib.plugins.form_handlers.mail_sender import base as mail_sender_base
        from fobi.contrib.plugins.form_handlers.mail_sender.forms import MailSenderForm
    except ImportError:
        return

    if getattr(MailSenderForm, "_unfold_mail_sender_patched", False):
        return

    MailSenderForm.plugin_data_fields = [
        (field_name, default_value)
        for field_name, default_value in MailSenderForm.plugin_data_fields
        if field_name != "to_name"
    ]
    _remove_form_field(MailSenderForm, "to_name")

    plugin_data_repr = _build_plugin_data_repr(
        mail_sender_base.render_to_string,
        mail_sender_base.safe_text,
    )
    mail_sender_base.MailSenderHandlerPlugin.plugin_data_repr = plugin_data_repr
    mail_sender_base.MailSenderWizardHandlerPlugin.plugin_data_repr = (
        plugin_data_repr
    )

    _patch_form_initialisers(mail_sender_base.MailSenderHandlerPlugin)
    _patch_form_initialisers(mail_sender_base.MailSenderWizardHandlerPlugin)

    MailSenderForm._unfold_mail_sender_patched = True
