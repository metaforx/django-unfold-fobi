"""T03 – Add-view fieldset baseline tests.

Verifies that the admin add view loads and produces the expected fieldset
groups, including the active-dates section and visibility inline grouping.
"""
import pytest
from django.test import RequestFactory
from django.urls import reverse

from helpers import (
    assert_fieldsets_contain_group,
    assert_fieldsets_group_has_fields,
    get_admin_add_url,
)


class TestAddViewLoads:
    """The add view should return 200 for an authenticated admin."""

    def test_add_view_returns_200(self, admin_client):
        response = admin_client.get(get_admin_add_url())
        assert response.status_code == 200


class TestAddViewFieldsets:
    """get_fieldsets must produce the defined grouped sections."""

    @pytest.fixture()
    def fieldsets(self, admin_user):
        """Call get_fieldsets on the registered ModelAdmin."""
        from django.contrib import admin

        from unfold_fobi.models import FormEntryProxy

        ma = admin.site._registry[FormEntryProxy]
        factory = RequestFactory()
        request = factory.get("/admin/")
        request.user = admin_user
        return ma.get_fieldsets(request, obj=None)

    def test_has_basic_information(self, fieldsets):
        assert_fieldsets_contain_group(fieldsets, "Basic information")

    def test_has_visibility(self, fieldsets):
        assert_fieldsets_contain_group(fieldsets, "Visibility")

    def test_has_success_page(self, fieldsets):
        assert_fieldsets_contain_group(fieldsets, "Success page")

    def test_has_active_dates(self, fieldsets):
        assert_fieldsets_contain_group(fieldsets, "Active dates")

    def test_visibility_groups_public_and_cloneable(self, fieldsets):
        """is_public and is_cloneable should be grouped together."""
        assert_fieldsets_group_has_fields(
            fieldsets, "Visibility", ["is_public", "is_cloneable"]
        )

    def test_active_dates_has_date_fields(self, fieldsets):
        """Active dates group must contain the date range fields."""
        assert_fieldsets_group_has_fields(
            fieldsets, "Active dates", ["active_date_from", "active_date_to"]
        )
