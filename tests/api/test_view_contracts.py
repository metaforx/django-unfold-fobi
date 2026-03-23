from django.urls import reverse
from django.utils.translation import override as translation_override
from fobi.contrib.plugins.form_handlers.db_store.models import (
    SavedFormDataEntry,
)


class TestChangeViewBreadcrumbContract:
    """T10: native change view renders proxy breadcrumbs."""

    def test_change_view_contains_form_name(self, admin_client, form_entry):
        url = reverse("admin:unfold_fobi_formentryproxy_change", args=[form_entry.pk])
        response = admin_client.get(url)
        assert response.status_code == 200
        html = response.content.decode("utf-8")
        assert form_entry.name in html

    def test_change_view_contains_proxy_verbose_name(self, admin_client, form_entry):
        with translation_override("en"):
            url = reverse(
                "admin:unfold_fobi_formentryproxy_change",
                args=[form_entry.pk],
            )
            response = admin_client.get(url)
        html = response.content.decode("utf-8")
        assert "Forms (builder)" in html


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
        saved_count = SavedFormDataEntry.objects.filter(form_entry=form_entry).count()
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
