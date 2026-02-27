"""T04 – Playwright smoke tests for builder screens.

Verifies:
- Add page loads with grouped fieldset visibility.
- Edit page loads with tab row and expected tab labels.
- Legend/action area renders in each main tab.
- No manual "Save ordering" control is visible.
"""
import pytest

# ---------------------------------------------------------------------------
# Add-view smoke tests
# ---------------------------------------------------------------------------

class TestAddPageSmoke:
    """The admin add page must load and show grouped fieldsets."""

    def test_add_page_loads(self, admin_login, live_server):
        page = admin_login
        url = f"{live_server.url}/admin/unfold_fobi/formentryproxy/add/"
        page.goto(url)
        assert page.title()  # page rendered

    def test_add_page_has_fieldset_groups(self, admin_login, live_server):
        page = admin_login
        url = f"{live_server.url}/admin/unfold_fobi/formentryproxy/add/"
        page.goto(url)

        content = page.content()
        for group in ["Basic information", "Visibility", "Success page", "Active dates"]:
            assert group in content, f"Fieldset group '{group}' not visible on add page"


# ---------------------------------------------------------------------------
# Edit-view smoke tests
# ---------------------------------------------------------------------------

class TestEditPageSmoke:
    """The edit page must load and show the tab row."""

    def test_edit_page_loads(self, admin_login, live_server, form_entry):
        page = admin_login
        url = f"{live_server.url}/admin/unfold_fobi/formentryproxy/edit/{form_entry.pk}/"
        page.goto(url)
        # The edit page may not set a <title>; verify the tabs container loaded.
        assert page.locator("#tabs-alpine").count() == 1

    def test_edit_page_has_tabs_container(self, admin_login, live_server, form_entry):
        page = admin_login
        url = f"{live_server.url}/admin/unfold_fobi/formentryproxy/edit/{form_entry.pk}/"
        page.goto(url)

        tabs = page.locator("#tabs-alpine")
        assert tabs.count() == 1

    def test_edit_page_has_tab_labels(self, admin_login, live_server, form_entry):
        page = admin_login
        url = f"{live_server.url}/admin/unfold_fobi/formentryproxy/edit/{form_entry.pk}/"
        page.goto(url)

        tab_items = page.locator("#tabs-items li")
        labels = [tab_items.nth(i).inner_text() for i in range(tab_items.count())]
        assert "Elements" in labels
        assert "Handlers" in labels
        assert "Properties" in labels


class TestEditTabLegends:
    """Each main tab must render a legend/action area."""

    @pytest.fixture()
    def edit_page(self, admin_login, live_server, form_entry):
        page = admin_login
        url = f"{live_server.url}/admin/unfold_fobi/formentryproxy/edit/{form_entry.pk}/"
        page.goto(url)
        return page

    def test_elements_tab_has_legend(self, edit_page):
        legend = edit_page.locator("#form_elements")
        assert legend.count() == 1
        assert "Change form elements" in legend.inner_text()

    def test_handlers_tab_has_legend(self, edit_page):
        # Click handlers tab to reveal content
        edit_page.locator("#tabs-items li").nth(1).click()
        legend = edit_page.locator("#form_handlers")
        assert legend.count() == 1
        assert "Change form handlers" in legend.inner_text()

    def test_properties_tab_has_legend(self, edit_page):
        # Click properties tab to reveal content
        edit_page.locator("#tabs-items li").nth(2).click()
        legend = edit_page.locator("#form_properties")
        assert legend.count() == 1
        assert "Change form properties" in legend.inner_text()

    def test_elements_tab_has_action_area(self, edit_page):
        actions = edit_page.locator("#tab-form-elements .fobi-actions")
        assert actions.count() >= 1


class TestNoSaveOrderingControl:
    """No visible 'Save ordering' button should exist."""

    def test_no_save_ordering_button(self, admin_login, live_server, form_entry):
        page = admin_login
        url = f"{live_server.url}/admin/unfold_fobi/formentryproxy/edit/{form_entry.pk}/"
        page.goto(url)

        content = page.content().lower()
        assert "save ordering" not in content
