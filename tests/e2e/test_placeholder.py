"""T04/T10 – Playwright smoke tests for admin screens.

Verifies:
- Add page loads with grouped fieldset visibility.
- Native change page loads with fieldsets and inlines.
"""


class TestAddPageSmoke:
    """The admin add page must load and show grouped fieldsets."""

    def test_add_page_loads(self, admin_login, live_server):
        page = admin_login
        url = f"{live_server.url}/en/admin/unfold_fobi/formentryproxy/add/"
        page.goto(url)
        assert page.title()

    def test_add_page_has_fieldset_groups(self, admin_login, live_server):
        page = admin_login
        url = f"{live_server.url}/en/admin/unfold_fobi/formentryproxy/add/"
        page.goto(url)

        content = page.content()
        for group in [
            "Basic information",
            "Visibility",
            "Success page",
            "Active dates",
        ]:
            assert group in content, f"Fieldset group '{group}' not visible on add page"


class TestChangePageSmoke:
    """T10: the native change page must load with fieldsets and inlines."""

    def test_change_page_loads(self, admin_login, live_server, form_entry):
        page = admin_login
        url = f"{live_server.url}/en/admin/unfold_fobi/formentryproxy/{form_entry.pk}/change/"
        page.goto(url)
        assert page.title()

    def test_change_page_has_fieldsets(self, admin_login, live_server, form_entry):
        page = admin_login
        url = f"{live_server.url}/en/admin/unfold_fobi/formentryproxy/{form_entry.pk}/change/"
        page.goto(url)
        content = page.content()
        assert "Basic information" in content

    def test_change_page_has_element_inline(self, admin_login, live_server, form_entry):
        page = admin_login
        url = f"{live_server.url}/en/admin/unfold_fobi/formentryproxy/{form_entry.pk}/change/"
        page.goto(url)
        content = page.content()
        assert "Form elements" in content

    def test_change_page_has_handler_inline(self, admin_login, live_server, form_entry):
        page = admin_login
        url = f"{live_server.url}/en/admin/unfold_fobi/formentryproxy/{form_entry.pk}/change/"
        page.goto(url)
        content = page.content()
        assert "Form handlers" in content
