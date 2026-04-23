# Task T26 - Add-view notice for Form elements and Form actions tabs

Goal
- Show clear instructions on the FormEntryProxy add view that form elements and form actions can only be added after the form is saved.
- Keep the message aligned with Unfold UI patterns/components.

Problem statement
- On:
  - `http://localhost:8080/admin/unfold_fobi/formentryproxy/add/#formelemententry_set`
  - `http://localhost:8080/admin/unfold_fobi/formentryproxy/add/#formhandlerentry_set`
- Users can open the `Form elements` tab before the form exists in the database.
- Users can also open the `Form handlers` tab (form actions) before the form exists in the database.
- At this stage, adding elements/actions is not possible because there is no saved form entry yet.
- The UI should explain the required workflow to reduce confusion.

Reference
- Unfold components introduction:
  - `https://unfoldadmin.com/docs/components/introduction/`

Suggested Skills
- Primary: `$unfold-dev-structured`.
- Review: `$unfold-codex-reviewer`.

Scope
- Add informational components for add view only.
- Show one in the `Form elements` tab state.
- Show one in the `Form handlers` tab state.
- Use Unfold `card` component.
- Use full available width and centered informational content.

Implementation requirements
- Implement through native Unfold/Django admin templates (no custom JS flow required).
- Messages must explicitly instruct:
  - first save the form,
  - use `Save and continue editing`,
  - then open the corresponding tab (`Form elements` / `Form handlers`) to add entries.
- Use Fobi terminology in English: `form elements` (not `form fields`).
- Keep change view behavior unchanged for existing forms.

Non-goals
- No redesign of inline tabs.
- No changes to form element/form action add popup flow.
- No API/model changes.

Deliverables
- Admin template changes for add-view tab messages:
  - `Form elements` tab notice.
  - `Form handlers` tab notice.
- ModelAdmin inline wiring to include both templates.
- Regression tests asserting add-view message presence and change-view absence.

Acceptance Criteria
- On add view, opening `#formelemententry_set` shows a full-width centered info card.
- On add view, opening `#formhandlerentry_set` shows a full-width centered info card in the same style.
- Card messages clearly state the save-first workflow and direct users to the appropriate tab after save.
- English wording uses `form elements` terminology.
- Existing change view behavior remains intact.
- Updated tests pass.

Tests to run
- `poetry run pytest -q tests/admin/test_add_view.py`
