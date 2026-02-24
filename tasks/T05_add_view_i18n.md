# Task T05 - Add View i18n Completion

Goal
- Complete i18n coverage and UX consistency for `FormEntryProxy` add view.

Dependencies
- Requires T03-T04 passing before and after changes.

Scope
- Audit add-view template/admin/view strings introduced by `unfold_fobi`.
- Wrap missing user-facing labels/help text/section titles/buttons in translation functions.
- Keep existing fieldset grouping and date/time grouping unchanged.
- Verify extractability for locale workflows.
- Extend pytest/Playwright assertions created in T03-T04 for the updated i18n behavior.

Non-goals
- No edit-view tab restructuring.
- No behavioral changes to add-form save logic.

Deliverables
- Add-view strings fully translation-ready.
- Tests updated to verify i18n-ready rendering.

Acceptance Criteria
- Add-view custom strings are i18n-wrapped.
- `makemessages` (or equivalent extraction) detects new strings.
- Existing T03-T04 suites remain green.

Tests to run
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent)
