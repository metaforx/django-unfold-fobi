# Task T16a - Sites Integration Wiring and Validation Follow-up

Goal
- Close the gaps left by T16 so the optional Sites integration is production-ready.
- Turn the current mixins/helpers into a fully wired and verified integration path.
- Keep the feature optional and package-local.

Why this follow-up exists
- T16 introduced the optional `unfold_fobi.contrib.sites` module, but the live
  admin flows are not fully wired to it yet.
- The current test coverage proves the helpers in isolation, not the real clone
  and import actions exposed by `FormEntryProxyAdmin`.
- The current suite also does not validate the true "Sites disabled" mode,
  because the test settings always install both `django.contrib.sites` and
  `unfold_fobi.contrib.sites`.

Requested outcomes
1. Wire clone/import flows to site-binding hooks
- When a project composes `SiteAwareFormEntryMixin` into its admin, site
  bindings must propagate through the actual admin flows, not only through
  helper calls in tests.
- `clone_selected_forms` should copy bindings automatically when the mixin is
  present.
- JSON import should create or assign bindings through the mixin hook, so
  imported forms do not require a separate post-processing step.

2. Add an adoption/backfill path for existing forms
- Enabling the optional Sites app on a project with existing forms should not
  make those forms disappear for non-superusers just because no binding rows
  exist yet.
- Provide either:
  - a data migration that creates missing bindings for existing forms, or
  - a documented management command / upgrade step with tests.
- Define the intended behavior for empty bindings after backfill.

3. Add real disabled-mode verification
- Add tests that run without `django.contrib.sites` and without
  `unfold_fobi.contrib.sites` in `INSTALLED_APPS`.
- Verify that base `unfold_fobi` imports, app loading, migrations, and core
  admin URLs still work in that mode.
- Avoid top-level imports in the disabled-mode tests that accidentally pull in
  the optional Sites app.

4. Tighten integration tests around the real admin surface
- Test the actual admin clone action with bindings present on the source form.
- Test the actual admin JSON import action and verify binding/default-assignment
  behavior on the imported form.
- Cover the project-composition contract for saved-entry scoping using
  `form_entry__site_binding__sites`.

Scope
- `src/unfold_fobi/admin/form_entry_proxy.py`
- `src/unfold_fobi/contrib/sites/*`
- tests for enabled/disabled modes and real admin flows
- README/task/review notes needed to reflect the final contract

Non-goals
- No redesign of `FormEntryProxy`.
- No forced dependency on `django.contrib.sites` for base package users.
- No GovOS-specific permission or group-site policy inside the package.

Deliverables
- Actual clone/import integration for site bindings.
- Verified disabled-mode coverage.
- Backfill/adoption support for existing forms.
- Updated docs that match the final behavior.

Acceptance Criteria
- Composed site-aware admin clone flow copies bindings without manual helper
  calls in tests.
- Composed site-aware admin import flow creates/applies bindings without manual
  post-processing.
- Existing forms have a supported upgrade path when the optional Sites app is
  enabled in an already-populated project.
- Base `unfold_fobi` remains usable when `django.contrib.sites` is absent.
- Tests prove both enabled and disabled modes through actual runtime
  configuration, not just isolated helper imports.
- `poetry run pytest -q` passes.

Tests to run
- `poetry run pytest -q`
- Targeted tests for:
  - disabled-mode settings/app loading,
  - clone action binding propagation,
  - import action binding propagation,
  - backfill/adoption behavior for existing forms.