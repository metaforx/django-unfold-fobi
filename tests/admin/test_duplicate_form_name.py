"""T22: Prevent duplicate form names with friendly validation."""

import pytest
from django.urls import reverse
from fobi.models import FormEntry


@pytest.fixture()
def existing_form(db, admin_user):
    """A form that already exists for admin_user."""
    return FormEntry.objects.create(
        user=admin_user,
        name="Testformular",
        slug="testformular",
        is_public=True,
    )


class TestDuplicateFormNameValidation:
    """Creating or renaming a form to a duplicate name must show a validation error."""

    def test_add_duplicate_name_shows_error(self, admin_client, existing_form):
        """Creating a form with an existing name returns a form error, not a 500."""
        url = reverse("admin:unfold_fobi_formentryproxy_add")
        response = admin_client.post(url, {"name": "Testformular"})
        assert response.status_code == 200  # re-renders form with errors
        content = response.content.decode()
        assert "already exists" in content

    def test_add_unique_name_has_no_duplicate_error(self, admin_client, existing_form):
        """A unique name must not trigger the duplicate-name validation error."""
        url = reverse("admin:unfold_fobi_formentryproxy_add")
        response = admin_client.post(url, {"name": "Different Form"})
        content = response.content.decode()
        assert "already exists" not in content

    def test_save_own_name_succeeds(self, admin_client, existing_form):
        """Saving a form without changing its name must not trigger the error."""
        url = reverse(
            "admin:unfold_fobi_formentryproxy_change", args=[existing_form.pk]
        )
        response = admin_client.post(
            url, {"name": "Testformular"}, follow=True
        )
        # Should succeed (redirect, not re-render with error)
        assert response.status_code == 200
        assert "already exists" not in response.content.decode()

    def test_rename_to_duplicate_shows_error(
        self, admin_client, admin_user, existing_form
    ):
        """Renaming a form to a conflicting name returns a form error."""
        other = FormEntry.objects.create(
            user=admin_user,
            name="Other Form",
            slug="other-form",
            is_public=True,
        )
        url = reverse(
            "admin:unfold_fobi_formentryproxy_change", args=[other.pk]
        )
        response = admin_client.post(url, {"name": "Testformular"})
        assert response.status_code == 200
        content = response.content.decode()
        assert "already exists" in content
