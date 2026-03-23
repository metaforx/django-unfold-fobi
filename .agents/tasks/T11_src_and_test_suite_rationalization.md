# Task T11 - Source/Function Necessity Audit and Cleanup (Tests Kept Stable)

Goal
- Validate whether `unfold_fobi` still needs all current custom code after T10-series integration.
- Reduce maintenance surface by preferring native Django admin + Unfold behavior.
- Perform cleanup first while keeping current tests stable and passing.

Requested direction
- Analyze each file and function in `src/unfold_fobi` for necessity.
- Reduce/remove unnecessary functionality in source code first.
- Keep existing tests as guardrails during cleanup.
- Only remove tests that are directly tied to functionality removed in this task.

Suggested Skills
- Primary: `$unfold-dev-advanced`.
- Review: `$unfold-codex-reviewer`.
- Debug fallback: `$unfold-debug-refactor`.

Dependencies
- Run after T10a-T10g baseline is stabilized.

Phase 0 (Mandatory): Full Audit Before Refactor
- Create analysis note: `.agents/reviews/development-integrated__T11-analysis.md`.
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

Phase 2: Cleanup Implementation
- Execute source cleanup in small, safe increments.
- Remove dead code, duplicate code paths, and unnecessary patching identified in Phase 0.
- Keep tests unchanged unless a test targets removed functionality.
- For every removed/changed test, document exact functional reason in task notes.

Scope
- Code and tests inside repo only.
- Keep behavior stable while reducing complexity.

Non-goals
- No redesign of Fobi plugin architecture.
- No unrelated UI redesign.
- No weakening of critical integration coverage.

Deliverables
- `.agents/reviews/development-integrated__T11-analysis.md` with per-file/per-function decision table.
- Implementation PR/commits for approved simplifications.
- Existing test suite kept passing during cleanup.
- Minimal test removals only for removed functionality, with rationale.
- Short before/after complexity summary:
  - custom files/functions removed,
  - monkey patches reduced,
  - tests removed only when tied to removed features.

Acceptance Criteria
- Each file/function in `src/unfold_fobi` has explicit keep/remove rationale.
- Unnecessary custom code is reduced in favor of native Django/Unfold paths.
- Existing tests remain green after cleanup.
- Any removed tests are clearly mapped to removed functionality.
- `poetry run pytest -q` passes.
- Playwright suite still passes for current behavior.

Tests to run
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent for key scenarios).