# Task T17a - Fix widget fallbacks for BooleanField and EmailField

Goal
- Ensure the `widget` key in the form-fields API response is correct for all
  built-in fobi field types, even when upstream plugins omit or misname the widget.

Problem statement
- T17 added the `widget` key by reading `field_kwargs["widget"]` from each fobi
  plugin's `get_form_field_instances()` return value.
- Two plugins produce incorrect results:
  1. **BooleanField** (`boolean` plugin): `field_kwargs` has no `"widget"` key at
     all, so the API returns `"widget": null`. The correct widget for
     `BooleanField` is `CheckboxInput`.
  2. **EmailField** (`email` plugin): `field_kwargs["widget"]` is
     `TextInput(attrs={"type": "email"})` — fobi uses a `TextInput` with a
     `type=email` HTML attribute instead of Django's `EmailInput` widget class.
     The API returns `"widget": "TextInput"` instead of `"EmailInput"`.

Root cause
- These are upstream fobi plugin choices, not bugs in `unfold_fobi`.
- The boolean plugin relies on Django's `BooleanField` default widget
  (`CheckboxInput`) by not specifying one.
- The email plugin predates Django's `EmailInput` widget and uses
  `TextInput(type=email)` instead.

Requested outcome
- `_build_widget_map` resolves the correct widget name for every field, using
  these fallback strategies (in order):
  1. Explicit widget from `field_kwargs["widget"]` (existing behavior).
  2. If absent, instantiate the field class with `field_kwargs` and read the
     default widget from the instance (covers BooleanField → CheckboxInput).
  3. If the widget is `TextInput` but `field_kwargs` contains
     `attrs={"type": "email"}` (or the field class is `EmailField`), resolve to
     `"EmailInput"` so consumers get the semantic widget name.

Suggested Skills
- Primary: `$unfold-dev-structured`.

Dependencies
- T17 (widget key in API response).

Scope
- `src/unfold_fobi/api/views.py` — adjust `_build_widget_map` fallback logic.
- `tests/api/test_form_fields.py` — add boolean and email widget assertions.

Non-goals
- No patching of upstream fobi plugins.
- No changes to other API endpoints or response keys.

Implementation requirements
- Keep the fix inside `_build_widget_map`. No new functions or modules.
- For missing widget: instantiate the field class from the tuple
  (`field_cls(**field_kwargs)`) and read `.widget.__class__.__name__`.
- For email TextInput workaround: if field class is `EmailField` (or a subclass)
  and resolved widget is `TextInput`, override to `"EmailInput"`.
- Both fixes are data-driven from the plugin output — no hardcoded plugin UID maps.

Deliverables
- Updated `_build_widget_map` with fallback logic.
- Tests for `BooleanField` → `CheckboxInput` and `EmailField` → `EmailInput`.
- `poetry run pytest -q` passes.

Acceptance Criteria
- `boolean` field returns `"widget": "CheckboxInput"`.
- `email` field returns `"widget": "EmailInput"`.
- All other fields continue to return correct widgets.
- No new dependencies or modules.
- `poetry run pytest -q` passes.

Tests to run
- `poetry run pytest -q`
