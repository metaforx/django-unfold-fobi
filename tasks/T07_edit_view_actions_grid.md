# Task T07 - Edit View Actions Alignment and Grid/Card Completion

Goal
- Complete remaining action placement and layout styling goals for edit builder.

Suggested Skills
- Primary: `$unfold-dev-advanced` (complex UI alignment and layout refactor across builder sections).
- Debug fallback: `$unfold-debug-refactor` for multi-step regressions in actions/layout behavior.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires T03-T04 passing before and after changes.

Context from code back-check
- "Add form element" control currently lives in legend/action area, not clearly in top tab/nav row.
- Handler section still uses changelist-style rendering; target is Unfold grid/card presentation.

Scope
- Move/align "Add form element" control to required tab/nav row placement.
- Ensure all edit-view actions use consistent Unfold button/select/dropdown styles.
- Replace remaining table/changelist-like builder presentation with Unfold-style grid/cards where required.
- Preserve ordering auto-save behavior and existing functional flows.
- Extend T03/T04 suites with action/layout regression assertions.

Non-goals
- No new builder business features.
- No API contract changes.

Deliverables
- Finalized action alignment and grid/card presentation.
- Regression tests covering finalized UX behavior.

Acceptance Criteria
- Action controls and placement match `UNFOLD_FOBI_PLAN` goals.
- Remaining legacy table-style presentation is removed from scoped builder sections.
- T03-T04 suites remain green.

Tests to run
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent)
