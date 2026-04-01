# Task T23 - Preview access for non-public forms in form-fields API

Goal
- Allow authenticated staff with `unfold_fobi.view_formentryproxy` permission
  to preview non-public forms via `GET /api/fobi-form-fields/{slug}/`.
- No new settings or configuration — use Django's built-in permission system.

Problem statement
- The endpoint filters `FormEntry.objects.get(slug=slug, is_public=True)`,
  so non-public forms always return 404.
- Admin users building forms need to preview them before publishing.

Suggested Skills
- Primary: `$unfold-dev-advanced`.

Dependencies
- T17/T17a, T18, T19 (current form-fields endpoint features).

Scope
- `src/unfold_fobi/api/views.py` — modify `get_form_fields` access logic.
- `tests/api/` — tests for preview access.

Non-goals
- No configurable hook or setting.
- No site-scope logic in the package.
- No changes to the PUT submission endpoint.

Implementation requirements
- Change the lookup from `get(slug=slug, is_public=True)` to `get(slug=slug)`.
- After lookup, apply access control:
  - Public form: serve to anyone (unchanged).
  - Non-public form: serve only if `request.user.has_perm("unfold_fobi.view_formentryproxy")`.
  - Otherwise: return 404 (not 403, to prevent information leakage).
- Add `"is_preview": true/false` to the response envelope so the frontend can
  show a preview indicator or disable submission.
- Keep `@never_cache`.

Deliverables
- Updated `get_form_fields` view.
- `is_preview` flag in response.
- Tests:
  - Public form: anonymous gets 200, `is_preview` is false.
  - Non-public form: anonymous gets 404.
  - Non-public form: staff with permission gets 200, `is_preview` is true.
  - Non-public form: staff without permission gets 404.
- `poetry run pytest -q` passes.

Acceptance Criteria
- Public forms behave exactly as before.
- Non-public forms are accessible to users with `view_formentryproxy` permission.
- `is_preview` flag distinguishes preview from public access.
- `poetry run pytest -q` passes.

Tests to run
- `poetry run pytest -q`
