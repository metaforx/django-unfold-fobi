# Task T18 - Enforce active dates on REST API and expose form metadata

Goal
- Block form submissions via REST API when the form is outside its active date
  window (`active_date_from` / `active_date_to`).
- Expose `success_page_title`, `success_page_message`, and active-date metadata
  in the GET form-fields endpoint so frontends can render success pages and
  "form not yet open" / "form closed" states.

Problem statement
- Fobi's `FormEntry` model has an `is_active` property that checks
  `active_date_from` and `active_date_to`. Neither the GET form-fields endpoint
  nor the upstream PUT submission endpoint (`FobiFormEntryViewSet.update`)
  checks this property.
- A form with `active_date_to = 2026-03-31 06:00` currently accepts REST
  submissions indefinitely — any `curl` request bypasses the frontend.
- `success_page_title` and `success_page_message` are `FormEntry` model fields
  but are not returned by the GET endpoint, so frontends cannot render a
  proper post-submission success page.

Root cause
- Fobi's DRF integration (`fobi.contrib.apps.drf_integration.views`) has no
  `is_active` check. Its queryset filters only `is_public`.
- The `get_form_fields` view in `unfold_fobi` returns form element fields but
  omits model-level metadata (`success_page_*`, `active_date_*`).

Suggested Skills
- Primary: `$unfold-dev-structured`.

Dependencies
- T17/T17a (form-fields endpoint with widget support).

Scope
- `src/unfold_fobi/api/views.py` — enhance GET response envelope.
- `src/unfold_fobi/patches/` or `src/unfold_fobi/api/` — enforce active-date
  check on PUT submission.
- `tests/api/` — tests for both endpoints.

Non-goals
- No redesign of fobi's DRF integration.
- No changes to the admin builder or HTML form submission flow (fobi's template
  views already check `is_active` in their own rendering).

Requested outcomes

1. GET `/api/fobi-form-fields/{slug}/` response envelope gains:
   ```json
   {
     "id": 3,
     "slug": "test-form",
     "title": "Test Form",
     "is_active": true,
     "active_date_from": "2026-01-01T00:00:00Z",
     "active_date_to": "2026-03-31T06:00:00Z",
     "success_page_title": "Thank you",
     "success_page_message": "Your submission has been received.",
     "fields": [...]
   }
   ```
   - `is_active`: boolean, computed from `FormEntry.is_active`.
   - `active_date_from` / `active_date_to`: ISO 8601 datetime or `null`.
   - `success_page_title` / `success_page_message`: string (may be empty).
   - The endpoint should still return 200 for inactive forms so frontends can
     show a "form closed" message using the metadata. Use `is_active` flag
     rather than a 403 on GET.

2. PUT `/api/fobi-form-entry/{slug}/` rejects submissions for inactive forms:
   - Return HTTP 403 with `{"detail": "This form is not currently accepting submissions."}`.
   - Check `form_entry.is_active` before processing the submission.
   - Implement as a patch on `FobiFormEntryViewSet.update` (same pattern as
     existing patches in `src/unfold_fobi/patches/`), or as a viewset mixin
     registered via URL override — whichever is less invasive.

Implementation constraints
- Do not modify upstream fobi code.
- Keep the patch/mixin in `unfold_fobi` package scope.
- Use `FormEntry.is_active` — do not reimplement the date logic.
- Translatable error message via `gettext_lazy`.

Deliverables
- Updated GET endpoint with metadata fields.
- Active-date enforcement on PUT endpoint.
- Tests covering:
  - GET returns `is_active`, dates, and success page fields.
  - PUT returns 200 for active form.
  - PUT returns 403 for form past `active_date_to`.
  - PUT returns 403 for form before `active_date_from`.
  - PUT returns 200 when no active dates are set (always active).
- `poetry run pytest -q` passes.

Acceptance Criteria
- GET response contains `is_active`, `active_date_from`, `active_date_to`,
  `success_page_title`, `success_page_message`.
- PUT to an inactive form returns 403.
- PUT to an active form (or form with no date constraints) returns 200.
- Existing tests unaffected.
- `poetry run pytest -q` passes.

Tests to run
- `poetry run pytest -q`
