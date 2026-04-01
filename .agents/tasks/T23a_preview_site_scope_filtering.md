# Task T23a - Site-scoped preview filtering for form-fields API

Goal
- When `unfold_fobi.contrib.sites` is installed, restrict preview access to
  forms that are assigned to one of the requesting user's sites.
- When the contrib app is not installed, preview behavior from T23 is unchanged.

Problem statement
- T23 grants preview access to any authenticated user with
  `fobi.view_formentry`. In multi-site deployments, a user with that permission
  can preview forms belonging to sites they have no access to.
- A POC solved this with a project-local view override. The site-scope check
  should live in `unfold_fobi.contrib.sites` so projects don't need to override
  the endpoint.

Suggested Skills
- Primary: `$unfold-dev-advanced`.

Dependencies
- T23 (preview access via `fobi.view_formentry`).
- T16/T16a (optional Sites integration with `contrib.sites`).

Scope
- `src/unfold_fobi/api/views.py` — add a hook point for preview access check.
- `src/unfold_fobi/contrib/sites/` — provide the site-scoped check.
- `tests/api/` — test both with and without sites app.

Non-goals
- No configurable setting or callable.
- No changes to the PUT submission endpoint.

Design
- In `get_form_fields`, after the base `fobi.view_formentry` permission check
  passes, call a `_check_preview_site_scope(user, form_entry)` function.
- This function checks if `unfold_fobi.contrib.sites` is installed
  (`django.apps.apps.is_installed`). If not, returns `True` (no filtering).
- If installed, imports `get_sites_for_user_func` from `contrib.sites.conf` and
  checks that the form's `site_binding.sites` intersects the user's sites.
- Superusers bypass the site check (already handled by the permission check).
- Keep it as a single function in `views.py` — no new modules.

Implementation requirements
- Use `django.apps.apps.is_installed("unfold_fobi.contrib.sites")` for the
  conditional check.
- Use lazy import of `contrib.sites` to avoid import errors when the app is
  not installed.
- If the form has no `site_binding` (no binding row created yet), deny preview
  access for non-superusers — a form without site assignment is not ready for
  preview.

Deliverables
- Updated preview access logic in `get_form_fields`.
- Tests:
  - Without sites app: staff with permission can preview any non-public form.
  - With sites app: staff can preview form on their site.
  - With sites app: staff cannot preview form on a different site.
  - Superuser bypasses site check.
- `poetry run pytest -q` passes.

Acceptance Criteria
- Multi-site users can only preview forms assigned to their sites.
- Single-site deployments (no contrib.sites) behave exactly as T23.
- Superusers can preview any form regardless of site assignment.
- `poetry run pytest -q` passes.

Tests to run
- `poetry run pytest -q`
