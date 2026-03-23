"""Native change-view permissions and non-owner access checks."""

from django.urls import reverse


class TestElementEditNonOwner:
    """Element edit and delete must not 404 for a different admin user."""

    def test_element_edit_accessible_by_non_owner(self, other_admin_client, form_entry):
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
        element = form_entry.formelemententry_set.first()
        delete_url = reverse(
            "fobi.delete_form_element_entry",
            kwargs={"form_element_entry_id": element.pk},
        )
        response = other_admin_client.get(delete_url)
        assert response.status_code in (200, 302)

    def test_handler_delete_accessible_by_non_owner(
        self, other_admin_client, form_entry
    ):
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
