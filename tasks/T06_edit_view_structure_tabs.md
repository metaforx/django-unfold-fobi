# Task T06 - Edit View Structure and Tabs

Goal
- Finalize Unfold-native edit page structure for form builder.

Dependencies
- Requires T03-T04 passing before and after changes.

Scope
- Ensure edit page is rendered as an Unfold custom page pattern.
- Remove H1 and keep H2/legend placement consistent.
- Replace remaining legacy/jQuery tab structure with Unfold native tab markup/classes.
- Ensure active tab state is correctly reflected and accessible.
- Update breadcrumbs to target structure: `Unfold_Fobi -> Forms (builder) -> <form name>`.
- Extend T03/T04 tests to cover new structure/tab/breadcrumb behavior.

Non-goals
- No table/grid visual overhaul beyond what is required for tab/layout correctness.

Deliverables
- Updated edit-view templates and supporting view context.
- Updated tests for tab and breadcrumb regressions.

Acceptance Criteria
- Edit page shows correct Unfold tab UX and active state.
- Breadcrumb chain and active item match expected structure.
- T03-T04 suites stay green with new assertions.

Tests to run
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent)
