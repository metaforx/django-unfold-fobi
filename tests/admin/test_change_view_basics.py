"""Native change-view basics: routes, fieldsets, inlines, and add actions."""

import pytest
from django.urls import reverse

from helpers import get_admin_edit_url


class TestChangeViewRoute:
    """The change URL must resolve and enforce authentication."""

    def test_change_route_resolves(self, form_entry):
        url = get_admin_edit_url(form_entry.pk)
        assert "/change/" in url

    def test_change_view_requires_authentication(self, client, form_entry):
        """Unauthenticated requests must redirect (302)."""
        url = get_admin_edit_url(form_entry.pk)
        response = client.get(url)
        assert response.status_code == 302

    def test_change_view_accessible_for_admin(self, admin_client, form_entry):
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        assert response.status_code == 200


class TestChangeViewFieldsets:
    """Native change view must render fieldsets from get_fieldsets."""

    def test_basic_information_fieldset(self, change_html):
        assert "Basic information" in change_html

    def test_visibility_fieldset(self, change_html):
        assert "Visibility" in change_html


class TestElementInline:
    """Element inline must show existing elements with action links."""

    def test_element_inline_present(self, change_html):
        """The element inline section must be rendered."""
        assert "Form elements" in change_html

    def test_element_plugin_uid_displayed(self, change_html):
        """The text plugin uid must appear in the inline."""
        assert "text" in change_html

    def test_element_edit_link(self, change_html, form_entry):
        """Edit action link for the element must be present."""
        element = form_entry.formelemententry_set.first()
        edit_url = reverse(
            "fobi.edit_form_element_entry",
            kwargs={"form_element_entry_id": element.pk},
        )
        assert edit_url in change_html

    def test_element_delete_link(self, change_html, form_entry):
        """Delete action link for the element must be present."""
        element = form_entry.formelemententry_set.first()
        delete_url = reverse(
            "fobi.delete_form_element_entry",
            kwargs={"form_element_entry_id": element.pk},
        )
        assert delete_url in change_html


class TestHandlerInline:
    """Handler inline must show existing handlers with action links."""

    def test_handler_inline_present(self, change_html):
        """The handler inline section must be rendered."""
        assert "Form handlers" in change_html

    def test_handler_plugin_uid_displayed(self, change_html):
        """The db_store handler uid must appear in the inline."""
        assert "db_store" in change_html

    def test_handler_delete_link(self, change_html, form_entry):
        """Delete action link for the handler must be present."""
        from fobi.models import FormHandlerEntry

        handler = FormHandlerEntry.objects.filter(
            form_entry=form_entry, plugin_uid="db_store"
        ).first()
        delete_url = reverse(
            "fobi.delete_form_handler_entry",
            kwargs={"form_handler_entry_id": handler.pk},
        )
        assert delete_url in change_html


class TestAddElementDropdown:
    """Change page must show 'Add element' dropdown with available plugins."""

    def test_add_element_button_present(self, change_html):
        assert "Add element" in change_html

    def test_add_element_links_to_fobi_add_url(self, change_html, form_entry):
        """At least one element plugin add URL must be in the dropdown."""
        add_url = reverse(
            "fobi.add_form_element_entry",
            kwargs={
                "form_entry_id": form_entry.pk,
                "form_element_plugin_uid": "text",
            },
        )
        assert add_url in change_html

    def test_add_element_shows_grouped_plugins(self, change_html):
        """Element plugins must be listed (e.g. Text, Email)."""
        assert "Text" in change_html
        assert "Email" in change_html


class TestAddHandlerDropdown:
    """Change page must show 'Add handler' dropdown with constraints."""

    def test_add_handler_button_hidden_when_single_use_attached(
        self, admin_client, form_entry
    ):
        """db_store is allow_multiple=False and already attached, so it must not appear."""
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        html = response.content.decode()
        add_url = reverse(
            "fobi.add_form_handler_entry",
            kwargs={
                "form_entry_id": form_entry.pk,
                "form_handler_plugin_uid": "db_store",
            },
        )
        assert add_url not in html

    def test_add_handler_button_shows_when_no_handler_attached(
        self, admin_client, form_entry
    ):
        """If db_store handler is removed, it must appear in the dropdown."""
        from fobi.models import FormHandlerEntry

        FormHandlerEntry.objects.filter(
            form_entry=form_entry, plugin_uid="db_store"
        ).delete()
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        html = response.content.decode()
        add_url = reverse(
            "fobi.add_form_handler_entry",
            kwargs={
                "form_entry_id": form_entry.pk,
                "form_handler_plugin_uid": "db_store",
            },
        )
        assert add_url in html
