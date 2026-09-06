# T29a — `widget_map` field-type shadowing (CheckboxSelectMultiple / RadioSelect)

## Fix

`apply_unfold_widgets_to_form` (`src/unfold_fobi/forms/widgets.py`) matched
on exact field type (`elif field_type in widget_map`) before ever checking
the field's actual widget type. `forms.MultipleChoiceField` and
`forms.ChoiceField` are both `widget_map` keys, so a field built the normal
way — `MultipleChoiceField(widget=CheckboxSelectMultiple(...))`,
`ChoiceField(widget=RadioSelect(...))`, exactly how fobi's
`checkbox_select_multiple` and `radio` plugins build theirs — always hit
the generic dict match and rendered as select dropdowns, never reaching the
later `elif widget_type == forms.CheckboxSelectMultiple` /
`elif widget_type == forms.RadioSelect` branches.

Added two `isinstance(field.widget, ...)` checks at the top of the field
loop, in the same spot and mirroring the existing `Textarea` special-case,
before the `field_type in widget_map` lookup:

```python
elif hasattr(field, "widget") and isinstance(
    field.widget, forms.CheckboxSelectMultiple
):
    set_widget(field, UnfoldAdminCheckboxSelectMultiple)
elif hasattr(field, "widget") and isinstance(field.widget, forms.RadioSelect):
    set_widget(field, UnfoldAdminRadioSelectWidget)
```

`widget_map` and the later dead-but-harmless `elif widget_type == ...`
branches are untouched — they still serve field types outside `widget_map`.

## Other changes

- `tests/forms/test_widgets.py`: `test_checkbox_select_multiple_mapping` now
  uses the real `MultipleChoiceField(widget=CheckboxSelectMultiple)` shape
  directly (dropped the `_CustomMultiChoiceField` workaround it no longer
  needs). Added `test_radio_select_mapping` for the analogous `RadioSelect`
  case. Import-smoke, shim-resolution, and no-duplicate-shim tests
  unchanged.

## Tests

`poetry run pytest -q tests/forms/` → 5 passed.
`poetry run pytest -q` (full suite) → 293 passed, 4 skipped (pre-existing,
unrelated e2e/playwright skips).

## Origin

Found by a Sourcery review comment on T29's PR, pointing out its
regression test bypassed this exact shadowing bug via a subclass workaround
instead of exercising the real field shape. Deferred out of T29 (non-goals
ruled out a broader widget-mapping refactor there) into this follow-up,
per the repo's `T16a`-style letter-suffixed follow-up convention.

## Review

`codex review` (non-interactive, diff of `src/unfold_fobi/forms/widgets.py`,
`src/unfold_fobi/__init__.py`, `tests/forms/test_widgets.py`,
`.agents/tasks/T29a_widget_map_field_type_shadowing.md`) →
"No actionable correctness issues were found in the reviewed diff. The
added widget checks address the documented shadowing case and the test
suite passes."

## Status

Implemented and reviewed. Not committed/pushed — awaiting human review.
