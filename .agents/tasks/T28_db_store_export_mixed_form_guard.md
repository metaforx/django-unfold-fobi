# Task T28 - db_store export: mixed-form guard on changelist bulk action

Type
- Fix. The changelist bulk "Export to CSV/XLS" action currently accepts
  any selected queryset and silently flattens rows from different forms
  into one sheet. This task makes that case fail loudly instead of
  producing a misleading file.

Goal
- On the `SavedFormDataEntry` changelist, prevent the bulk
  "Export to CSV/XLS" action from running across rows that belong to
  **different** `form_entry` parents. Show a user-facing error message
  that explicitly tells the user to filter the changelist by a single
  form before retrying.

Problem statement
- The changelist's bulk `export_data` action accepts any selected
  queryset. If the user selects rows from two or more different forms
  (or runs without filtering), `DataExporter` flattens all submissions
  into one sheet keyed by the union of headers — silently mixing data
  sets. The result is technically a CSV but semantically misleading.
- The inline-button path (T27, `unfold_fobi_savedformdataentry_export`)
  is unaffected because it filters by a single `form_entry_id` server-side.

Suggested Skills
- Primary: `$unfold-dev-structured`.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Builds on T27 (`SavedFormDataEntryAdminIntegrationMixin` already
  exists; T27 added `export_for_form_entry` and the project export URL).
- Reuses the project's pattern of overriding upstream Fobi admin
  behavior via `SavedFormDataEntryAdminIntegrationMixin` rather than
  patching `fobi.contrib.plugins.form_handlers.db_store`.

Scope
- `src/unfold_fobi/admin/saved_data_entry.py` — override the inherited
  `export_data` admin action to reject mixed-form querysets with a
  user-facing error; in all other cases, delegate to `super()` unchanged.
- `tests/admin/test_db_store_export_action.py` — add regression tests
  for the guard.

Non-goals
- No monkey-patching or forking of `fobi/contrib/plugins/form_handlers/db_store/`.
- No reimplementation of `DataExporter`.
- No change to the inline-button URL contract from T27.
- No change to permission gating.
- No new bulk action; the existing `export_data` action keeps the same
  short description and registration so user-visible labels do not move.
- `SavedFormWizardDataEntry` is out of scope. The wizard admin is a
  separate `ModelAdmin` subclass; this task only touches the integration
  mixin used for `SavedFormDataEntry`.

Implementation requirements

Where the guard sits
- The only user-visible behavior change is on the changelist bulk
  "Export to CSV/XLS" action. The inline "Einträge exportieren" button
  (T27) already produces the correct CSV — it filters by a single
  `form_entry_id` before calling `export_data` and is not the bug we're
  fixing.
- The override is nevertheless placed on the shared `export_data`
  method, because both paths funnel through it
  (`export_for_form_entry` → `self.export_data` → also the bulk-action
  target). The inline path always passes a single-form queryset, so the
  guard is a no-op there in practice; in the bulk-action path it fires
  when the user manually multi-selects rows from different forms.
- This expresses the rule "`export_data` requires a single-form
  queryset" once, at the boundary, instead of duplicating the check at
  each caller.

1. Override `export_data` on `SavedFormDataEntryAdminIntegrationMixin`
   - Signature must match the upstream admin action:
     `def export_data(self, request, queryset): ...`
   - Behavior:
     1. Compute distinct form_entry ids:
        `form_entry_ids = list(queryset.values_list("form_entry_id", flat=True).distinct())`.
     2. **Mixed-form case** (`len(form_entry_ids) > 1`): do **not** call
        `super()`. Emit `messages.error(request, ...)` (see message
        below) and return
        `HttpResponseRedirect(request.get_full_path())` so any active
        `?form_entry__id__exact=...` filter is preserved.
     3. **All other cases** (0 or 1 distinct form): delegate to
        `super().export_data(request, queryset)` and return its
        response unchanged. This preserves the T27 contract that an
        empty queryset still returns a header-only CSV with status 200.
   - Keep `short_description` aligned with upstream so the action label
     in the dropdown is unchanged:
     `export_data.short_description = _("Export data to CSV/XLS")`.

2. User-facing error message
   - Wording (English source; translators handle other locales):
     "Export across multiple forms is not supported. Filter the list by
     a single form (use the form filter in the sidebar) and try again."
   - Wrap in `gettext_lazy` (`_(...)`) so locale extraction picks it up.
   - Use `messages.error`, not `messages.warning` — the export did not run.
   - Do not include form names or ids in the message.

3. Imports / wiring
   - Add to `saved_data_entry.py`:
     `from django.contrib import messages`
     `from django.http import HttpResponseRedirect`
   - Place the override colocated with the existing
     `export_for_form_entry` method.

Regression prevention

Add to `tests/admin/test_db_store_export_action.py` (reuses the existing
`saved_entries` fixture and admin-registration plumbing).

- **Mixed-form guard rejects the export**
  - Create saved entries on two different forms; build a queryset
    spanning both; call the registered admin's `export_data(request, qs)`
    directly via a `RequestFactory.post(...)` request.
  - Assert: response is an `HttpResponseRedirect` (status 302); exactly
    one `messages.error` was emitted; `super().export_data` was **not**
    called (patch the upstream method to count calls / raise).

- **Mixed-form guard preserves changelist filter**
  - Build the request with
    `RequestFactory.post("/admin/.../?form_entry__id__exact=42&q=foo", ...)`.
  - Assert the redirect's `Location` (or `.url`) equals the same path
    including all query parameters.

- **Single-form happy path is unchanged**
  - With one form's worth of rows, `super().export_data` IS called once
    and the response is returned unmodified (assert via call counter
    and identity / status code).

- **Empty queryset still delegates**
  - With an empty queryset, `super().export_data` is called and its
    response returned. No mixed-form error. Protects the T27 invariant.

- **T27 regressions**
  - All existing tests in `tests/admin/test_db_store_export_action.py`
    continue to pass without modification (the inline-endpoint path
    only sees single-form querysets, so the guard never fires there).

Deliverables
- `export_data` override on `SavedFormDataEntryAdminIntegrationMixin`.
- New tests in `tests/admin/test_db_store_export_action.py` covering
  the guard.
- `poetry run pytest -q tests/admin/` passes.
- `poetry run pytest -q` (full suite) passes.

Acceptance Criteria
- Triggering the changelist bulk action across rows from two or more
  different forms does **not** download any file. The user is
  redirected back to the changelist with an error message telling them
  to filter by a single form.
- The redirect preserves the user's existing changelist URL (filters,
  search, page).
- Bulk export from a single-form-filtered changelist still works
  byte-identically to today (same upstream response).
- T27 acceptance criteria continue to hold.
- No upstream Fobi files are patched at runtime.

Tests to run
- `poetry run pytest -q tests/admin/test_db_store_export_action.py`
- `poetry run pytest -q tests/admin/`
- `poetry run pytest -q`

Branch
- `feat/t28-db-store-export-mixed-form-guard`.
- Do not push or merge until reviewer approval.
