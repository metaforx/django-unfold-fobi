"""T10/T10a/T10b/T10c/T10d – Native change view tests.

Verifies:
- Change route resolves and is permission-protected.
- Native change view renders with fieldsets and inlines.
- Element inline shows plugin actions (edit/delete links).
- Handler inline shows plugin actions.
- T10a: "Add element" and "Add handler" dropdowns present.
- T10a: Element position is editable and persisted on save.
- T10a: Single-use handler plugins are hidden from "Add handler" dropdown.
- T10b: Element edit works for non-owner admin (no 404).
- T10b: Inline tabs render for elements and handlers.
- T10b: Sortable inline attributes present (ordering_field, x-sort).
- T10c: Multi-element drag-drop reorder persists after save.
- T10d: Drag handle HTML contract (CSS classes, Alpine directives, icon).
"""

import pytest
from django.contrib.auth.models import User
from django.test import Client
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


class TestAddElementDropdown:
    """T10a: change page must show 'Add element' dropdown with available plugins."""

    @pytest.fixture()
    def change_html(self, admin_client, form_entry):
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        return response.content.decode()

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
    """T10a: change page must show 'Add handler' dropdown with constraints."""

    def test_add_handler_button_hidden_when_single_use_attached(
        self, admin_client, form_entry
    ):
        """db_store is allow_multiple=False and already attached, so
        it must NOT appear in the handler dropdown."""
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


class TestElementPositionEditing:
    """T10a: element position must be editable and saved via admin form."""

    def test_position_field_is_editable(self, admin_client, form_entry):
        """Position input must be a writable field (not just readonly text)."""
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        html = response.content.decode()
        # Position should appear as an input field, not just as display text
        assert 'name="formelemententry_set-0-position"' in html

    def test_position_change_persisted_on_save(self, admin_client, form_entry):
        """Changing element position via admin save must persist."""

        element = form_entry.formelemententry_set.first()
        assert element.position == 1

        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)

        # Build POST data from the change form
        post_data = {
            "name": form_entry.name,
            "slug": form_entry.slug,
            "is_public": "on" if form_entry.is_public else "",
            "is_cloneable": "on" if form_entry.is_cloneable else "",
            # Element inline formset
            "formelemententry_set-TOTAL_FORMS": "1",
            "formelemententry_set-INITIAL_FORMS": "1",
            "formelemententry_set-MIN_NUM_FORMS": "0",
            "formelemententry_set-MAX_NUM_FORMS": "0",
            "formelemententry_set-0-id": str(element.pk),
            "formelemententry_set-0-form_entry": str(form_entry.pk),
            "formelemententry_set-0-position": "5",
            # Handler inline formset (unchanged)
            "formhandlerentry_set-TOTAL_FORMS": "1",
            "formhandlerentry_set-INITIAL_FORMS": "1",
            "formhandlerentry_set-MIN_NUM_FORMS": "0",
            "formhandlerentry_set-MAX_NUM_FORMS": "0",
            "formhandlerentry_set-0-id": str(
                form_entry.formhandlerentry_set.first().pk
            ),
            "formhandlerentry_set-0-form_entry": str(form_entry.pk),
            "_save": "Save",
        }

        response = admin_client.post(url, data=post_data)
        assert response.status_code in (200, 302)

        element.refresh_from_db()
        assert element.position == 5


class TestMultiElementSortPersistence:
    """T10c: drag-drop reordering of multiple elements must persist after save."""

    @pytest.fixture()
    def form_entry_multi(self, db, admin_user):
        """Form with three elements at positions 0, 1, 2."""
        import json as _json

        from fobi.models import FormElementEntry, FormEntry, FormHandlerEntry

        entry = FormEntry.objects.create(
            user=admin_user,
            name="Multi Element Form",
            slug="multi-element-form",
            is_public=True,
            is_cloneable=True,
        )
        for i, (uid, label) in enumerate([
            ("text", "First Name"),
            ("email", "Email Address"),
            ("text", "Last Name"),
        ]):
            FormElementEntry.objects.create(
                form_entry=entry,
                plugin_uid=uid,
                plugin_data=_json.dumps({"label": label, "name": f"field_{i}"}),
                position=i,
            )
        FormHandlerEntry.objects.get_or_create(
            form_entry=entry, plugin_uid="db_store",
        )
        return entry

    def test_multi_element_reorder_persisted(self, admin_client, form_entry_multi):
        """Simulates sortRecords(): each formset row keeps its id, only position changes."""
        entry = form_entry_multi
        elements = list(entry.formelemententry_set.order_by("position"))
        assert len(elements) == 3
        assert [e.position for e in elements] == [0, 1, 2]

        url = get_admin_edit_url(entry.pk)
        handler = entry.formhandlerentry_set.first()

        # Real browser behavior: sortRecords keeps each form index paired
        # with its original element id and only mutates the position input.
        # Simulate reversing order: A(0→2), B(1→1), C(2→0).
        new_positions = [2, 1, 0]
        post_data = {
            "name": entry.name,
            "slug": entry.slug,
            "is_public": "on",
            "is_cloneable": "on",
            "formelemententry_set-TOTAL_FORMS": "3",
            "formelemententry_set-INITIAL_FORMS": "3",
            "formelemententry_set-MIN_NUM_FORMS": "0",
            "formelemententry_set-MAX_NUM_FORMS": "0",
            "formhandlerentry_set-TOTAL_FORMS": "1",
            "formhandlerentry_set-INITIAL_FORMS": "1",
            "formhandlerentry_set-MIN_NUM_FORMS": "0",
            "formhandlerentry_set-MAX_NUM_FORMS": "0",
            "formhandlerentry_set-0-id": str(handler.pk),
            "formhandlerentry_set-0-form_entry": str(entry.pk),
            "_save": "Save",
        }
        for idx, elem in enumerate(elements):
            prefix = f"formelemententry_set-{idx}"
            post_data[f"{prefix}-id"] = str(elem.pk)
            post_data[f"{prefix}-form_entry"] = str(entry.pk)
            post_data[f"{prefix}-position"] = str(new_positions[idx])

        response = admin_client.post(url, data=post_data)
        assert response.status_code in (200, 302)

        for elem in elements:
            elem.refresh_from_db()
        assert elements[0].position == 2  # A: was 0, now last
        assert elements[1].position == 1  # B: unchanged (middle)
        assert elements[2].position == 0  # C: was 2, now first

    def test_reordered_elements_render_in_position_order(
        self, admin_client, form_entry_multi
    ):
        """After reorder, inline row 0 must contain the element with lowest position."""
        import re

        entry = form_entry_multi
        elements = list(entry.formelemententry_set.order_by("position"))
        # Swap first and last via DB
        elements[0].position = 2
        elements[2].position = 0
        elements[0].save()
        elements[2].save()

        url = get_admin_edit_url(entry.pk)
        response = admin_client.get(url)
        html = response.content.decode()

        # Extract element PKs in formset render order (index 0, 1, 2)
        id_pattern = re.compile(
            r'name="formelemententry_set-(\d+)-id"\s+value="(\d+)"'
        )
        rendered_order = {
            int(m.group(1)): int(m.group(2)) for m in id_pattern.finditer(html)
        }
        # Inline row 0 must be the element now at position 0 (originally elements[2])
        assert rendered_order[0] == elements[2].pk
        # Inline row 2 must be the element now at position 2 (originally elements[0])
        assert rendered_order[2] == elements[0].pk


