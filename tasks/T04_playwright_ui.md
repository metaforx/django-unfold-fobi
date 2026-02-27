# Task T04 - Playwright Smoke Baseline for Builder Screens

Goal
- Establish early browser-level regression checks for existing add/edit builder flows.

Suggested Skills
- Primary: `$unfold-dev-structured` (targeted UI smoke test additions).
- Debug fallback: `$unfold-debug-cleanup` for selector/timing instability.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires T01-T03 completed.

Scope
- Add smoke tests for:
  - Add page load and grouped fieldset visibility.
  - Edit page load and tab row visibility.
  - Legend/action area rendering in each main tab.
  - Absence of manual "Save ordering" control.
- Keep tests resilient and minimal; expand in T06/T08.

Non-goals
- No visual snapshot suite.
- No exhaustive matrix yet.

Deliverables
- Playwright smoke tests integrated with local test stack.

Acceptance Criteria
- Playwright smoke suite passes locally.
- Failures are actionable and map to builder workflow regressions.

Tests to run
- `poetry run pytest -q` (if pytest-playwright)
- or `npx playwright test`
