"""T13 – Unfold actions, tab-scoped add controls, handler modal fixes.

Verifies:
- Import JSON changelist action is wired and functional.
- "Add element" button is scoped to elements tab only (Alpine x-show).
- "Add handler" button is scoped to handlers tab only (Alpine x-show).
- Popup response uses direct parent reload (not postMessage).
- Email handler plugin is registered and available.
"""

import io
import json
from types import SimpleNamespace

import pytest
from django import forms
from django.urls import reverse
from helpers import get_admin_edit_url


class TestImportJsonAction:
    """T13: JSON import must be available as Unfold changelist action."""

    def test_import_action_in_actions_list(self):
        """import_form_entry_action must be listed in actions_list."""
        from unfold_fobi.admin import FormEntryProxyAdmin

        assert "import_form_entry_action" in FormEntryProxyAdmin.actions_list

    def test_import_url_resolves(self, admin_client):
        """The import-json action URL must resolve under the admin namespace."""
        url = reverse("admin:unfold_fobi_formentryproxy_import_form_entry_action")
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_import_get_renders_upload_form(self, admin_client):
        """GET to import action must render the file upload template."""
        url = reverse("admin:unfold_fobi_formentryproxy_import_form_entry_action")
        response = admin_client.get(url)
        content = response.content.decode()
        assert 'type="file"' in content
        assert "Import" in content
        assert 'class="unfoldadminfilefieldwidget"' in content
        assert "file_upload" in content
        assert "bg-primary-600" in content
        assert "btn btn-primary" not in content
        assert "clearablefileinput" not in content

    def test_import_post_creates_form_entry(self, admin_client, admin_user, form_entry):
        """POST with valid export JSON must create a new form entry."""
        from fobi.models import FormEntry
        from fobi.utils import prepare_form_entry_export_data

        export_data = prepare_form_entry_export_data(form_entry)
        json_bytes = json.dumps(export_data).encode("utf-8")
        upload_file = io.BytesIO(json_bytes)
        upload_file.name = "form-export.json"

        count_before = FormEntry.objects.count()
        url = reverse("admin:unfold_fobi_formentryproxy_import_form_entry_action")
        response = admin_client.post(url, {"file": upload_file})

        assert response.status_code == 302
        assert FormEntry.objects.count() == count_before + 1

    def test_import_post_invalid_json_shows_error(self, admin_client):
        """POST with invalid JSON must return the form with an error."""
        upload_file = io.BytesIO(b"not valid json {{{")
        upload_file.name = "bad.json"

        url = reverse("admin:unfold_fobi_formentryproxy_import_form_entry_action")
        response = admin_client.post(url, {"file": upload_file})
        assert response.status_code == 200
        content = response.content.decode()
        assert 'type="file"' in content

    def test_import_post_invalid_payload_root_shows_error(self, admin_client):
        """POST with JSON root that is not dict/list must return form error."""
        upload_file = io.BytesIO(b'"unexpected-string-root"')
        upload_file.name = "bad-root.json"

        url = reverse("admin:unfold_fobi_formentryproxy_import_form_entry_action")
        response = admin_client.post(url, {"file": upload_file})
        assert response.status_code == 200
        content = response.content.decode()
        assert "expected an object or an array" in content

    def test_import_handles_array_payload(self, admin_client, admin_user, form_entry):
        """POST with exported JSON array (multi-form export) must import all forms."""
        from fobi.models import FormEntry
        from fobi.utils import prepare_form_entry_export_data

        export_data = prepare_form_entry_export_data(form_entry)
        # Export action produces a JSON array of form dicts
        json_bytes = json.dumps([export_data]).encode("utf-8")
        upload_file = io.BytesIO(json_bytes)
        upload_file.name = "form-export.json"

        count_before = FormEntry.objects.count()
        url = reverse("admin:unfold_fobi_formentryproxy_import_form_entry_action")
        response = admin_client.post(url, {"file": upload_file})

        assert response.status_code == 302
        assert FormEntry.objects.count() == count_before + 1

    def test_import_keeps_single_db_store_handler(
        self, admin_client, admin_user, form_entry
    ):
        """Imported form must end up with exactly one db_store handler."""
        from fobi.models import FormEntry, FormHandlerEntry
        from fobi.utils import prepare_form_entry_export_data

        export_data = prepare_form_entry_export_data(form_entry)
        upload_file = io.BytesIO(json.dumps(export_data).encode("utf-8"))
        upload_file.name = "form-export.json"

        existing_ids = set(FormEntry.objects.values_list("id", flat=True))
        url = reverse("admin:unfold_fobi_formentryproxy_import_form_entry_action")
        response = admin_client.post(url, {"file": upload_file})

        assert response.status_code == 302
        imported = (
            FormEntry.objects.exclude(id__in=existing_ids).order_by("-id").first()
        )
        assert imported is not None
        assert (
            FormHandlerEntry.objects.filter(
                form_entry=imported,
                plugin_uid="db_store",
            ).count()
            == 1
        )

    def test_import_action_has_permission_check(self):
        """Import action must declare permissions to prevent privilege escalation."""
        from unfold_fobi.admin import FormEntryProxyAdmin

        method = FormEntryProxyAdmin.import_form_entry_action
        assert hasattr(method, "allowed_permissions")
        assert "fobi.add_formentry" in method.allowed_permissions