class TestElementEditNonOwner:
    """T10b: element edit must not 404 for admin users who are not the form owner."""

    @pytest.fixture()
    def other_admin(self, db):
        return User.objects.create_superuser(
            username="other_admin", email="other@test.local", password="pass"
        )

    @pytest.fixture()
    def other_admin_client(self, other_admin):
        client = Client()
        client.login(username="other_admin", password="pass")
        return client

    def test_element_edit_accessible_by_non_owner(
        self, other_admin_client, form_entry
    ):
        """A staff user who did not create the form must be able to edit elements."""
        element = form_entry.formelemententry_set.first()
        edit_url = reverse(
            "fobi.edit_form_element_entry",
            kwargs={"form_element_entry_id": element.pk},
        )
        response = other_admin_client.get(edit_url)
        assert response.status_code == 200

    def test_element_delete_accessible_by_non_owner(
        self, other_admin_client, form_entry
    ):
        """A staff user who did not create the form must be able to delete elements."""
        element = form_entry.formelemententry_set.first()
        delete_url = reverse(
            "fobi.delete_form_element_entry",
            kwargs={"form_element_entry_id": element.pk},
        )
        response = other_admin_client.get(delete_url)
        # delete view redirects (302) after deletion, or shows confirmation (200)
        assert response.status_code in (200, 302)

    def test_handler_delete_accessible_by_non_owner(
        self, other_admin_client, form_entry
    ):
        """A staff user who did not create the form must be able to delete handlers."""
        from fobi.models import FormHandlerEntry

        handler = FormHandlerEntry.objects.filter(
            form_entry=form_entry, plugin_uid="db_store"
        ).first()
        delete_url = reverse(
            "fobi.delete_form_handler_entry",
            kwargs={"form_handler_entry_id": handler.pk},
        )
        response = other_admin_client.get(delete_url)
        assert response.status_code in (200, 302)


class TestInlineTabs:
    """T10b: inlines must render as tabs (Unfold native inline tabs)."""

    @pytest.fixture()
    def change_html(self, admin_client, form_entry):
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        return response.content.decode()

    def test_element_inline_tab_present(self, change_html):
        """Tab navigation must include a tab for form elements."""
        # Unfold renders tab buttons with the formset prefix as slug
        assert "formelemententry_set" in change_html

    def test_handler_inline_tab_present(self, change_html):
        """Tab navigation must include a tab for form handlers."""
        assert "formhandlerentry_set" in change_html

    def test_inline_uses_x_show_for_tabs(self, change_html):
        """Inlines must use x-show for tab switching (Unfold native pattern)."""
        assert "x-show" in change_html


class TestSortableInline:
    """T10b/T10d: element inline must use Unfold sortable pattern with full handle contract."""

    @pytest.fixture()
    def change_html(self, admin_client, form_entry):
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        return response.content.decode()

    def test_ordering_field_data_attribute(self, change_html):
        """The element inline table must have data-ordering-field='position'."""
        assert 'data-ordering-field="position"' in change_html

    def test_sort_ghost_directive(self, change_html):
        """The element inline must have Alpine.js x-sort.ghost directive."""
        assert "x-sort.ghost" in change_html

    def test_sort_end_event_binding(self, change_html):
        """The inline table must bind sortRecords on drag-end."""
        assert 'x-on:end="sortRecords"' in change_html

    def test_drag_handle_icon(self, change_html):
        """Drag handle icon must be present for existing elements."""
        assert "drag_indicator" in change_html

    def test_drag_handle_markup_contract(self, change_html):
        """T10d: drag handle must be a single element with all required attributes."""
        # Unfold renders: <span class="material-symbols-outlined cursor-move" x-sort:handle>drag_indicator</span>
        # Assert the full contiguous fragment to prevent false positives.
        assert (
            'class="material-symbols-outlined cursor-move" x-sort:handle>drag_indicator'
            in change_html
        )
