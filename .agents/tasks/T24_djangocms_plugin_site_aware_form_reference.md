# Task T24 - django CMS plugin for reusable site-aware Fobi form reference

Goal
- Add a reusable django CMS plugin in this package that references a Fobi form.
- Make plugin behavior site-aware when `unfold_fobi.contrib.sites` is enabled.
- Keep base behavior fully functional when optional integrations are not enabled.
- Use `django-unfold-extra` plugin base support (version `0.2.1`).

Decision (FormEntry vs FormEntryProxy)
- The plugin model FK must target `fobi.FormEntry` (concrete model), not
  `unfold_fobi.FormEntryProxy`.
- Reasoning:
  - `FormEntryProxy` is an admin-facing proxy concern.
  - Runtime/plugin data should depend on the stable concrete model.
  - Site filtering still works through `site_binding` relation because
    `FobiFormSiteBinding` already links to the same underlying form row.
- Required query path for site filtering remains:
  - `form_entry__site_binding__sites`

Problem statement
- We need a package-owned django CMS plugin so projects can reuse one
  implementation instead of building project-local plugins.
- In multi-site setups, editors must only pick forms allowed for the current
  site context (and, optionally, for their allowed user sites).

Suggested Skills
- Primary: `$unfold-dev-advanced`.
- Review: `$unfold-codex-reviewer`.

Scope
- Add optional django CMS integration under a new package contrib module, for
  example `src/unfold_fobi/contrib/djangocms/`.
- Add plugin model + plugin registration + render logic.
- Add admin/form queryset filtering for site-aware form selection.
- Build plugin class on top of `UnfoldCMSPluginBase` and keep widget override
  support explicit.
- Add docs for installation and behavior in both modes:
  - base mode (no sites contrib),
  - sites-enabled mode (`unfold_fobi.contrib.sites`).
- Add tests that validate filtering behavior and safe fallback behavior.

Non-goals
- No FK to `FormEntryProxy`.
- No mandatory dependency on django CMS for base `unfold_fobi` users.
- No mandatory dependency on `django.contrib.sites` for users who do not enable
  sites integration.
- No project-specific permission policy in package code.

Implementation requirements
1. Optional integration boundary
- Keep django CMS support optional and isolated in contrib app/module so projects
  without django CMS are unaffected.
- Avoid top-level imports that break startup when django CMS is not installed.
- Document required `INSTALLED_APPS` entries for enabling the plugin.

2. Plugin model and FK
- Create a CMS plugin model (still based on `CMSPlugin`) with:
  - `form_entry = ForeignKey("fobi.FormEntry", ...)`
- Use `on_delete=models.PROTECT` unless there is an explicit package standard
  requiring a different delete behavior.

3. Plugin class base and widgets (`django-unfold-extra==0.2.1`)
- Register the plugin class using `UnfoldCMSPluginBase` from
  `django-unfold-extra` (v`0.2.1` minimum).
- Follow this contract:

```python
class MyPlugin(UnfoldCMSPluginBase):
    cms_widget_overrides = {
        **UnfoldCMSPluginBase.cms_widget_overrides,
        SomeField: MyCustomWidget,
    }
```

- Keep the override map additive (`**UnfoldCMSPluginBase.cms_widget_overrides`)
  so package defaults from unfold-extra are preserved.

4. Site-aware queryset filtering
- In plugin admin/form selection:
  - If `unfold_fobi.contrib.sites` is not installed:
    - show standard form queryset (existing/base behavior).
  - If `unfold_fobi.contrib.sites` is installed:
    - restrict by current site context (`site_binding__sites` contains current
      site),
    - restrict non-superusers further by
      `get_sites_for_user_func()(request.user)`,
    - return `distinct()` queryset.
- If a form has no site binding, treat it as not selectable in sites-enabled
  mode (consistent with strict site assignment behavior).

5. Validation and rendering contract
- Validate on save that selected form is allowed for the request/site context in
  sites-enabled mode.
- Plugin render must fail safely if form is missing/inaccessible (no hard 500).
- Keep rendering hook points explicit so projects can customize template/output.

6. Documentation
- Update README with:
  - enabling django CMS contrib module,
  - requirement: `django-unfold-extra>=0.2.1`,
  - plugin usage example in placeholders,
  - behavior matrix for:
    - no sites contrib,
    - sites contrib enabled.

Deliverables
- New django CMS contrib integration module.
- CMS plugin model registered and usable in django CMS.
- Site-aware form FK queryset filtering tied to existing
  `unfold_fobi.contrib.sites` behavior.
- Tests for both modes and permission-aware site filtering.
- README update with setup and behavior notes.

Acceptance Criteria
- Plugin stores FK to `fobi.FormEntry` and works end-to-end.
- Plugin class extends `UnfoldCMSPluginBase` and preserves base
  `cms_widget_overrides` via additive merge.
- In sites-enabled mode, plugin form selection is filtered by current site and
  user-allowed sites (non-superuser).
- In sites-disabled mode, plugin remains usable without importing sites modules.
- Base package still imports/starts when django CMS contrib module is not
  enabled.
- `poetry run pytest -q` passes.

Tests to run
- `poetry run pytest -q`
- Add targeted tests for:
  - plugin model FK target correctness (`FormEntry` concrete model),
  - sites-disabled plugin selection behavior,
  - sites-enabled queryset filtering by current site,
  - non-superuser filtering via `UNFOLD_FOBI_SITES_FOR_USER`,
  - safe rendering behavior when referenced form is unavailable.
