"""Native change-view sorting, tabs, and inline ordering behavior."""

import re

import pytest

from helpers import get_admin_edit_url


class TestElementPositionEditing:
    """Element position must be editable and saved via the admin form."""

    def test_position_field_is_editable(self, admin_client, form_entry):
        """Position input must be a writable field, not just readonly text."""
        url = get_admin_edit_url(form_entry.pk)
        response = admin_client.get(url)
        html = response.content.decode()
        assert 'name="formelemententry_set-0-position"' in html

    def test_position_change_persisted_on_save(self, admin_client, form_entry):
        """Changing element position via admin save must persist."""
        element = form_entry.formelemententry_set.first()
        assert element.position == 1

        url = get_admin_edit_url(form_entry.pk)
        admin_client.get(url)

        post_data = {
            "name": form_entry.name,
            "slug": form_entry.slug,
            "is_public": "on" if form_entry.is_public else "",
            "is_cloneable": "on" if form_entry.is_cloneable else "",
            "formelemententry_set-TOTAL_FORMS": "1",
            "formelemententry_set-INITIAL_FORMS": "1",
            "formelemententry_set-MIN_NUM_FORMS": "0",
            "formelemententry_set-MAX_NUM_FORMS": "0",
            "formelemententry_set-0-id": str(element.pk),
            "formelemententry_set-0-form_entry": str(form_entry.pk),
            "formelemententry_set-0-position": "5",
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
    """Drag-drop reordering of multiple elements must persist after save."""

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
        for i, (uid, label) in enumerate(
            [
                ("text", "First Name"),
                ("email", "Email Address"),
                ("text", "Last Name"),
            ]
        ):
            FormElementEntry.objects.create(
                form_entry=entry,
                plugin_uid=uid,
                plugin_data=_json.dumps({"label": label, "name": f"field_{i}"}),
                position=i,
            )
        FormHandlerEntry.objects.get_or_create(
            form_entry=entry,
            plugin_uid="db_store",
        )
        return entry

    def test_multi_element_reorder_persisted(self, admin_client, form_entry_multi):
        """Each formset row keeps its id; only position changes."""
        entry = form_entry_multi
        elements = list(entry.formelemententry_set.order_by("position"))
        assert len(elements) == 3
        assert [e.position for e in elements] == [0, 1, 2]

        url = get_admin_edit_url(entry.pk)
        handler = entry.formhandlerentry_set.first()

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
        assert elements[0].position == 2
        assert elements[1].position == 1
        assert elements[2].position == 0

    def test_reordered_elements_render_in_position_order(
        self, admin_client, form_entry_multi
    ):
        """Inline row 0 must contain the element with the lowest position."""
        entry = form_entry_multi
        elements = list(entry.formelemententry_set.order_by("position"))
        elements[0].position = 2
        elements[2].position = 0
        elements[0].save()
        elements[2].save()

        url = get_admin_edit_url(entry.pk)
        response = admin_client.get(url)
        html = response.content.decode()

        id_pattern = re.compile(r'name="formelemententry_set-(\d+)-id"\s+value="(\d+)"')
        rendered_order = {
            int(m.group(1)): int(m.group(2)) for m in id_pattern.finditer(html)
        }
        assert rendered_order[0] == elements[2].pk
        assert rendered_order[2] == elements[0].pk


class TestInlineTabs:
    """Inlines must render as tabs using Unfold's native tab pattern."""

    def test_element_inline_tab_present(self, change_html):
        assert "formelemententry_set" in change_html

    def test_handler_inline_tab_present(self, change_html):
        assert "formhandlerentry_set" in change_html

    def test_inline_uses_x_show_for_tabs(self, change_html):
        assert "x-show" in change_html


class TestSortableInline:
    """Element inline must use the Unfold sortable contract."""

    def test_ordering_field_data_attribute(self, change_html):
        assert 'data-ordering-field="position"' in change_html

    def test_sort_ghost_directive(self, change_html):
        assert "x-sort.ghost" in change_html

    def test_sort_end_event_binding(self, change_html):
        assert 'x-on:end="sortRecords"' in change_html

    def test_drag_handle_icon(self, change_html):
        assert "drag_indicator" in change_html

    def test_drag_handle_markup_contract(self, change_html):
        assert (
            'class="material-symbols-outlined cursor-move" x-sort:handle>drag_indicator'
            in change_html
        )
