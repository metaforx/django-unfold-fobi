# Task T06 - Edit View Structure, Header, Tabs, Breadcrumb Contract

Goal
- Finalize edit-view structure to match Unfold custom-page and tab expectations from `UNFOLD_FOBI_PLAN`.

Suggested Skills
- Primary: `$unfold-dev-advanced` (cross-template/view/JS refactor and behavior contract work).
- Debug fallback: `$unfold-debug-refactor` when tab/header/breadcrumb issues require deeper structural debugging.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires T03-T04 passing before and after changes.

Context from code back-check
- Edit view already uses Unfold mixin but has legacy tab residue (`tab-links` and dead `#tabs` JS logic).
- H1 removal and breadcrumb contract are not explicitly guaranteed.

Scope
- Ensure edit page structure is explicitly Unfold-custom-page compliant.
- Remove/neutralize H1 title rendering path if still present.
- Replace remaining tab legacy residue with clean Unfold tab semantics/classes.
- Ensure active tab state and accessibility attributes are correct.
- Implement breadcrumb contract:
  - `Unfold_Fobi -> Forms (builder) -> <form name>`
- Remove dead tab JS behavior that depends on obsolete DOM patterns.
- Extend T03/T04 tests for these contracts.

Non-goals
- Full action-grid redesign (handled in T07).

Deliverables
- Updated edit-view structure/tab/breadcrumb implementation.
- Regression tests for tab/header/breadcrumb behavior.

Acceptance Criteria
- Edit view matches required Unfold structure.
- Breadcrumbs and active item behave as specified.
- T03-T04 suites remain green with added assertions.

Tests to run
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent)
