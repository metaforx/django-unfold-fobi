# Task T20 - Reusable SavedFormDataEntry admin integration (readonly + pretty JSON)

Goal
- Introduce a reusable admin integration for `SavedFormDataEntryAdmin`.
- Make entries readonly by default for non-superuser staff without requiring
  explicit model permission assignment.
- Render submitted form data once, as pretty JSON, in the plain admin detail
  view to avoid redundant internal-state display.

Problem statement
- `SavedFormDataEntryAdmin` behavior is currently embedded directly in
  `fobi_admin.py`, making composition in consuming projects harder.
- Non-superuser read access currently depends on explicit permission
  assignment in tests/projects.
- The stock db_store admin surfaces multiple representations (formatted and raw)
  that can be redundant for day-to-day admin viewing.

Suggested Skills
- Primary: `$unfold-dev-advanced`.

Dependencies
- T07 (entries admin readonly contract).

Scope
- Add reusable integration mixin in `src/unfold_fobi/admin/`.
- Compose the registered `SavedFormDataEntryAdmin` with that mixin.
- Keep add disabled for everyone.
- Keep non-superusers readonly and deny change/delete mutations.
- Keep superuser change/delete permissions.
- Replace plain admin detail fields with one pretty JSON rendering of submitted
  payload.
- Extend admin tests for default readonly access and pretty rendering.

Non-goals
- No change to db_store submission persistence logic.
- No change to export actions.
- No change to internal saved-data state persistence format.

Implementation requirements
- Add a reusable mixin (e.g. `SavedFormDataEntryAdminIntegrationMixin`) that
  centralizes:
  - admin permissions (view/read-only defaults),
  - list/search config,
  - pretty JSON renderer for transmitted payload.
- Support `saved_data` as either JSON string or dict.
- If `saved_data` includes wrapper state dicts, prefer a transmitted-payload key
  when present (for plain view), otherwise render the full payload.
- Render with `<pre>` for readable pretty JSON.

Deliverables
- New reusable admin mixin module in `src/unfold_fobi/admin/`.
- `SavedFormDataEntryAdmin` wired to use the mixin.
- Admin tests validating:
  - staff readonly view works without explicit permission assignment,
  - raw redundant fields are not shown in plain view,
  - transmitted payload is rendered as pretty JSON once.

Acceptance Criteria
- Non-superuser staff can open changelist/detail in readonly mode by default.
- Non-superuser mutation attempts remain forbidden.
- Superusers still cannot add entries manually.
- Admin detail view shows one pretty-transmitted-data block, without raw-field
  duplication in the plain view.
- `poetry run pytest tests/admin/test_entries_admin.py -q` passes.

Tests to run
- `poetry run pytest tests/admin/test_entries_admin.py -q`
