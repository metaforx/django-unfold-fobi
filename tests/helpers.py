"""Reusable assertion helpers for unfold_fobi tests (T03+)."""

from django.urls import reverse


def get_admin_add_url():
    """Return the admin add URL for FormEntryProxy."""
    return reverse("admin:unfold_fobi_formentryproxy_add")


def get_admin_edit_url(pk):
    """Return the admin change URL for a form entry (native change view)."""
    return reverse("admin:unfold_fobi_formentryproxy_change", args=[pk])


def get_admin_changelist_url():
    """Return the admin changelist URL for FormEntryProxy."""
    return reverse("admin:unfold_fobi_formentryproxy_changelist")


def assert_fieldsets_contain_group(fieldsets, group_name):
    """Assert that *fieldsets* includes a group whose label matches *group_name*.

    Works with both plain strings and lazy translation proxies.
    """
    labels = [str(label) for label, _opts in fieldsets]
    assert group_name in labels, (
        f"Expected fieldset group '{group_name}' not found. Available groups: {labels}"
    )


def assert_fieldsets_group_has_fields(fieldsets, group_name, expected_fields):
    """Assert a fieldset group contains all *expected_fields*."""
    for label, opts in fieldsets:
        if str(label) == group_name:
            # Flatten tuples (e.g. ("is_public", "is_cloneable")) to a flat list
            flat_fields = []
            for f in opts["fields"]:
                if isinstance(f, (list, tuple)):
                    flat_fields.extend(f)
                else:
                    flat_fields.append(f)
            for field in expected_fields:
                assert field in flat_fields, (
                    f"Field '{field}' missing from '{group_name}'. "
                    f"Fields present: {flat_fields}"
                )
            return
    raise AssertionError(f"Fieldset group '{group_name}' not found")


def assert_html_contains_tab(content, tab_label):
    """Assert that HTML *content* contains a tab with the given label text."""
    assert tab_label in content, (
        f"Expected tab '{tab_label}' not found in response content"
    )


def assert_no_save_ordering_button(content):
    """Assert the response body has no visible 'Save ordering' control.

    The auto-save implementation uses JavaScript instead of a submit button,
    so the phrase 'save ordering' must not appear as user-visible text at all.
    """
    assert "save ordering" not in content.lower(), (
        "Found an unexpected 'Save ordering' control in the template"
    )
