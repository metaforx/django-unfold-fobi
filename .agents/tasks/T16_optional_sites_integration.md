# Task T16 - Optional Sites Integration Extraction

Goal
- Extract the reusable parts of the current GovOS multi-site Fobi integration into `unfold_fobi`.
- Keep the feature optional and drop-in:
  - projects with `django.contrib.sites` enabled can use it,
  - projects without Sites enabled continue to use `unfold_fobi` unchanged.
- Preserve the current `FormEntryProxy` proxy-model approach.

Suggested Skills
- Primary: `$unfold-dev-advanced`.
- Debug fallback: `$unfold-debug-refactor`.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Reuse the current `unfold_fobi` admin structure after T14/T15.
- Treat the GovOS implementation as the behavior reference, not as a runtime dependency.

Context from current GovOS implementation
- Use these files in `../govos-bubikon-backend` as the extraction baseline:
  - `fobi_site_forms/admin.py`
  - `fobi_site_forms/models.py`
  - `fobi_site_forms/migrations/0001_initial.py`
  - `fobi_site_forms/migrations/0002_seed_form_bindings.py`
  - `site_permissions/admin.py`
  - `site_permissions/utils.py`
  - `unfold_fobi/admin/form_entry_proxy.py`
  - `unfold_fobi/fobi_admin.py`
  - `govos/settings.py`
- Important boundary:
  - `fobi_site_forms/admin.py` currently mixes reusable site-aware Fobi behavior with GovOS-specific permission policy.
  - `site_permissions/*` is the project integration target to compose with, not code to copy into `unfold_fobi`.

Scope
- Add an optional Sites integration surface inside `unfold_fobi`.
- Keep proxy handling unchanged.
- Provide reusable package-owned support for:
  - form-entry site binding persistence,
  - synthetic `sites` field support in form admin,
  - import/clone propagation of site bindings,
  - relation-based site scoping helpers for `SavedFormDataEntry`,
  - opt-in configuration so projects can enable or ignore the feature cleanly.
- Add tests for both modes:
  - Sites disabled,
  - Sites enabled.

Package boundary
- The following must become part of `unfold_fobi`:
  - optional app/module structure for Sites integration,
  - site-binding model and migrations,
  - admin mixins/helpers for site-aware `FormEntryProxy` admin forms,
  - reusable services/helpers for reading, writing, and copying form site bindings,
  - relation-based queryset/permission helper mixins for models that do not own a direct `sites` field,
  - package docs for enabling the feature.

Project boundary
- The following must stay in the consuming project:
  - user-to-site permission resolution,
  - project-specific admin permission policy,
  - project-specific fallback assignment rules and messages,
  - project `Admin` subclasses that combine package mixins with local permission behavior,
  - any `SiteRestrictedAdmin` composition details.

Implementation constraints
- Do not change proxy model handling.
- Do not redesign `FormEntryProxy` into a concrete model.
- Do not add a real database `sites` field directly to `FormEntryProxy`.
- Do not force `django.contrib.sites` for all `unfold_fobi` consumers.
- Do not couple `unfold_fobi` directly to GovOS `site_permissions`.
- No commits.
- No push.

Required design checks
- Create analysis note: `.agents/reviews/<branch>__T16-analysis.md`.
- Confirm which GovOS behavior is:
  - package-generic,
  - project-specific,
  - intentionally left outside the package.
- Document how the optional Sites mode is activated.
- Document how disabled mode avoids import, app-loading, and settings breakage.
- Document why proxy-model handling remains unchanged.
- Add a short GovOS adoption note showing:
  - what current GovOS code is replaced by package functionality,
  - what thin adapter code remains in GovOS after extraction.

Non-goals
- No direct dependency on GovOS project code.
- No redesign of Fobi core models.
- No forced Sites dependency for package consumers that do not need it.
- No attempt to make `FormEntryProxy.sites` a real ORM field.
- No unrelated admin UI redesign.

Deliverables
- Optional Sites integration in `unfold_fobi` with clear extension points.
- Tests covering enabled and disabled modes.
- Analysis note documenting extraction boundaries and GovOS mapping.
- Short package usage documentation for enabling the feature and composing it with project-specific admin/permission logic.

Acceptance Criteria
- `unfold_fobi` works without `django.contrib.sites`.
- Optional Sites integration can be enabled without changing proxy-model semantics.
- Package-owned site-binding behavior is reusable and no longer requires GovOS-specific code copies.
- `SavedFormDataEntry` relation-based site scoping is supported through package helpers or mixins.
- GovOS-specific permission logic remains outside the package.
- Tests exist for:
  - package behavior with Sites disabled,
  - package behavior with Sites enabled,
  - clone/import retaining site bindings in enabled mode,
  - relation-scoped saved-entry queryset behavior in enabled mode.
- `poetry run pytest -q` passes.

Tests to run
- `poetry run pytest -q`
- Add targeted tests for:
  - disabled-mode app loading/import behavior,
  - enabled-mode model/admin wiring,
  - clone/import site-binding propagation,
  - relation-scoped saved-entry queryset behavior.