class TestTabScopedAddButtons:
    """T13: Add Element/Handler buttons must be scoped to their respective tabs."""

    @pytest.fixture()
    def change_html(self, admin_client, form_entry):
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        return response.content.decode()

    def test_add_element_scoped_to_element_tab(self, change_html):
        """Add element button container must use x-show for formelemententry_set tab."""
        assert "x-show=\"activeTab == 'formelemententry_set'\"" in change_html

    def test_add_handler_scoped_to_handler_tab(self, change_html):
        """Add handler button container must use x-show for formhandlerentry_set tab."""
        assert "x-show=\"activeTab == 'formhandlerentry_set'\"" in change_html

    def test_add_element_has_x_cloak(self, change_html):
        """Add element container must have x-cloak to prevent flash of unstyled content."""
        # x-cloak should be on the same div that has the x-show for element tab
        assert "x-cloak" in change_html

    def test_add_handler_not_visible_by_default(self, change_html):
        """Without active tab set, add handler must be hidden (x-cloak + x-show)."""
        # Both x-show and x-cloak ensure it's hidden until Alpine activates the tab
        # The key contract: both element and handler containers use x-show + x-cloak
        assert change_html.count("x-cloak") >= 2


class TestPopupResponseReload:
    """T13: popup response must reload parent directly (not postMessage)."""

    def test_popup_response_uses_parent_reload(self):
        """popup_response.html must use window.parent.location.reload()."""
        from pathlib import Path

        template_path = (
            Path(__file__).resolve().parents[2]
            / "src"
            / "unfold_fobi"
            / "templates"
            / "admin"
            / "unfold_fobi"
            / "popup_response.html"
        )
        with open(template_path) as f:
            content = f.read()
        assert "window.parent.location.reload()" in content

    def test_popup_response_no_post_message_call(self):
        """popup_response.html must NOT call postMessage() (broken with unfold-modal)."""
        from pathlib import Path

        template_path = (
            Path(__file__).resolve().parents[2]
            / "src"
            / "unfold_fobi"
            / "templates"
            / "admin"
            / "unfold_fobi"
            / "popup_response.html"
        )
        with open(template_path) as f:
            content = f.read()
        # Must not have an actual postMessage() function call (comments are OK)
        assert ".postMessage(" not in content

    def test_popup_response_handles_opener(self):
        """popup_response.html must handle window.opener for traditional popups."""
        from pathlib import Path

        template_path = (
            Path(__file__).resolve().parents[2]
            / "src"
            / "unfold_fobi"
            / "templates"
            / "admin"
            / "unfold_fobi"
            / "popup_response.html"
        )
        with open(template_path) as f:
            content = f.read()
        assert "window.opener" in content


