# Task T04 - Playwright UI Smoke for Form Building

Goal
- Introduce early browser-level smoke coverage so UI regressions are caught during each implementation step.

Dependencies
- Requires T01-T03 completed.

Scope
- Add initial Playwright cases for core builder screens:
  - Add view loads and key grouped sections are visible.
  - Edit view loads and main tab/action row renders.
  - Existing completed interactions remain functional (including ordering UX baseline).
- Keep tests small and resilient; extend in later tasks as UI evolves.

Non-goals
- No full visual regression suite.
- No exhaustive matrix yet.

Deliverables
- Playwright suite integrated with test environment.
- Stable smoke tests used as continuous gate for T05-T07.

Acceptance Criteria
- Playwright smoke tests pass locally.
- Failures clearly indicate broken core builder workflow.

Tests to run
- `poetry run pytest -q` (if pytest-playwright)
- or `npx playwright test`
