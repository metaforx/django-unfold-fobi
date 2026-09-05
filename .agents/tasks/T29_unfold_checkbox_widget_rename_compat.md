# Task T29 - Fix `UnfoldAdminCheckboxSelectMultiple` import break on newer django-unfold

Type
- Fix. `django-unfold` removed the `UnfoldAdminCheckboxSelectMultiple` alias
  starting with 0.94.0, keeping only `UnfoldAdminCheckboxSelectMultipleWidget`.
  Any project that resolves `django-unfold>=0.94.0` alongside
  `django-unfold-fobi` currently fails at import time.

Goal
- Restore `unfold_fobi` importability against current `django-unfold`
  releases (0.94.0+) without breaking older supported versions, and publish
  a new release so downstream projects can unpin `django-unfold`.

Problem statement
- `src/unfold_fobi/forms/widgets.py` imports `UnfoldAdminCheckboxSelectMultiple`
  from `unfold.widgets` and uses it in `apply_unfold_widgets` (the
  `forms.CheckboxSelectMultiple` branch).
- That name existed as a thin subclass of `UnfoldAdminCheckboxSelectMultipleWidget`
  from at least 0.80.0 through 0.93.0, then was removed entirely in 0.94.0.
- Downstream, any project whose lockfile resolves `django-unfold>=0.94.0`
  (nothing in our own `pyproject.toml` upper-bounds it) hits, at Django
  startup, via `admin.autodiscover()` importing
  `unfold_fobi.admin.form_entry_proxy` → `unfold_fobi.forms` →
  `unfold_fobi.forms.widgets`:
  ```
  ImportError: cannot import name 'UnfoldAdminCheckboxSelectMultiple' from
  'unfold.widgets'. Did you mean: 'UnfoldAdminCheckboxSelectMultipleWidget'?
  ```
- Confirmed via PyPI wheel inspection: `UnfoldAdminCheckboxSelectMultiple`
  present in 0.80.0-0.93.0, absent from 0.94.0 onward.
  `UnfoldAdminCheckboxSelectMultipleWidget` (the base class) is present in
  every version checked back to 0.80.0, i.e. it already satisfies our
  declared floor (`django-unfold>=0.81.0` in `[project.dependencies]`,
  `>=0.80.0` in `[tool.poetry.dependencies]`).

Suggested Skills
- Primary: `$unfold-dev-structured`.
- Review: `$unfold-codex-reviewer`.

Dependencies
- None. Isolated to the widget-mapping module.

Scope
- `src/unfold_fobi/forms/widgets.py` — replace the direct import of
  `UnfoldAdminCheckboxSelectMultiple` with a try/except compat shim that
  falls back to `UnfoldAdminCheckboxSelectMultipleWidget` (see
  Implementation requirements below). The call site keeps using the
  `UnfoldAdminCheckboxSelectMultiple` name unchanged.
- `tests/` — add a regression test (new `tests/forms/` package; none exists
  yet for `unfold_fobi.forms.widgets`).
- `pyproject.toml` — reconcile the two duplicate dependency declarations
  (`[project.dependencies]` says `django-unfold>=0.81.0`, `[tool.poetry.dependencies]`
  says `>=0.80.0`) and confirm neither needs an upper bound.
- `src/unfold_fobi/__init__.py` — version bump.
- `README.md` — changelog/compat note if the repo keeps one inline (check
  before adding a new `CHANGELOG.md`; none currently exists).

Non-goals
- No broader widget-mapping refactor. Only the one renamed symbol.
- No new `CHANGELOG.md` file if the project has never used one — prefer
  whatever the existing release-notes convention is (check GitHub Releases
  history for the pattern used at 0.1.19 → 0.1.20 and 0.1.20 → 0.2.0 bumps).
- No changes to `django-unfold-modal` or `django-fobi` pins.
- Do not vendor or monkey-patch `unfold.widgets`.

Implementation requirements

1. Fix the import (`src/unfold_fobi/forms/widgets.py`) with a compat shim,
   not a hard cutover
   - Keep supporting the pre-0.94 alias instead of dropping it outright, so
     projects still pinned to an older `django-unfold` (0.81.0-0.93.0, our
     currently declared floor) keep working unchanged.
   - Pull `UnfoldAdminCheckboxSelectMultiple` out of the main
     `from unfold.widgets import (...)` block and replace it with a small
     try/except immediately below the import block, mirroring the existing
     pattern in `patches/content_text_wysiwyg.py` /
     `contrib/cms/cms_plugins.py`:
     ```python
     try:
         # django-unfold >= 0.94 removed this alias; only the Widget-suffixed
         # base class remains. Fall back to it so we still work on 0.94+
         # without dropping support for the 0.81.0-0.93.0 range that only
         # has the alias name.
         from unfold.widgets import UnfoldAdminCheckboxSelectMultiple
     except ImportError:
         from unfold.widgets import (
             UnfoldAdminCheckboxSelectMultipleWidget as UnfoldAdminCheckboxSelectMultiple,
         )
     ```
   - Leave the call site (`forms.CheckboxSelectMultiple` branch in
     `apply_unfold_widgets`) untouched — it keeps referring to
     `UnfoldAdminCheckboxSelectMultiple`, which now always resolves to a
     working widget class regardless of the installed `django-unfold`
     version.
   - Grep the rest of the package for any other reference to the old name
     (docs, tests, comments) before considering this done.

