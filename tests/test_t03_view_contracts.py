import pytest
from django.urls import reverse

from fobi.contrib.plugins.form_handlers.db_store.models import (
    SavedFormDataEntry,
)


class TestPendingEditViewContracts:
    @pytest.mark.xfail(
        reason="Pending T06: proxy breadcrumb contract is not implemented yet."
    )
    def test_edit_view_uses_proxy_breadcrumb_contract(
        self, admin_client, form_entry
    ):
        url = reverse(
            "admin:unfold_fobi_formentryproxy_edit", args=[form_entry.pk]
        )
        response = admin_client.get(url)
        assert response.status_code == 200
        html = response.content.decode("utf-8")

        assert "Forms (builder)" in html
        assert "/admin/fobi/formentry/" not in html
        assert "Form entries" not in html

    @pytest.mark.xfail(
        reason="Pending T07: edit save action should follow Unfold submit-row convention."
    )
    def test_edit_view_uses_unfold_submit_row_for_save_action(
        self, admin_client, form_entry
    ):
        url = reverse(
            "admin:unfold_fobi_formentryproxy_edit", args=[form_entry.pk]
        )
        response = admin_client.get(url)
        assert response.status_code == 200
        html = response.content.decode("utf-8")

        assert 'id="submit-row"' in html
        assert (
            '<button type="submit" form="formentryproxy_form" '
            'name="_save"'
        ) in html


class TestViewEntriesFlow:
    def test_view_entries_url_for_form(self, form_entry):
        url = reverse(
            "fobi.contrib.plugins.form_handlers.db_store.view_saved_form_data_entries",
            args=[form_entry.pk],
        )
        assert url == f"/fobi/{form_entry.pk}/"

    def test_rest_put_creates_saved_form_data_entry(
        self, form_entry, rest_submitted_form_data
    ):
        saved_count = SavedFormDataEntry.objects.filter(
            form_entry=form_entry
        ).count()
        assert saved_count == 1

        payload = rest_submitted_form_data["payload"]
        response = rest_submitted_form_data["response"]
        assert response.json() == payload

    def test_view_entries_lists_rest_submitted_data(
        self, admin_client, form_entry, rest_submitted_form_data
    ):
        url = reverse(
            "fobi.contrib.plugins.form_handlers.db_store.view_saved_form_data_entries",
            args=[form_entry.pk],
        )
        response = admin_client.get(url)
        assert response.status_code == 200

        html = response.content.decode("utf-8")
        assert "Saved form data" in html
        assert "db-store-saved-form-data-entry-table" in html
        assert "Full Name: Alice Example" in html
