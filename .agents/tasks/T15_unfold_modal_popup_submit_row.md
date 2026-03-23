# Task T15 - Unfold Submit Row for Popup Modal Element/Handler Forms

Goal
- Restore a visible, usable save/submit action for Fobi add/edit forms opened inside `django-unfold-modal`.
- Make popup-based add element / add handler flows use the same submit-row pattern users expect from native Unfold admin forms.
- Keep the popup/modal workflow intact without introducing custom modal-specific save mechanics.

Problem statement
- Current popup forms opened from:
  - `Add element`
  - `Add handler`
  - related edit flows for elements/handlers
  are rendered inside Unfold modal iframes without a visible submit/save row.
- Result:
  - users can open modal forms,
  - fields are visible,
  - but there is no obvious save action in the modal UI.
- This is a blocking usability issue for the modal-based workflow.

Requested outcome
1. Add the same submit-row pattern used by Unfold admin forms
- Popup forms rendered in modal context should expose a clear save action row.
- Prefer reusing Unfold/Django admin submit-row conventions instead of inventing a custom footer.

2. Cover both element and handler popup forms
- Must work for:
  - add element,
  - edit element,
  - add handler,
  - edit handler.

3. Keep popup compatibility behavior intact
- Existing popup close/reload behavior after successful save must continue to work.
- Do not break `_popup=1` semantics or `django-unfold-modal` integration.

4. Keep implementation package-local
- Fix this in `unfold_fobi`.
- Do not require changes in `django-unfold-modal`.
- Avoid patching third-party Fobi templates more broadly than necessary.

Suggested Skills
- Primary: `$unfold-dev-advanced`.
- Debug fallback: `$unfold-debug-refactor`.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires T10e/T10f/T10g popup and modal compatibility baseline.
- Reuse current popup response behavior and Fobi theme override structure already present in `unfold_fobi`.

Phase 0 (Mandatory): Analysis Before Changes
- Create analysis note: `.agents/reviews/development-integrated__T15-analysis.md`.
- Analysis checklist:
  - Identify which templates render add/edit element and handler popup forms.
  - Confirm why submit controls are missing in modal popup rendering.
  - Compare current popup form structure against native Unfold change/add form submit-row structure.
  - Determine the minimal override point:
    - Fobi theme template override,
    - form helper/layout change,
    - or admin-compatible template include.
  - Confirm whether add and edit flows share the same template path or need separate handling.

Implementation requirements
- Reuse existing Unfold submit-row styling/pattern where possible.
- Keep the popup UI compact and consistent with modal usage.
- Ensure save/submit controls render only once.
- Preserve cancel/close behavior if already present.
- Avoid introducing JS-only save actions when a normal form submit can be preserved.

Scope
- Popup/modal add/edit forms for Fobi elements and handlers inside `unfold_fobi`.
- Related template overrides, form rendering helpers, and tests.

Non-goals
- No redesign of modal title behavior.
- No changes to modal container chrome in `django-unfold-modal`.
- No broad rewrite of all Fobi templates.
- No unrelated admin polish work.

Deliverables
- `.agents/reviews/development-integrated__T15-analysis.md`.
- Template/form rendering changes so popup modal forms show Unfold-style submit controls.
- Coverage for add/edit element and handler modal form rendering/submission behavior.

Acceptance Criteria
- Add element modal shows a visible save/submit row.
- Edit element modal shows a visible save/submit row.
- Add handler modal shows a visible save/submit row.
- Edit handler modal shows a visible save/submit row.
- Successful submission still follows existing popup close/reload behavior.
- No duplicate submit rows are rendered.
- `poetry run pytest -q` passes.

Tests to run
- `poetry run pytest -q`
- UI test (Playwright or equivalent) covering modal form rendering and successful submission for element/handler popup flows.