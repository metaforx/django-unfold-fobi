"""T10 – Native change view baseline tests.

Verifies:
- Change route resolves and is permission-protected.
- Native change view renders with fieldsets and inlines.
- Element inline shows plugin actions (edit/delete links).
- Handler inline shows plugin actions.
"""
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

    @pytest.fixture()
    def change_html(self, admin_client, form_entry):
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        return response.content.decode()

    def test_basic_information_fieldset(self, change_html):
        assert "Basic information" in change_html

    def test_visibility_fieldset(self, change_html):
        assert "Visibility" in change_html

    def test_form_name_displayed(self, change_html, form_entry):
        assert form_entry.name in change_html


class TestElementInline:
    """Element inline must show existing elements with action links."""

    @pytest.fixture()
    def change_html(self, admin_client, form_entry):
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        return response.content.decode()

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

    @pytest.fixture()
    def change_html(self, admin_client, form_entry):
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        return response.content.decode()

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
