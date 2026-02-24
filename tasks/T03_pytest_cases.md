# Task T03 - Pytest Cases for Early Verification

Goal
- Establish Django/pytest verification early so every later implementation task can be validated immediately.

Dependencies
- Requires T01-T02 completed.

Scope
- Add focused pytest coverage for current `unfold_fobi` behavior:
  - Add view availability and grouped sections baseline.
  - Edit view routing/permissions baseline.
  - Presence of existing completed UX behaviors (for example, no "Save ordering").
- Set up reusable fixtures/helpers for form-builder checks.
- Organize tests so later tasks (T05-T07) extend assertions instead of rewriting setup.

Non-goals
- No browser automation.
- No major UI refactor in this task.

Deliverables
- Pytest modules under `tests/` with stable baseline coverage.
- Clear test structure ready for incremental additions in subsequent tasks.

Acceptance Criteria
- `pytest -q` passes.
- Tests are runnable after each following task as a verification gate.

Tests to run
- `poetry run pytest -q`
