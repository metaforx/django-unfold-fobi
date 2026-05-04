# Task T27 - Fix: db_store "Export entries" inline button returns empty CSV for non-owner staff

Type
- Fix (not a feature). No new product capability is added; this restores
  expected behavior of an existing button.

Goal
- Make the inline "Einträge exportieren" / "Export entries" button on the
  form-handler row produce the same CSV that the admin changelist's bulk
  "Export to CSV/XLS" action produces for the same form.

Problem statement
- On the form-entry change view, the form-handler row for the `db_store`
  plugin renders an "Export entries" action button that links to
  `/admin/fobi/db-store/export/<form_entry_id>/`.
- For staff users that are not the form's original `user`, the resulting
  CSV is empty (header row only, no data rows).
- The admin changelist filtered by the same form
  (`/admin/fobi_contrib_plugins_form_handlers_db_store/savedformdataentry/?form_entry__id__exact=<id>`)
  + bulk action "Export to CSV/XLS" returns the correct, non-empty CSV.

Root cause
- The button targets upstream Fobi's view
  `fobi.contrib.plugins.form_handlers.db_store.views.export_saved_form_data_entries`,
  which hard-filters the queryset by owner:
  ```python
  entries = SavedFormDataEntry._default_manager.select_related(
      "form_entry"
  ).filter(form_entry__user__pk=request.user.pk)
  ```
- This project has explicitly chosen "staff = unrestricted access" elsewhere
  (`patches/owner_filtering.py` for edit/delete views, `saved_data_entry.py`
  granting `has_view_permission` to any staff user, T07 "View entries"
  redirect bypassing the owner filter). The export button is the last
  remaining touchpoint that still enforces owner filtering — inconsistent
  with the rest of the surface and surprising to users.

Suggested Skills
- Primary: `$unfold-dev-structured`.
- Review: `$unfold-codex-reviewer`.

Dependencies
- None. Builds on existing patterns:
  - T07 inline action redirect (`admin/inlines.py` "View entries" branch).
  - `SavedFormDataEntryAdminIntegrationMixin` permission model
    (`admin/saved_data_entry.py`).

Scope
- `src/unfold_fobi/admin/saved_data_entry.py` — add a project-owned admin
  endpoint that runs the existing admin `export_data` bulk action against a
  queryset filtered by `form_entry_id`.
- `src/unfold_fobi/admin/inlines.py` — change the "Export entries" branch
  in `FormHandlerEntryInline.handler_actions` to `reverse()` the new admin
  endpoint instead of leaving the upstream Fobi URL unchanged.
- `tests/admin/` — add regression tests covering the fix and the existing
  permission model.

Non-goals
- No monkey-patch of the upstream Fobi export view.
- No change to the upstream URL `/admin/fobi/db-store/export/...` (it
  remains routed by Fobi; we just stop linking to it from the inline).
- No new permission model. Access is gated by the existing
  `SavedFormDataEntryAdminIntegrationMixin.has_view_permission` (any
  `is_staff` user).
- No change to the changelist bulk action UX (option 2 keeps working
  unchanged).
- No expansion of who can read entries — staff already see all entries via
  the changelist; this fix only realigns the button.

Implementation requirements

1. Admin endpoint
   - In `SavedFormDataEntryAdminIntegrationMixin`:
     - Override `get_urls` to prepend a single path
       `export/` named
       `unfold_fobi_savedformdataentry_export`, wrapped via
       `self.admin_site.admin_view(...)` so admin auth applies.
     - Implement the view as a method on the mixin (so it has access to
       `self.export_data`, `self.get_queryset`, `self.has_view_permission`).
     - Method body:
       1. Reject (HTTP 403 / `PermissionDenied`) if
          `not self.has_view_permission(request)`.
       2. Read `form_entry_id` from `request.GET` (validate as integer; on
          missing/invalid, return HTTP 400 with a user-facing message).
       3. Build queryset via `self.get_queryset(request).filter(
          form_entry_id=form_entry_id)`.
       4. Delegate to `self.export_data(request, queryset)` — the same
          method used by the changelist bulk action that already produces
          the correct CSV. Return its response.
   - Reuse the upstream admin's `export_data` action (`db_store/admin.py`).
     Do not re-implement `DataExporter` wiring. The two CSVs must be
     byte-identical when called with the same queryset.

Security boundary (must not regress)
- The endpoint **must** build its queryset from `self.get_queryset(request)`
  and only then `.filter(form_entry_id=...)`. It **must not** use
  `SavedFormDataEntry._default_manager`, `objects.all()`, or any direct
  manager access that bypasses the admin's queryset.
- Rationale: `contrib/sites/admin.py:RelationSiteScopeAdminMixin` overrides
  `get_queryset` to restrict non-superusers to forms bound to their
  allowed sites. Consuming projects compose that mixin into their
  `SavedFormDataEntryAdmin`. If the export endpoint queries the manager
  directly, it silently bypasses that scoping for any URL-poking staff
  user — a privilege escalation relative to the changelist + bulk-action
  path that this fix is meant to mirror.
