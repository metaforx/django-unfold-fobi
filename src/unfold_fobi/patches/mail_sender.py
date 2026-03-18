"""Patch the Fobi mail_sender handler to drop the unused recipient name field."""

from django.template import TemplateDoesNotExist


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


def apply():
    """Remove the unused recipient-name field from the mail_sender handler."""
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

    MailSenderForm._unfold_mail_sender_patched = True
