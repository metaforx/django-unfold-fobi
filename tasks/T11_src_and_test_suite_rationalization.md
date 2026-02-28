# Task T11 - Source/Function Necessity Audit and Test Suite Rationalization

Goal
- Validate whether `unfold_fobi` still needs all current custom code after T10-series integration.
- Reduce maintenance surface by preferring native Django admin + Unfold behavior.
- Rebalance test scope toward high-value integration checks (not excessive duplication).

Requested direction
- Analyze each file and function in `src/unfold_fobi` for necessity.
- Verify which tests are truly needed now.
- Keep strong coverage for:
  - form creation,
  - REST Framework submit validation/storage path,
  - Playwright verification that created values appear in expected locations.
- Add only additional view checks that provide clear regression value.

Suggested Skills
- Primary: `$unfold-dev-advanced`.
- Review: `$unfold-codex-reviewer`.
- Debug fallback: `$unfold-debug-refactor`.

Dependencies
- Run after T10a-T10g baseline is stabilized.

Phase 0 (Mandatory): Full Audit Before Refactor
- Create analysis note: `reviews/development-integrated__T11-analysis.md`.
- For every file in `src/unfold_fobi`:
  - list purpose and ownership,
  - list every function/class/method,
  - classify each item as:
    - `KEEP_NATIVE` (aligned with Django/Unfold default usage),
    - `KEEP_CUSTOM_REQUIRED` (unavoidable integration logic),
    - `SIMPLIFY` (can be reduced),
    - `REMOVE` (obsolete).
- Include special focus on:
  - `admin.py`,
  - `views.py`,
  - `apps.py` monkey patches,
  - template overrides and custom JS/CSS.

Phase 1: Refactor Plan (No big-bang rewrite)
- Produce a staged plan that removes or simplifies highest-cost custom code first.
- Prioritize eliminating duplicate logic where Django/Unfold already provides behavior.
- Keep URL/permission/plugin behavior intact during simplification.

Phase 2: Test Suite Rationalization
- Inventory current tests and group by user value:
  - `CRITICAL` (must keep),
  - `USEFUL` (keep if low cost),
  - `REDUNDANT` (consolidate/remove).
- Build a lean baseline test matrix:
  - Form creation flow (admin/native path).
  - REST submit flow and saved data verification.
  - Playwright scenario asserting created data appears where expected.
  - Additional high-value view checks (recommended):
    - native change page loads with elements/handlers sections,
    - element edit open path (popup/modal contract),
    - sortable elements persistence,
    - handler custom action visibility (e.g. entries link).
- Remove/merge tests that only duplicate lower-level assertions without regression value.

Scope
- Code and tests inside repo only.
- Keep behavior stable while reducing complexity.

Non-goals
- No redesign of Fobi plugin architecture.
- No unrelated UI redesign.
- No weakening of critical integration coverage.

Deliverables
- `reviews/development-integrated__T11-analysis.md` with per-file/per-function decision table.
- Implementation PR/commits for approved simplifications.
- Updated, lean test suite with rationale for removed/consolidated tests.
- Short before/after complexity summary:
  - custom files/functions removed,
  - monkey patches reduced,
  - tests reduced/consolidated.

Acceptance Criteria
- Each file/function in `src/unfold_fobi` has explicit keep/remove rationale.
- Unnecessary custom code is reduced in favor of native Django/Unfold paths.
- Test suite is slimmer but still covers critical create/submit/render flows.
- `poetry run pytest -q` passes.
- Playwright coverage for key end-to-end path passes.

Tests to run
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent for key scenarios).
