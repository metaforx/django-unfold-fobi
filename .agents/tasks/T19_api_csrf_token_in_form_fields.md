# Task T19 - Return CSRF token in form-fields API response

Goal
- Include the CSRF token in the GET `/api/fobi-form-fields/{slug}/` response
  so frontends can submit forms via the PUT endpoint without a separate
  request to obtain the token.

Problem statement
- DRF's `SessionAuthentication` enforces CSRF on unsafe methods (PUT/POST).
- The frontend fetches form structure via `GET /api/fobi-form-fields/{slug}/`
  then submits via `PUT /api/fobi-form-entry/{slug}/`.
- The GET response does not include a CSRF token, so the frontend must either
  parse it from a cookie (requires `CSRF_COOKIE_HTTPONLY = False`) or make a
  separate request to obtain it.
- Returning the token in the form-fields response eliminates this friction.

Suggested Skills
- Primary: `$unfold-dev-structured`.

Dependencies
- T17/T17a (form-fields endpoint).

Scope
- `src/unfold_fobi/api/views.py` — add `csrf_token` to response envelope.
- `tests/api/test_form_fields.py` — assert key is present and non-empty.

Non-goals
- No changes to the PUT submission endpoint.
- No changes to authentication or CSRF middleware.

Implementation requirements
- Use `django.middleware.csrf.get_token(request)` to obtain the token.
  This also sets the CSRF cookie on the response.
- Add `"csrf_token": token` to the `form_structure` dict, before `"fields"`.
- One import, one line in the response dict.

Expected response
```json
{
  "id": 3,
  "slug": "test-form",
  "title": "Test Form",
  "csrf_token": "abc123...",
  "fields": [...]
}
```

The frontend includes this token as `X-CSRFToken` header on the PUT request.

Deliverables
- Updated `src/unfold_fobi/api/views.py`.
- Test asserting `csrf_token` is a non-empty string in the response.
- `poetry run pytest -q` passes.

Acceptance Criteria
- GET `/api/fobi-form-fields/{slug}/` returns `csrf_token` string.
- Token is valid for use in subsequent PUT requests.
- `poetry run pytest -q` passes.

Tests to run
- `poetry run pytest -q`