- Posture target: parity with the changelist bulk-action export (working
  "option 2"). The endpoint must never widen access beyond what option 2
  permits for the same user.
- Note for base-package security: `unfold_fobi` itself does not apply site
  scoping by default; in the base package, any staff user with
  `view_savedformdataentry` can export any form via option 2 today, and
  the new endpoint inherits that. Tightening base-package access is out
  of scope for T27 — call it out as a follow-up if desired.

2. Inline button rewiring
   - In `src/unfold_fobi/admin/inlines.py`,
     `FormHandlerEntryInline.handler_actions`:
     - In the `elif str(label) == str(_("Export entries"))` branch,
       replace `action_url` via:
       ```python
       action_url = (
           reverse("admin:unfold_fobi_savedformdataentry_export")
           + f"?form_entry_id={obj.form_entry_id}"
       )
       ```
     - Keep `icon_name = "download"` unchanged.
   - Do not touch the existing "View entries" branch.

3. URL naming
   - The URL `name=` must be unique within the admin namespace. Confirm by
     `reverse()`-ing it in a test. Suggested: keep
     `unfold_fobi_savedformdataentry_export` to avoid collision with the
     upstream-registered `admin:fobi_contrib_plugins_form_handlers_db_store_savedformdataentry_*`
     names.

Regression prevention

Tests must lock in:
- Inline-button URL contract:
  - Asserting the rendered href on the change view points to the new admin
    endpoint with the correct `form_entry_id` query string, not to
    `/admin/fobi/db-store/export/...`.
- Endpoint behavior (happy path):
  - Staff user that is *not* the form's `user` requests the endpoint with
    `?form_entry_id=<id>`. Response status 200, `Content-Type` text/csv (or
    application/csv as upstream emits), `Content-Disposition` is an
    attachment.
  - Response body contains the saved entry's data row(s), not just the
    header — i.e. parse CSV, assert at least one non-header row exists for
    a form that has saved entries.
- Endpoint behavior (parity with changelist export):
  - For a given form_entry with N saved entries, the CSV from the new
    endpoint must contain the same number of data rows and the same header
    as the changelist's bulk-action export (the working "option 2"). One
    test asserts row-count parity; do not over-fit on byte equality if
    timestamps or ordering could differ.
- Permission gating:
  - Anonymous user → redirected to admin login (302) by
    `admin_site.admin_view`.
  - Authenticated non-staff user → 302 to login or 403 (whichever
    `admin_view` produces in this project's setup; assert it is *not* 200).
  - Staff user with `has_view_permission` → 200.
- Site-scope inheritance (regression test for the security boundary):
  - With `RelationSiteScopeAdminMixin` composed into a test
    `SavedFormDataEntryAdmin`, a non-superuser whose
    `get_sites_for_user(...)` returns no sites containing the target form
    must receive an **empty data-rows CSV** (header only) — i.e. the
    queryset filter applied. This proves the endpoint honors
    `get_queryset(request)` rather than the default manager.
  - The same user, granted access to the form's site, receives a non-empty
    CSV with the expected rows. Confirms the filter is *only* tightening,
    not blocking legitimate access.
  - Test fixture must NOT touch the base-package admin registration; use a
    parametrized admin or a context-managed `unregister`/`register` swap so
    the rest of the suite is unaffected.
- Input validation:
  - Missing `form_entry_id` → 400.
  - Non-integer `form_entry_id` → 400.
  - `form_entry_id` referencing a form with no saved entries → 200 with a
    header-only CSV (still a valid response, just empty data rows).
- Existing behavior preserved:
  - The changelist bulk "Export to CSV/XLS" action still works (covered by
    the existing test suite if present; otherwise add a smoke assertion
    that the action stays registered).
  - The "View entries" inline-button URL is unchanged (regression
    assertion against `inlines.py` redirect target).
  - `has_change_permission` / `has_delete_permission` still
    superuser-only, unaffected by this change.

Deliverables
- Admin endpoint and `get_urls` override on
  `SavedFormDataEntryAdminIntegrationMixin`.
- Updated "Export entries" branch in `FormHandlerEntryInline.handler_actions`.
- Test module (e.g. `tests/admin/test_db_store_export_action.py`) covering
  the regression-prevention list above.
- `poetry run pytest -q` passes.

Acceptance Criteria
- The "Einträge exportieren" / "Export entries" inline button on the form
  change view returns a non-empty CSV for any staff user with view
  permission, regardless of who originally created the form.
- The CSV row count and header match what the changelist's bulk-action
  export returns for the same form.
- Anonymous and non-staff users cannot reach the endpoint.
- No upstream Fobi files are patched at runtime; no upstream URL is
  rewritten.
- Existing tests continue to pass; the new tests pass.

Tests to run
- `poetry run pytest -q tests/admin/`
- `poetry run pytest -q` (full suite, regression gate)

Branch
- `fix/t27-db-store-export-inline-button` (already created).
- Do not push or merge until reviewer approval.
