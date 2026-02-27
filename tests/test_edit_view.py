"""T03 – Edit-view baseline tests.

Verifies:
- Edit route resolves and is permission-protected.
- Edit template renders the Alpine.js tabs container with expected tab labels.
- "Save ordering" button is absent (auto-save via JS instead).
- Ordering POST path behaves as expected.
"""
import pytest
from django.urls import reverse

from helpers import (
    assert_html_contains_tab,
    assert_no_save_ordering_button,
    get_admin_edit_url,
)


class TestEditViewRoute:
    """The edit URL must resolve and enforce authentication."""

    def test_edit_route_resolves(self, form_entry):
        url = get_admin_edit_url(form_entry.pk)
        assert "/edit/" in url

    def test_edit_view_requires_authentication(self, client, form_entry):
        """Unauthenticated requests must redirect (302)."""
        url = get_admin_edit_url(form_entry.pk)
        response = client.get(url)
        assert response.status_code == 302

    def test_edit_view_accessible_for_admin(self, admin_client, form_entry):
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        assert response.status_code == 200


class TestEditTemplateTabs:
    """The edit template must render the Alpine.js tabs container."""

    @pytest.fixture()
    def edit_html(self, admin_client, form_entry):
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        return response.content.decode()

    def test_tabs_container_present(self, edit_html):
        assert 'id="tabs-alpine"' in edit_html

    def test_elements_tab_label(self, edit_html):
        assert_html_contains_tab(edit_html, "Elements")

    def test_handlers_tab_label(self, edit_html):
        assert_html_contains_tab(edit_html, "Handlers")

    def test_properties_tab_label(self, edit_html):
        assert_html_contains_tab(edit_html, "Properties")

    def test_tab_content_sections_present(self, edit_html):
        """Each tab must have a corresponding content div."""
        assert 'id="tab-form-elements"' in edit_html
        assert 'id="tab-form-handlers"' in edit_html
        assert 'id="tab-form-properties"' in edit_html


class TestSaveOrderingAbsent:
    """No visible 'Save ordering' button; ordering is auto-saved via JS."""

    def test_no_save_ordering_button(self, admin_client, form_entry):
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        content = response.content.decode()
        assert_no_save_ordering_button(content)

    def test_ordering_hidden_input_present(self, admin_client, form_entry):
        """A hidden ordering field should exist for JS auto-save."""
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        content = response.content.decode()
        assert 'name="ordering"' in content


class TestOrderingPost:
    """The ordering POST path must accept valid position data."""

    def test_ordering_post_redirects_on_success(self, admin_client, form_entry):
        """POST with ordering=1 and valid positions redirects (302)."""
        url = get_admin_edit_url(form_entry.pk)
        element = form_entry.formelemententry_set.first()
        data = {
            "ordering": "1",
            f"form-0-id": str(element.pk),
            f"form-0-position": "1",
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "1",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
        }
        response = admin_client.post(url, data=data)
        assert response.status_code == 302

    def test_ordering_post_invalid_positions_redirects(
        self, admin_client, form_entry
    ):
        """POST with invalid positions still redirects (with error message)."""
        url = get_admin_edit_url(form_entry.pk)
        data = {
            "ordering": "1",
            "form-0-position": "999",
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "1",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
        }
        response = admin_client.post(url, data=data)
        assert response.status_code == 302
