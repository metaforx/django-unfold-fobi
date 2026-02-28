"""T05b – Playwright tests for language switcher visibility and behavior.

Verifies:
- Language switcher is visible in the Unfold admin header/sidebar.
- Admin loads under both /en/ and /de/ language prefixes.
"""


class TestLanguageSwitcherVisible:
    """The Unfold admin must show language switching forms."""

    def test_language_switcher_present(self, admin_login, live_server):
        page = admin_login
        # Unfold renders each language as a <form> with a hidden
        # <input name="language"> that posts to the set_language endpoint.
        switcher_forms = page.locator("form input[name='language'][type='hidden']")
        assert switcher_forms.count() >= 1, (
            "Language switcher forms not found in admin UI"
        )

    def test_switcher_contains_german_option(self, admin_login, live_server):
        page = admin_login
        de_input = page.locator("input[name='language'][value='de']")
        assert de_input.count() >= 1, "German language option not found in switcher"

    def test_switcher_contains_english_option(self, admin_login, live_server):
        page = admin_login
        en_input = page.locator("input[name='language'][value='en']")
        assert en_input.count() >= 1, "English language option not found in switcher"


class TestLanguagePrefixedPages:
    """Admin pages must load under both language prefixes."""

    def test_de_admin_loads(self, admin_login, live_server):
        page = admin_login
        page.goto(f"{live_server.url}/de/admin/")
        assert page.url.endswith("/de/admin/")
        assert page.title()

    def test_en_admin_loads(self, admin_login, live_server):
        page = admin_login
        page.goto(f"{live_server.url}/en/admin/")
        assert page.url.endswith("/en/admin/")
        assert page.title()
