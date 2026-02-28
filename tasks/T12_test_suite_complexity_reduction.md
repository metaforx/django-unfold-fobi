# Task T12 - Code Organization First, Then Test Suite Complexity Reduction

Goal
- Organize code structure first (clear separation of API and non-API layers).
- Then reduce test-suite complexity after structure is stabilized.
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

Phase 0 (Mandatory): Code Organization Before Test Cleanup
- Create analysis note section for code organization in:
  - `reviews/development-integrated__T12-analysis.md`.
- Define and apply module boundaries:
  - keep admin/web views in `views.py`,
  - move DRF endpoints to `api/views.py` (and `api/urls.py` as needed),
  - keep shared business logic in `services.py`.
- Ensure API and internal usage reuse service-layer functions, not DRF view classes.
- Update imports/URL wiring with no behavioral regression.

Phase 1 (Mandatory): Test Inventory and Value Classification
- Create analysis note: `reviews/development-integrated__T12-analysis.md`.
- Classify existing tests:
  - `KEEP_CRITICAL`,
  - `KEEP_USEFUL`,
  - `MERGE`,
  - `REMOVE_REDUNDANT`.
- For each `MERGE` or `REMOVE_REDUNDANT`, provide explicit reason and replacement coverage mapping.

Phase 2: Simplification Implementation
- Consolidate duplicate tests with overlapping assertions.
- Prefer fewer broader integration tests over many narrow duplicates.
- Keep assertions focused on user-visible outcomes and integration contracts.
- Remove brittle checks that do not protect meaningful behavior.

Phase 3: Coverage Validation
- Validate retained tests still protect core paths.
- Ensure no coverage gap on create/submit/render popup/sort contracts.

Non-goals
- No weakening of critical integration confidence.

Deliverables
- `reviews/development-integrated__T12-analysis.md`.
- Code organization changes separating API and non-API view layers.
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
