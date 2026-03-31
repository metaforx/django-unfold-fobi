# Task T21 - Safe FormEntryProxy delete without removing submitted data

Goal
- Allow deleting forms from `FormEntryProxy` changelist actions without deleting
  any existing submitted form data.
- Preserve historical `SavedFormDataEntry` rows at all costs.
- Restrict deletion so non-superusers can only delete their own forms; superusers
  can delete any form.

Problem statement
- Repro:
  1. Open `/admin/unfold_fobi/formentryproxy/`.
  2. Select one or more forms.
  3. Run changelist action "Delete selected forms".
- Current result: deletion is blocked by protected related objects and Django admin
  shows (German locale):
  - `Das Loeschen der ausgewaehlten Formulare (Baukasten) wuerde im Loeschen`
    `geschuetzter verwandter Objekte resultieren ...`
  - related object: `Formularuebergabe Eintraege`.
- This prevents form cleanup and mixes two concerns:
  - deleting form definitions,
  - retaining submitted data for audit/history.

Suggested Skills
- Primary: `$unfold-dev-advanced`.

Dependencies
- T09 (permission alignment semantics for form ownership/admin access).
- T20 (saved-entry admin behavior and preserved historical data expectations).

Scope
- `src/unfold_fobi/admin/form_entry_proxy.py`
  - implement safe delete flow for single and bulk delete paths.
  - enforce ownership-aware delete permissions for non-superusers.
- Any required glue in `src/unfold_fobi/services.py` (or adjacent admin helpers)
  to keep unlink logic reusable and testable.
- `tests/admin/`
  - add regression tests for changelist bulk delete and object delete behavior.
  - add permission tests for owner vs non-owner vs superuser deletion.
  - add data-retention tests proving submitted entries are not deleted.

Non-goals
- No new ownership fields on models.
- No deletion of `SavedFormDataEntry` records.
- No redesign of saved-entry admin UI.

Implementation requirements
- Deleting a `FormEntryProxy` must not cascade-delete submitted data rows.
- Implement a deterministic unlink strategy before deleting forms:
  - remove or neutralize the relation from saved submissions to the deleted form,
    while preserving submission payload and metadata.
  - if FK constraints do not allow nulling directly, provide a compatibility-safe
    fallback that still guarantees data retention (no data loss).
- Support both Django admin delete paths:
  - object delete view,
  - changelist bulk delete (`delete_selected`).
- Permission semantics:
  - superuser: may delete any form.
  - non-superuser staff: may delete only forms they own (using existing owner/user
    semantics already present in fobi model data; do not add model fields).
  - unauthorized delete attempts must be denied cleanly (403 or filtered queryset,
    but never partial silent data loss).
- Keep user-facing messaging explicit when deletion is skipped/denied for
  ownership reasons.

Deliverables
- Safe-delete implementation in admin/service layer.
- Tests covering:
  - bulk delete succeeds for eligible forms,
  - submitted data survives form deletion,
  - non-owner staff cannot delete foreign forms,
  - superuser can delete any form,
  - no protected-object blocker appears for normal safe-delete path.
- Task notes documenting final unlink behavior and ownership rule used.

Acceptance Criteria
- Selecting forms in `/admin/unfold_fobi/formentryproxy/` and running delete no
  longer fails with protected-related-object error for eligible forms.
- Deleted forms are removed from `FormEntryProxy`/`FormEntry` as expected.
- Existing submitted data rows remain intact and queryable after form deletion.
- Non-superuser staff can delete only own forms; superuser can delete all.
- `poetry run pytest tests/admin -q` passes.

Tests to run
- `poetry run pytest tests/admin -q`

