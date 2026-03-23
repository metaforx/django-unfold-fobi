# Task T05b - Unfold Multi-Language Switcher Enablement

Goal
- Enable language switching in the Unfold admin UI according to official Unfold multi-language configuration.
- Ensure the test project supports `/en/admin/` and `/de/admin/` flows with a visible language switcher.

Suggested Skills
- Primary: `$unfold-dev-structured` (settings/URL/i18n wiring and regression checks).
- Debug fallback: `$unfold-debug-cleanup` for middleware/URL/i18n integration issues.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires T05/T05a localization groundwork (translations and test-project locale setup).

Scope
- Update Django i18n routing for language-prefixed admin paths:
  - Add `path("i18n/", include("django.conf.urls.i18n"))` for language switching endpoint.
  - Ensure this `i18n/` route is not inside `i18n_patterns`.
  - Wrap admin URLs in `i18n_patterns(...)` to expose language-prefixed admin routes.
- Align settings with multi-language support:
  - `LocaleMiddleware` enabled and ordered correctly.
  - `USE_I18N = True`.
  - `LANGUAGE_CODE` default set.
  - `LANGUAGES` includes at least English and German.
- Configure Unfold language selector:
  - Set `UNFOLD["SHOW_LANGUAGES"] = True`.
  - Optionally define `UNFOLD["LANGUAGES"]["navigation"]` override only if custom language list/order is needed.
- Add/extend tests:
  - Verify `/admin/` redirects/serves with language prefix behavior.
  - Verify `/en/admin/` and `/de/admin/` are reachable for authenticated admin users.
  - Verify language switch endpoint (`/i18n/setlang/`) exists and changes active language.
  - Add a UI-level assertion (Playwright) that language switcher is visible in admin header.

Non-goals
- No translation content rewrite beyond required language-switcher wiring.
- No redesign of admin header/navigation beyond enabling built-in switcher.

Deliverables
- URL configuration updated for language-prefixed admin and set-language endpoint.
- Settings updated for Unfold/Django multi-language handling.
- Regression tests for route and switcher behavior.

Acceptance Criteria
- Language switcher is visible in Unfold admin.
- Admin is accessible via `/en/admin/` and `/de/admin/`.
- Language change via `/i18n/` endpoint works.
- `poetry run pytest -q` remains green.

Tests to run
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent)

Reference
- https://unfoldadmin.com/docs/configuration/multi-language/