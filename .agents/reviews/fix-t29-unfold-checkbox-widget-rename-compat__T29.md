# T29 — `UnfoldAdminCheckboxSelectMultiple` import break on newer django-unfold

## Fix

`django-unfold` dropped the `UnfoldAdminCheckboxSelectMultiple` alias in
0.94.0, keeping only `UnfoldAdminCheckboxSelectMultipleWidget`. Any project
resolving `django-unfold>=0.94.0` hit an `ImportError` at Django startup via
`unfold_fobi.forms.widgets`.

`src/unfold_fobi/forms/widgets.py` now imports the name via a try/except
shim instead of the plain `from unfold.widgets import (...)` block:

```python
try:
    # django-unfold >= 0.94 dropped this alias; falls back to the Widget-suffixed class.
    from unfold.widgets import UnfoldAdminCheckboxSelectMultiple
except ImportError:
    from unfold.widgets import (
        UnfoldAdminCheckboxSelectMultipleWidget as UnfoldAdminCheckboxSelectMultiple,
    )
```

The `apply_unfold_widgets_to_form` call site is unchanged — it keeps
referring to `UnfoldAdminCheckboxSelectMultiple`, which now resolves on both
the pre-0.94 alias and 0.94+ base-class-only releases. Mirrors the existing
try/except compat pattern in `patches/content_text_wysiwyg.py` /
`contrib/cms/cms_plugins.py`.

## Other changes

- `pyproject.toml`: `[tool.poetry.dependencies]` `django-unfold` floor
  raised `>=0.80.0` → `>=0.81.0` to match `[project.dependencies]` (no
  upper bound — `UnfoldAdminCheckboxSelectMultipleWidget` exists at every
  version checked back to 0.80.0). `[tool.poetry] version = "0.1.0"` left
  untouched — confirmed dead (build is hatchling, `package-mode = false`,
  `[tool.hatch.version]` reads `__version__` from `__init__.py`).
- `src/unfold_fobi/__init__.py`: `__version__` `0.2.0` → `0.2.1` (patch,
  backward-compatible bugfix).
- `README.md`: no changelog entry added — repo has no inline
  changelog/`CHANGELOG.md` convention (version bumps are standalone `chore:`
  commits), per task non-goals.

## Tests

`tests/forms/__init__.py`, `tests/forms/test_widgets.py` (new package —
none existed for `unfold_fobi.forms.widgets` before):

- import smoke test
- `CheckboxSelectMultiple` → `UnfoldAdminCheckboxSelectMultipleWidget`
  mapping, via `apply_unfold_widgets_to_form`
- shim resolves to whatever `unfold.widgets` actually exposes (handles
  both alias-present and alias-absent installs)
- grep guard: the compat try/except appears exactly once in `src/`

`poetry run pytest -q tests/forms/` → 4 passed.
`poetry run pytest -q` (full suite) → 292 passed, 4 skipped (pre-existing,
unrelated e2e/playwright skips).
Also verified in a throwaway venv against `django-unfold==0.105.0` (latest,
no old alias): import succeeds, shim resolves to the Widget-suffixed class.

## Pre-existing quirk found, not fixed (out of scope per non-goals)

`apply_unfold_widgets_to_form`'s `widget_map` dict matches on exact field
type (`forms.MultipleChoiceField` → `UnfoldAdminSelectMultipleWidget`)
*before* falling through to widget-type introspection — so a
`forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)` (how
fobi's `checkbox_select_multiple` plugin actually builds its field) never
reaches the `CheckboxSelectMultiple` branch that hosts this shim; it's
mapped to a select-multiple dropdown instead. Unrelated to T29 (task's
non-goals explicitly forbid a broader widget-mapping refactor) — the
regression test uses a `MultipleChoiceField` subclass outside `widget_map`
to actually exercise the shim. Worth a separate task if checkbox-select
fields should render as checkboxes end-to-end.

## Review

`codex review` (non-interactive, diff of `pyproject.toml`,
`src/unfold_fobi/__init__.py`, `src/unfold_fobi/forms/widgets.py`,
`tests/forms/`) → **No issues found.**

## Status

Implemented and reviewed. Not committed/pushed — awaiting human review per
task instructions (`Do not commit or push until reviewer approval`).
