# Task T17 - Add widget type to GET /api/fobi-form-fields/{slug}/ response

Goal
- Add a `widget` key to each field object returned by the form-fields API endpoint.
- Allow frontend consumers to distinguish ambiguous field types (e.g. `CharField` rendered as `TextInput` vs `Textarea`, `ChoiceField` rendered as `Select` vs `RadioSelect`).
- Keep the change minimal — a single added key per field.

Problem statement
- The current API response includes `type` (the DRF/Django field class name) but not the widget class name.
- Several field types map to different HTML controls depending on the widget:
  - `CharField` → `TextInput` or `Textarea`
  - `ChoiceField` → `Select` or `RadioSelect`
- All other field types (EmailField, IntegerField, BooleanField, DateField, etc.) are unambiguous from `type` alone, but including `widget` is still useful for completeness and forward-compatibility.

Requested outcome
- Each field object in the `fields` array gains a `widget` key containing the widget class name:
  ```json
  {
    "name": "langer_text",
    "type": "CharField",
    "widget": "Textarea",
    "label": "Langer Text",
    "required": false,
    ...
  }
  ```

Suggested Skills
- Primary: `$unfold-dev-structured`.

Dependencies
- None. The endpoint already exists and has the widget object available at runtime.

Scope
- `src/unfold_fobi/api/views.py` — add one line to `get_form_fields` view.
- `tests/` — add or update test(s) covering the new key.
- `.agents/plans/FOBI_API_USAGE.md` — update field-type mapping docs.

Non-goals
- No new endpoints.
- No changes to PUT submission behavior.
- No changes to Fobi plugin architecture.
- No changes to serializer logic.

Implementation requirements
- Read `field.widget.__class__.__name__` for each field in the loop at `views.py:80`.
- Insert `"widget": field.widget.__class__.__name__` into `field_info` dict.
- No filtering or special-casing — emit the widget for every field.

Deliverables
- Updated `src/unfold_fobi/api/views.py` with the `widget` key.
- Test coverage verifying the key is present and correct for at least:
  - a `CharField` with `Textarea` widget,
  - a `CharField` with `TextInput` widget,
  - a `ChoiceField` with `Select` widget.
- Updated `.agents/plans/FOBI_API_USAGE.md` response examples.

Acceptance Criteria
- GET `/api/fobi-form-fields/{slug}/` returns `widget` for every field.
- Existing response fields (`name`, `type`, `label`, `required`, etc.) are unchanged.
- `poetry run pytest -q` passes.

Tests to run
- `poetry run pytest -q`
