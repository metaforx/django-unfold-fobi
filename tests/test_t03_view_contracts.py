import pytest
from django.urls import reverse
from django.utils.translation import override as translation_override

from fobi.contrib.plugins.form_handlers.db_store.models import (
    SavedFormDataEntry,
)


class TestEditViewBreadcrumbContract:
    """T06: proxy breadcrumb contract must render correctly."""

    def test_edit_view_uses_proxy_breadcrumb_contract(
        self, admin_client, form_entry
    ):
        with translation_override("en"):
            url = reverse(
                "admin:unfold_fobi_formentryproxy_edit", args=[form_entry.pk]
            )
            response = admin_client.get(url)
        assert response.status_code == 200
        html = response.content.decode("utf-8")

        assert "Forms (builder)" in html
        # The breadcrumb must link through the proxy changelist, not the
        # raw fobi FormEntry changelist.  The fobi URL may still appear
        # elsewhere on the page (e.g. sidebar), so we scope the check to
        # breadcrumb anchors only.
        import re

        breadcrumb_hrefs = re.findall(
            r'<a[^>]*class="[^"]*truncate[^"]*"[^>]*href="([^"]*)"', html
        )
        for href in breadcrumb_hrefs:
            assert "/fobi/formentry/" not in href, (
                f"Breadcrumb links to raw FormEntry URL: {href}"
            )

    def test_breadcrumb_contains_form_name(self, admin_client, form_entry):
        url = reverse(
            "admin:unfold_fobi_formentryproxy_edit", args=[form_entry.pk]
        )
        response = admin_client.get(url)
        html = response.content.decode("utf-8")
        assert form_entry.name in html

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
