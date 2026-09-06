# Task T29a - Fix `widget_map` field-type shadowing (CheckboxSelectMultiple / RadioSelect)

Type
- Fix, follow-up to T29 (merged).

Why this follow-up exists
- A Sourcery review comment on T29's PR pointed out that
  `tests/forms/test_widgets.py::test_checkbox_select_multiple_mapping` only
  exercises the compat shim via a `MultipleChoiceField` subclass kept
  deliberately outside `widget_map` — not via the real field shape fobi's
  `checkbox_select_multiple` plugin actually builds.
- Investigation confirmed a real, pre-existing bug, unrelated to the T29
  import fix itself. T29's own non-goals rule out fixing it there ("No
  broader widget-mapping refactor. Only the one renamed symbol."), so it's
  a separate task rather than a T29 subtask.

Goal
- `CheckboxSelectMultiple` and `RadioSelect` widgets set explicitly on a
  form field render as Unfold-styled checkboxes/radio buttons in the admin,
  not as a select dropdown.

Problem statement
- In `apply_unfold_widgets_to_form` (`src/unfold_fobi/forms/widgets.py`),
  `elif field_type in widget_map:` (line 202) matches on exact field type
  before the widget-type introspection branches further down ever run.
- `widget_map` maps `forms.MultipleChoiceField` → `UnfoldAdminSelectMultipleWidget`
  (line 190) and `forms.ChoiceField` → `UnfoldAdminSelectWidget` (line 188).
  Both are exact-type matches, so they fire first regardless of the field's
  actual widget.
- This shadows `elif widget_type == forms.CheckboxSelectMultiple` (lines
  265-266) and `elif widget_type == forms.RadioSelect` (lines 248-250) —
  those branches never run for a field built the normal way.
- fobi's own plugins build fields exactly the shadowed way:
  - `checkbox_select_multiple` plugin:
    `MultipleChoiceField(widget=CheckboxSelectMultiple(...))`
  - `radio` plugin (`fobi/contrib/plugins/form_elements/fields/radio/base.py`):
    `ChoiceField` with `widget=RadioSelect(...)`
  - Both plugin fields render as select dropdowns in the Unfold admin
    instead of checkboxes/radio buttons.
- No existing workaround anywhere in `src/`.

Scope
- `src/unfold_fobi/forms/widgets.py` only.
- `tests/forms/test_widgets.py`.
- `src/unfold_fobi/__init__.py` — version bump.

Non-goals
- No other `widget_map` reordering or entries beyond these two.
- No unrelated cleanup of `apply_unfold_widgets_to_form`.
- No changes to fobi's plugin code.

Implementation requirements

1. Fix the shadowing in `apply_unfold_widgets_to_form`
   - Mirror the existing `Textarea` special-case already at the top of the
     field loop (checked via `isinstance(field.widget, forms.Textarea)`
     before `elif field_type in widget_map:`).
   - Add two more `isinstance(field.widget, ...)` checks in the same spot,
     before `elif field_type in widget_map:`:
     - `forms.CheckboxSelectMultiple` → `UnfoldAdminCheckboxSelectMultiple`
     - `forms.RadioSelect` → `UnfoldAdminRadioSelectWidget`
   - Leave `widget_map` and the later `elif widget_type == ...` branches
     untouched — they still serve field types that aren't in `widget_map`.

2. Version bump
   - Bump `__version__` in `src/unfold_fobi/__init__.py`: `0.2.1` → `0.2.2`
     (patch, backward-compatible bugfix), same pattern T29 used.

Regression prevention

Update `tests/forms/test_widgets.py`:
- `test_checkbox_select_multiple_mapping`: use the real
  `forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)` shape
  directly; drop the now-unnecessary `_CustomMultiChoiceField` workaround.
- Add an analogous test:
  `forms.ChoiceField(widget=forms.RadioSelect)` through
  `apply_unfold_widgets_to_form` → asserts `UnfoldAdminRadioSelectWidget`.
- Keep the existing import-smoke, shim-resolution, and
  no-duplicate-shim tests as-is.

Deliverables
- Updated `src/unfold_fobi/forms/widgets.py` with the two extra
  widget-type checks.
- Updated `tests/forms/test_widgets.py`.
- Version bump in `src/unfold_fobi/__init__.py`.
- `poetry run pytest -q` passes.

Acceptance Criteria
- A `forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)` field
  run through `apply_unfold_widgets_to_form` ends up with an
  `UnfoldAdminCheckboxSelectMultipleWidget` instance (or the pre-0.94 alias
  instance), not `UnfoldAdminSelectMultipleWidget`.
- A `forms.ChoiceField(widget=forms.RadioSelect)` field run through
  `apply_unfold_widgets_to_form` ends up with an `UnfoldAdminRadioSelectWidget`
  instance, not `UnfoldAdminSelectWidget`.
- `poetry run pytest -q` passes.
- No other `widget_map`-routed field type changes behavior.

Tests to run
- `poetry run pytest -q tests/forms/`
- `poetry run pytest -q`

Suggested Skills
- Primary: `$unfold-dev-structured`.
- Review: `$unfold-codex-reviewer`.

Dependencies
- None. Same file T29 touched.

Release
- After merge and reviewer approval: tag and publish the version-bumped
  package to PyPI.

Branch
- `fix/t29a-widget-map-field-type-shadowing` (cut from `main` after T29's
  merge).
- Do not commit or push until reviewer approval.
