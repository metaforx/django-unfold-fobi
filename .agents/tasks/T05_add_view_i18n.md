# Task T05 - Add View i18n Audit and Completion

Goal
- Close remaining add-view i18n gaps and verify extraction workflow.

Suggested Skills
- Primary: `$unfold-dev-structured` (bounded i18n + test updates).
- Debug fallback: `$unfold-debug-cleanup` for extraction/test regressions.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires T03-T04 passing before and after changes.

Scope
- Audit add-view user-facing strings across:
  - `FormEntryProxyAdmin` fieldset labels/messages.
  - Add-view templates and related UI labels.
- Wrap any missing strings with Django i18n helpers.
- Define and run extraction verification (`makemessages` workflow) for changed strings.
- Extend pytest/Playwright assertions where practical.

Non-goals
- No edit-view layout refactor.

Deliverables
- Add-view strings translation-ready.
- Extraction verification documented and reproducible.
- Regression tests updated.

Acceptance Criteria
- Add-view custom strings are i18n-wrapped.
- Extraction command discovers expected strings.
- T03-T04 suites remain green.

Tests to run
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent)