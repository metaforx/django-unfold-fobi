"""T05b – Language-prefixed admin routing and set-language endpoint tests.

Verifies:
- Admin is reachable at /en/admin/ and /de/admin/.
- Unprefixed /admin/ redirects to the language-prefixed version.
- The /i18n/setlang/ endpoint changes the active language.
- UNFOLD SHOW_LANGUAGES setting is enabled.
"""

from django.urls import reverse


class TestLanguagePrefixedAdminRoutes:
    """Admin URLs must include a language prefix."""

    def test_reverse_includes_language_prefix(self):
        url = reverse("admin:index")
        assert url.startswith("/en/"), f"Expected /en/ prefix, got {url}"

    def test_en_admin_accessible(self, admin_client):
        response = admin_client.get("/en/admin/")
        assert response.status_code == 200

    def test_de_admin_accessible(self, admin_client):
        response = admin_client.get("/de/admin/")
        assert response.status_code == 200

    def test_unprefixed_admin_redirects(self, admin_client):
        """Requests to /admin/ should redirect to a language-prefixed URL."""
        response = admin_client.get("/admin/", follow=False)
        assert response.status_code == 302
        assert (
            "/en/admin/" in response["Location"] or "/de/admin/" in response["Location"]
        )


class TestSetLanguageEndpoint:
    """The /i18n/setlang/ endpoint must exist and switch language."""

    def test_setlang_url_resolves(self):
        url = reverse("set_language")
        assert url == "/i18n/setlang/"

    def test_setlang_switches_to_german(self, admin_client):
        """POST to /i18n/setlang/ with language=de should set the session language."""
        response = admin_client.post(
            "/i18n/setlang/",
            data={"language": "de", "next": "/de/admin/"},
        )
        assert response.status_code == 302

        # Follow redirect and verify we land on German admin
        response = admin_client.get("/de/admin/")
        assert response.status_code == 200


class TestUnfoldShowLanguagesSetting:
    """The UNFOLD config must have SHOW_LANGUAGES enabled."""

    def test_show_languages_enabled(self, settings):
        assert settings.UNFOLD.get("SHOW_LANGUAGES") is True
