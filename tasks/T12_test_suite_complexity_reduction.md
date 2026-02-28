# Task T12 - Code Organization First, Then Test Suite Complexity Reduction

Goal
- Organize code structure first (clear separation of API and non-API layers).
- Perform a thorough code cleanup across `src/unfold_fobi` during this restructuring step.
- Then reduce test-suite complexity after structure is stabilized.
- Include Ruff-based code cleanup as part of the implementation quality gate.
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
- Re-check necessity of remaining modules/functions after T11 cleanup, explicitly including:
  - `context_processors.py` (`admin_site`, title mappings, and any Unfold/Fobi context bridge),
  - `views.py`, `api/views.py`,
  - `forms.py`,
  - `services.py`,
  - `admin.py` and template override hooks.
- For each file/function, classify:
  - `KEEP`,
  - `SIMPLIFY`,
  - `REMOVE`,
  with concrete reason tied to current behavior.
- Include explicit cleanup targets:
  - dead/unused functions, filters, tags, and helper classes,
  - obsolete template overrides/snippets no longer on active routes,
  - stale imports/compat shims/patch code not needed after T10/T11,
  - duplicated logic that can be replaced by native Django/Unfold behavior.
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
- Execute thorough code cleanup based on Phase 0 decisions before test reduction work.
- Consolidate duplicate tests with overlapping assertions.
- Prefer fewer broader integration tests over many narrow duplicates.
- Keep assertions focused on user-visible outcomes and integration contracts.
- Remove brittle checks that do not protect meaningful behavior.
- Run Ruff cleanup on changed code paths:
  - apply safe autofixes where appropriate,
  - resolve remaining lint issues explicitly.

Phase 3: Coverage Validation
- Validate retained tests still protect core paths.
- Ensure no coverage gap on create/submit/render popup/sort contracts.

Non-goals
- No weakening of critical integration confidence.

Deliverables
- `reviews/development-integrated__T12-analysis.md`.
- Code organization changes separating API and non-API view layers.
- Thorough cleanup changes across `src/unfold_fobi` with keep/remove rationale.
- Simplified test suite with explicit mapping of removed/merged tests.
- Ruff cleanup updates for touched files/modules.
- Short before/after metrics:
  - test count,
  - runtime impact,
  - critical-flow coverage map,
  - Ruff issue count delta (before/after for scoped files).

Acceptance Criteria
- Thorough cleanup is completed for scoped `src/unfold_fobi` modules with documented rationale.
- Redundant tests are reduced with documented rationale.
- Critical create/submit/playwright integration coverage remains intact.
- Ruff checks pass for project scope used in this task.
- `poetry run pytest -q` passes.
- Playwright coverage for critical user flow passes.

Tests to run
- `poetry run ruff check src tests`
- `poetry run ruff format --check src tests`
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent for critical scenarios).
