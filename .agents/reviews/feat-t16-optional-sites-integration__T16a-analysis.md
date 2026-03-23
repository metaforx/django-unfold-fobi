# T16a Analysis — Sites Integration Wiring and Validation

## Outcome 1: Clone/import wired to site-binding hooks

**Approach:** Extracted `_do_clone(request, form_entry)` and `_do_import(request, entry_data)`
hook methods from `FormEntryProxyAdmin`. The actual admin actions (`clone_selected_forms`,
`import_form_entry_action`) now delegate to these hooks instead of calling
`clone_form_entry()` / `perform_form_entry_import()` directly.

`SiteAwareFormEntryMixin` overrides both hooks:
- `_do_clone`: calls `super()._do_clone()`, then `copy_site_bindings()`, then
  `assign_default_sites()` if the clone has no sites.
- `_do_import`: calls `super()._do_import()`, then `ensure_binding()`, then
  `assign_default_sites()`.

No action decorators need to be duplicated in the mixin.

## Outcome 2: Backfill migration

`0002_seed_form_bindings.py` iterates all `FormEntry` rows and creates a
`FobiFormSiteBinding` for each one that doesn't have one. If a default site
(id=1) exists, it is assigned to each new binding.

Tests verify: idempotency, missing default site graceful behavior.

## Outcome 3: Disabled-mode verification

Verified by:
- File scan: no `from django.contrib.sites` in base `unfold_fobi` (excluding `contrib/`)
- Admin changelist, add, and change views all work without the site mixin composed
- Form entries have no binding by default

## Outcome 4: Real admin surface tests

- Clone action via POST to changelist (base admin, no mixin) — works, creates clone
- `_do_clone` hook test — copies bindings from source to clone
- `_do_clone` hook test — calls `assign_default_sites` when source has no sites
- Import action via POST with file upload — creates form entry
- `_do_import` hook test — creates binding and calls `assign_default_sites`
- SavedFormDataEntry queryset filterable via `form_entry__site_binding__sites`