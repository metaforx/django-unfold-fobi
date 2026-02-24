# Task T02 - Package Hardening (Existing Project)

Goal
- Align existing package metadata and distribution config with current `unfold_fobi` reality.

Status
- Package scaffold already exists; this task is refinement, not initial creation.

Scope
- Validate `pyproject.toml` metadata (name, description, URLs, authors, classifiers, dependencies).
- Ensure build targets include `src/unfold_fobi` and shipped templates/static assets.
- Verify `MANIFEST.in` and wheel/sdist include required runtime files.
- Update README install/use sections to match current admin + form-builder flow.
- Add a minimal import/build smoke check in tests or CI command docs.

Non-goals
- No UI behavior changes.
- No feature additions beyond packaging/docs correctness.

Deliverables
- Updated packaging metadata and distribution config.
- README/package docs aligned with current project behavior.
- Smoke validation command documented and passing locally.

Acceptance Criteria
- `python -c "import unfold_fobi"` works.
- `python -m build` succeeds and artifacts include required templates/static files.

Tests to run
- `poetry run pytest -q`
- `python -m build`