2. Dependency floor
   - Verify `UnfoldAdminCheckboxSelectMultipleWidget` exists at whatever
     floor version we end up declaring (0.80.0 confirmed OK). Do not bump
     the floor just for this fix — the base class predates the alias.
   - Reconcile `[project.dependencies]` vs `[tool.poetry.dependencies]` so
     both state the same `django-unfold` floor (pick the higher, currently
     `>=0.81.0`, unless investigation shows a reason to prefer the lower one).

3. Version bump
   - Bump `__version__` in `src/unfold_fobi/__init__.py` (patch bump, e.g.
     `0.2.0` → `0.2.1`, since this is a backward-compatible bugfix — no
     public API changed for consumers who only used the documented
     `INSTALLED_APPS` wiring).
   - Match whatever `pyproject.toml` version field mirrors `__init__.py`
     (check `[tool.hatch.version]` path — it reads from `__init__.py`
     directly, so only one place needs editing; confirm the `[tool.poetry]`
     table's own `version = "0.1.0"` field is unused/stale before touching
     it — if it's dead poetry metadata not used for the actual build,
     leave it alone or flag it, don't silently fix an unrelated
     pre-existing inconsistency as part of this task).

Regression prevention

Add `tests/forms/__init__.py` and `tests/forms/test_widgets.py`:

- **Import smoke test**: `from unfold_fobi.forms.widgets import apply_unfold_widgets`
  succeeds against whatever `django-unfold` version is installed in the
  test env (this alone reproduces the reported crash if the import is
  wrong).
- **CheckboxSelectMultiple mapping**: build a form with a
  `forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)`, run it
  through `apply_unfold_widgets`, and assert the field's widget is now an
  instance of `UnfoldAdminCheckboxSelectMultipleWidget`.
- **Shim resolves on current django-unfold**: assert
  `unfold_fobi.forms.widgets.UnfoldAdminCheckboxSelectMultiple` is the
  same object as `unfold.widgets.UnfoldAdminCheckboxSelectMultipleWidget`
  whenever the installed `django-unfold` lacks the old alias (i.e. the
  fallback branch actually ran, not just the primary import silently
  succeeding for an unrelated reason).
- **Single try/except, not scattered duplication**: a lightweight guard
  (grep-based is fine) that the compat try/except lives once in
  `forms/widgets.py` and isn't copy-pasted elsewhere in the package.

Deliverables
- Updated `src/unfold_fobi/forms/widgets.py` with the try/except compat
  shim (commented with the version boundary, per the snippet above).
- `tests/forms/test_widgets.py` with the regression tests above.
- Reconciled `django-unfold` floor in `pyproject.toml`.
- Version bump in `src/unfold_fobi/__init__.py`.
- `poetry run pytest -q` passes with the currently installed `django-unfold`
  in the dev venv (0.93.0 at time of writing — also worth confirming
  locally against a `pip install django-unfold>=0.94` in a throwaway venv,
  since the dev venv itself may be pinned old).

Acceptance Criteria
- `python -c "import unfold_fobi.forms.widgets"` succeeds against
  `django-unfold==0.93.0` (last version with the old alias) and against
  the latest published `django-unfold` (0.105.0 at time of writing, no
  old alias).
- `CheckboxSelectMultiple` fields still render with Unfold's styled
  checkbox widget — no visual/behavioral regression.
- `poetry run pytest -q` passes.
- The only reference to the bare `UnfoldAdminCheckboxSelectMultiple` name
  left in `src/` is the single try/except shim in `forms/widgets.py` —
  no duplicate shims, no direct unguarded import of it from `unfold.widgets`
  elsewhere in the package.

Tests to run
- `poetry run pytest -q tests/forms/`
- `poetry run pytest -q`

Release
- After merge and reviewer approval: tag and publish the version-bumped
  package to PyPI so downstream projects (e.g. `djangocms-test`) can
  unpin their `django-unfold==0.93.0` workaround and move back to a
  floor-only constraint.

Branch
- `fix/t29-unfold-checkbox-widget-rename-compat`.
- Do not commit or push until reviewer approval.
