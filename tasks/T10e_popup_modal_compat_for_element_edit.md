# Task T10e - Feasibility: Admin-Popup Style Element Edit/Add (Unfold Modal Compatible)

Goal
- Evaluate and, if feasible, implement form element edit/add flow using Django admin popup mechanics (same pattern as FK related widget popups).
- Keep field behavior and plugin logic identical to current Fobi add/edit element flows.
- Maximize reuse of native Django/Unfold rendering to reduce custom crispy/unfold patching.

Problem context
- Current element edit URL:
  - `http://127.0.0.1:8080/de/admin/fobi/forms/elements/edit/3/`
- Desired UX/contract:
  - Opens like a Django admin related-widget popup.
  - Compatible with `django-unfold-modal` without changing that package.
  - Uses popup mechanism similar to native admin related object workflows.

Reference package
- `https://github.com/metaforx/django-unfold-modal`

Suggested Skills
- Primary: `$unfold-dev-advanced`.
- Debug fallback: `$unfold-debug-refactor`.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires T10a-T10d context.

Phase 0 (Mandatory): Feasibility Analysis First
- Create analysis note: `reviews/feat-t10d-sort-handle-contract__T10e-analysis.md`.
- Analysis checklist:
  - Map current element add/edit request/response flow and URL contracts.
  - Verify which Django admin popup parameters/response patterns are needed for compatibility.
  - Check whether Fobi add/edit element views can be wrapped/adapted to popup contract without changing plugin logic.
  - Evaluate whether element forms can be rendered through native admin/Unfold change-form templates while preserving existing validation/save logic.
  - Identify patches that can be removed if native rendering is adopted.
  - Decide one of:
    - `FEASIBLE_NOW` (implement in T10e),
    - `FEASIBLE_WITH_LIMITS` (documented constraints),
    - `NOT_FEASIBLE` (with concrete blocker and fallback).

Scope
- Feasibility first, then minimal implementation if feasible.
- Target both element edit and add popup behavior from native change page.
- Keep package compatibility goal:
  - No changes to `django-unfold-modal`.

Implementation requirements (if feasible)
- Popup behavior must follow Django admin-like related-widget mechanism.
- Preserve existing Fobi element plugin field set, validation, and save logic.
- Prefer native admin/Unfold rendering path for forms if it does not change business logic.
- Avoid duplicating frontend styling logic already provided by Unfold/admin templates.
- Keep native `FormEntryProxy` change handling primary.

Non-goals
- No plugin architecture changes.
- No broad template rewrites outside scoped popup integration.
- No changes to `django-unfold-modal` package internals.

Deliverables
- `reviews/feat-t10d-sort-handle-contract__T10e-analysis.md` with feasibility decision.
- If feasible: code changes enabling popup-style element add/edit compatibility.
- Tests for popup open/submit/close flow and regression checks for element logic parity.

Acceptance Criteria
- Feasibility decision is documented with technical reasoning and risks.
- If marked feasible:
  - Element add/edit opens via admin-like popup mechanism compatible with modal integration.
  - Existing plugin field behavior/validation/save remains unchanged.
  - Native Unfold/Django rendering is used where possible to reduce custom patching.
- `poetry run pytest -q` passes for updated scope.

Tests to run
- `poetry run pytest -q`
- UI test (Playwright or equivalent) for popup/modal interaction and successful save flow.
