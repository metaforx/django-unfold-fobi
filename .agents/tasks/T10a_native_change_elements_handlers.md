# Task T10a - Native Change View Usability: Elements and Handlers

Goal
- Make native Unfold change view usable at:
  - `/admin/unfold_fobi/formentryproxy/<id>/change/`
- Restore full builder operations inside native change flow:
  - Form elements: add, edit, delete, sort.
  - Form handlers: add, edit, delete, custom handler actions.

Why this task exists
- Current POC direction is not usable without element/handler management on native change page.
- This is a hard usability gate for T10, not optional polish.

Suggested Skills
- Primary: `$unfold-dev-advanced`.
- Debug fallback: `$unfold-debug-refactor`.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires `T10_native_unfold_admin_poc.md`.
- Reuse T03/T04/T09 test baseline as regression guard.

Phase 0 (Mandatory): Detailed Analysis Before Code
- Create analysis note: `.agents/reviews/feat-t10-native-unfold-poc__T10a-analysis.md`.
- Analysis must answer:
  - Which existing builder pieces are required for element/handler parity?
  - Which pieces can be reused directly in native `change_form_template`?
  - Which pieces can be removed (custom `edit/<id>/` route, custom tab view plumbing)?
  - What is the minimal integration design that keeps complexity lower than current builder implementation?

Scope
- Integrate Elements and Handlers into native `formentryproxy` change page.

Elements requirements (mandatory)
- Add functionality:
  - Show available element plugins (same permission/availability rules as Fobi).
  - Add action must use existing Fobi plugin add flow.
- Edit functionality:
  - Edit existing element plugin config using existing Fobi edit endpoints.
  - Use only fields consistent with public Fobi plugin edit surface (no raw internal admin-only fields).
- Delete functionality:
  - Delete action available per element with existing permissions.
- Sorting functionality:
  - Reorder elements on native change page and persist position updates.
  - Preserve existing ordering validation behavior.

Handlers requirements (mandatory)
- Add functionality:
  - Show available handlers with single-use plugin constraints respected.
- Edit/Delete functionality:
  - Manage existing handlers from native change context.
- Custom actions:
  - Preserve handler custom actions previously available from builder (including entries flow behavior).

Implementation constraints
- Keep native add/change as primary flow (`/add/`, `/<id>/change/`).
- Do not reintroduce a full custom standalone builder page if avoidable.
- Reuse existing Fobi endpoints and helper utilities for plugin operations.
- Minimize monkey patching: any new patch must be justified in analysis and tied to unavoidable plugin behavior.
- Prefer targeted template/admin integration over duplicating full custom view logic.

Deliverables
- `.agents/reviews/feat-t10-native-unfold-poc__T10a-analysis.md`.
- Native change page integration for elements + handlers.
- Tests for add/edit/delete/sort flows from native change page.
- Complexity delta note (what custom code was removed vs. retained and why).

Acceptance Criteria
- On `/admin/unfold_fobi/formentryproxy/<id>/change/`, elements can be added, edited, deleted, and sorted.
- On the same page, handlers can be added and managed with previous builder parity.
- Plugin edit forms use Fobi-compatible field surface (no regression to unusable raw forms).
- No regression in permissions and URL compatibility behavior.
- Net complexity is reduced or unchanged with explicit justification (must not increase silently).
- `poetry run pytest -q` passes.

Tests to run
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent) focused on native change interactions.

Definition of Done
- T10a usability gate is met on native change page.
- Analysis and implementation record clearly justify remaining non-native pieces.