class TestEmailHandlerAvailability:
    """T13: email handler must be registered and available for forms."""

    def test_mail_handler_plugin_registered(self):
        """The mail handler plugin must be in the fobi handler registry."""
        from fobi.base import form_handler_plugin_registry

        registered_uids = form_handler_plugin_registry.registry.keys()
        assert "mail" in registered_uids

    def test_mail_handler_in_installed_apps(self):
        """fobi.contrib.plugins.form_handlers.mail must be in INSTALLED_APPS."""
        from django.conf import settings

        assert "fobi.contrib.plugins.form_handlers.mail" in settings.INSTALLED_APPS

    def test_email_backend_configured_in_settings(self):
        """Test project settings file must configure console email backend."""
        from pathlib import Path

        settings_file = (
            Path(__file__).resolve().parents[2]
            / "tests"
            / "server"
            / "testapp"
            / "settings.py"
        )
        content = settings_file.read_text()
        assert "django.core.mail.backends.console.EmailBackend" in content

    def test_mail_handler_appears_in_change_view(self, admin_client, form_entry):
        """Mail handler must appear as an option in the change view handler dropdown."""
        # Remove existing handlers so mail shows up (db_store is allow_multiple=False)
        from fobi.models import FormHandlerEntry

        FormHandlerEntry.objects.filter(
            form_entry=form_entry, plugin_uid="db_store"
        ).delete()

        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        html = response.content.decode()

        add_mail_url = reverse(
            "fobi.add_form_handler_entry",
            kwargs={
                "form_entry_id": form_entry.pk,
                "form_handler_plugin_uid": "mail",
            },
        )
        assert add_mail_url in html

    def test_change_view_renders_with_mail_handler(self, admin_client, form_entry):
        """Change view must not fail when a handler has no custom actions."""
        from fobi.models import FormHandlerEntry

        FormHandlerEntry.objects.get_or_create(
            form_entry=form_entry,
            plugin_uid="mail",
        )
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        assert response.status_code == 200


class TestMailSenderHandlerPatch:
    """mail_sender should not expose the unused recipient-name field."""

    @staticmethod
    def _make_plugin(form_entry_id):
        from fobi.contrib.plugins.form_handlers.mail_sender.base import (
            MailSenderHandlerPlugin,
        )

        plugin = MailSenderHandlerPlugin()
        plugin.request = SimpleNamespace(
            resolver_match=SimpleNamespace(kwargs={"form_entry_id": form_entry_id})
        )
        return plugin

    def test_mail_sender_form_omits_to_name_field(self, form_entry):
        from fobi.contrib.plugins.form_handlers.mail_sender.forms import (
            MailSenderForm,
        )

        form = self._make_plugin(form_entry.pk).get_initialised_create_form_or_404()

        assert "to_name" not in form.fields
        assert "to_name" not in dict(MailSenderForm.plugin_data_fields)

    def test_mail_sender_uses_dropdown_of_email_fields_only(self, form_entry):
        from fobi.models import FormElementEntry

        FormElementEntry.objects.create(
            form_entry=form_entry,
            plugin_uid="email",
            plugin_data=json.dumps(
                {
                    "label": "Email address",
                    "name": "email",
                    "required": True,
                }
            ),
            position=2,
        )

        form = self._make_plugin(form_entry.pk).get_initialised_create_form_or_404()
        field = form.fields["form_field_name_to_email"]

        assert isinstance(field, forms.ChoiceField)
        assert ("", "Choose email field") in field.choices
        assert ("email", "Email address (email)") in field.choices
        assert ("full_name", "Full Name (full_name)") not in field.choices

    def test_mail_sender_has_empty_dropdown_when_no_email_fields(self, form_entry):
        form = self._make_plugin(form_entry.pk).get_initialised_create_form_or_404()
        field = form.fields["form_field_name_to_email"]

        assert isinstance(field, forms.ChoiceField)
        assert list(field.choices) == [
            (
                "",
                "No email fields are available on this form. Add an email field first.",
            )
        ]

    def test_mail_sender_rejects_non_email_field_names(self, form_entry):
        from fobi.models import FormElementEntry

        FormElementEntry.objects.create(
            form_entry=form_entry,
            plugin_uid="email",
            plugin_data=json.dumps(
                {
                    "label": "Email address",
                    "name": "email",
                    "required": True,
                }
            ),
            position=2,
        )

        plugin = self._make_plugin(form_entry.pk)
        plugin.data = SimpleNamespace(
            form_field_name_to_email="full_name",
            subject="Confirmation",
        )

        form = plugin.get_initialised_create_form_or_404(
            data={
                "from_name": "Test sender",
                "from_email": "sender@example.com",
                "form_field_name_to_email": "full_name",
                "subject": "Confirmation",
                "body": "Body",
            }
        )

        assert not form.is_valid()
        assert "form_field_name_to_email" in form.errors

    def test_mail_sender_plugin_data_repr_does_not_require_to_name(self):
        from fobi.contrib.plugins.form_handlers.mail_sender.base import (
            MailSenderHandlerPlugin,
        )

        plugin = MailSenderHandlerPlugin()
        plugin.data = SimpleNamespace(
            form_field_name_to_email="email",
            subject="Confirmation",
        )

        html = plugin.plugin_data_repr()

        assert "email" in html
        assert "Confirmation" in html
