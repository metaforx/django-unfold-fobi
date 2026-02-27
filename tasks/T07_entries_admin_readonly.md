# Task T07 - DB Store Entries: Admin List Routing and Readonly Detail

Goal
- Route "View entries" from form builder to Django admin `SavedFormDataEntry` changelist with form filter.
- Make submitted entry detail effectively read-only for non-superusers while keeping admin visibility/export workflows.

Suggested Skills
- Primary: `$unfold-dev-advanced` (cross-view/admin permission and action-link alignment).
- Debug fallback: `$unfold-debug-refactor` for permission and URL edge-case regressions.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires T03-T04 passing before and after changes.

Context from code back-check
- Builder action list currently appends plugin custom actions via `plugin.get_custom_actions(...)`.
- DB-store plugin "View entries" currently points to `/fobi/<form_entry_id>/` (frontend-style view), not admin changelist.
- `SavedFormDataEntryAdmin` is re-registered in `unfold_fobi`, but non-superusers can still open change form pages where editable fields are present.

Scope
- Replace/override DB-store "View entries" action URL in builder edit UI to:
  - `/admin/fobi_contrib_plugins_form_handlers_db_store/savedformdataentry/?form_entry__id__exact=<id>`
- Keep "Export entries" behavior intact.
- In `SavedFormDataEntryAdmin`:
  - allow viewing for staff with existing Django admin permissions.
  - restrict mutation for non-superusers (no change/save; optional no delete).
- Preserve superuser full access.
- Extend pytest coverage for:
  - builder action link target.
  - filtered admin changelist visibility.
  - readonly behavior on entry change page for non-superuser staff.

Non-goals
- No proxy model for saved entry rows unless strictly required by admin constraints.
- No redesign of db_store templates or data export format.
- No API contract changes for form submission.

Deliverables
- Builder "View entries" action linked to admin filtered changelist.
- Admin permission overrides for submitted entry mutability.
- Regression tests covering URL and readonly contract.

Acceptance Criteria
- Clicking "View entries" from `/admin/unfold_fobi/formentryproxy/edit/<id>/` opens admin filtered list, not `/fobi/<id>/`.
- Non-superuser staff can inspect submitted entries but cannot modify them.
- Superusers retain edit access.
- `poetry run pytest -q` passes with added checks.

Tests to run
- `poetry run pytest -q`
