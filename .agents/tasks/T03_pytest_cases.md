# Task T03 - Pytest Baseline for Current Builder Behavior

Goal
- Establish backend regression tests early for what is already implemented.

Suggested Skills
- Primary: `$unfold-dev-structured` (well-scoped backend test creation).
- Debug fallback: `$unfold-debug-cleanup` for flaky/failing test triage.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires T01-T02 completed.

Scope
- Add focused pytest coverage for current behavior:
  - Add view loads and fieldsets include grouped sections + date section.
  - Edit view route resolves and is permission-protected.
  - Edit template renders tabs container and expected tab labels.
  - "Save ordering" action is absent; ordering POST path behaves as expected.
  - Core translated labels/messages exist for custom admin/view strings.
  - DB-store "view entries" route (`/fobi/<form_id>/`) shows submitted rows when data is created via DRF (`PUT /api/fobi-form-entry/<slug>/`).
- Add pending-contract tests (xfail until T06/T08 implementation):
  - Edit breadcrumb follows proxy contract (`Unfold_Fobi -> Forms (builder) -> <form title>`), not legacy `Fobi -> Form entries -> ...`.
  - Edit save action follows Unfold submit-row convention.
- Add reusable assertions/helpers for later tasks (T05-T09).

Non-goals
- No browser automation.
- No refactor of UI code in this task.

Deliverables
- Pytest modules covering current baseline behavior.
- Stable fixtures/assertion helpers reused by subsequent tasks.

Acceptance Criteria
- `poetry run pytest -q` passes.
- Tests fail when current baseline contracts regress.

Tests to run
- `poetry run pytest -q`