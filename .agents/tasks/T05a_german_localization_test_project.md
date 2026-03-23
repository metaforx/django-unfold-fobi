# Task T05a - German Localization Setup for Test Project

Goal
- Add German (`de`) localization support to the Django test project via `tests/server/testapp/settings.py`.
- Provide German translations for existing `unfold_fobi` user-facing strings.

Suggested Skills
- Primary: `$unfold-dev-structured` (bounded i18n/config + test updates).
- Debug fallback: `$unfold-debug-cleanup` for gettext/compile/test regressions.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires T05 baseline i18n audit completed (or in progress with green tests).

Scope
- Configure localization in test project settings:
  - Add `LocaleMiddleware` in correct middleware order.
  - Define language config for German support (`LANGUAGE_CODE`, `LANGUAGES`, optional `LOCALE_PATHS` as needed).
- Add German locale catalog for `unfold_fobi`:
  - Create/update `src/unfold_fobi/locale/de/LC_MESSAGES/django.po`.
  - Translate existing app strings currently present in locale catalogs/templates/admin/view labels.
- Compile messages so German translations are effective at runtime.
- Extend/adjust tests to verify German localization behavior in scoped areas.

Non-goals
- No edit-view layout refactor.
- No permission-model changes.
- No broad content rewrite beyond existing user-facing strings.

Deliverables
- Test project localization settings updated for German support.
- German translation catalog with translated existing strings.
- Message compilation step documented and reproducible.
- Regression tests covering German localization in scope.

Acceptance Criteria
- Test project can run with German localization enabled.
- Existing `unfold_fobi` scoped strings have German translations in `de` catalog.
- Runtime translation path is validated (compiled messages and passing tests).
- `poetry run pytest -q` remains green.

Tests to run
- `poetry run pytest -q`
- `poetry run python tests/server/manage.py compilemessages -l de`