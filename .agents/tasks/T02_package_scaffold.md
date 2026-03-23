# Task T02 - Package Scaffold (django-unfold-fobi)

Goal
- Follow the same package scaffold pattern as `~/code/django-unfold-modal`.
- Use `django-unfold-fobi` as the distribution name for `pip`/Poetry.
- Keep `unfold_fobi` as the Django app/import path for `INSTALLED_APPS` and Python imports.

Scope
- Set package/build metadata around the name split:
  - distribution/package name: `django-unfold-fobi`.
  - Django app module: `unfold_fobi`.
- Ensure `pyproject.toml` has `[project]` + `[build-system]` (Hatchling) ready for PyPI builds.
- Keep `tool.poetry` for dependency management (dev/test workflow).
- Keep app package structure under `src/unfold_fobi/` and AppConfig discovery intact.
- Update README install/config examples to reflect:
  - installation with `django-unfold-fobi`;
  - Django settings usage with `unfold_fobi`.
- Keep repository URLs explicit and ready for later GitHub rename/alignment.

Non-goals
- No feature/UI behavior changes.
- No refactor of runtime module path away from `unfold_fobi`.

Deliverables
- Updated `pyproject.toml` metadata aligned with the naming convention.
- `README.md` installation and setup examples aligned with the naming convention.
- Verified package scaffold consistency with the `django-unfold-modal` pattern.

Acceptance Criteria
- `pip install django-unfold-fobi` / `poetry add django-unfold-fobi` is the documented install path.
- `python -c "import unfold_fobi"` works in project environment.
- `INSTALLED_APPS` continues to use `"unfold_fobi"` (not `"django-unfold-fobi"`).
- Package metadata is valid for build.

Tests to run
- `poetry run pytest -q`
- `python -m build`