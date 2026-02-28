# Task T12 - Test Suite Complexity Reduction (Post-Cleanup)

Goal
- Reduce test-suite complexity after T11 cleanup is complete and stable.
- Keep strong, high-value integration coverage while removing redundant assertions.

Prerequisite
- T11 completed.
- Source cleanup merged and tests stable.

Priority coverage to keep
- Form creation (native admin/unfold flow).
- REST Framework submit and stored data verification.
- Playwright end-to-end check that created/submitted values appear in correct locations.
- Additional high-value checks:
  - native change page renders elements/handlers context correctly,
  - element edit open path (popup/modal contract),
  - sortable element persistence,
  - handler custom action visibility where applicable.

Suggested Skills
- Primary: `$unfold-dev-advanced`.
- Review: `$unfold-codex-reviewer`.
- Debug fallback: `$unfold-debug-refactor`.

Phase 0 (Mandatory): Test Inventory and Value Classification
- Create analysis note: `reviews/development-integrated__T12-analysis.md`.
- Classify existing tests:
  - `KEEP_CRITICAL`,
  - `KEEP_USEFUL`,
  - `MERGE`,
  - `REMOVE_REDUNDANT`.
- For each `MERGE` or `REMOVE_REDUNDANT`, provide explicit reason and replacement coverage mapping.

Phase 1: Simplification Implementation
- Consolidate duplicate tests with overlapping assertions.
- Prefer fewer broader integration tests over many narrow duplicates.
- Keep assertions focused on user-visible outcomes and integration contracts.
- Remove brittle checks that do not protect meaningful behavior.

Phase 2: Coverage Validation
- Validate retained tests still protect core paths.
- Ensure no coverage gap on create/submit/render popup/sort contracts.

Non-goals
- No source-feature refactors (belongs to T11 or later source tasks).
- No weakening of critical integration confidence.

Deliverables
- `reviews/development-integrated__T12-analysis.md`.
- Simplified test suite with explicit mapping of removed/merged tests.
- Short before/after metrics:
  - test count,
  - runtime impact,
  - critical-flow coverage map.

Acceptance Criteria
- Redundant tests are reduced with documented rationale.
- Critical create/submit/playwright integration coverage remains intact.
- `poetry run pytest -q` passes.
- Playwright coverage for critical user flow passes.

Tests to run
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent for critical scenarios).
