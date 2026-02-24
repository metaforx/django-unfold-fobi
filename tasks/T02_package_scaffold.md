# Task T02 - Package Hardening for Current Repo State

Goal
- Align package/build metadata and docs with the current, already-implemented `unfold_fobi` integration.

Suggested Skills
- Primary: `$unfold-dev-structured` (docs/metadata/build hardening).
- Debug fallback: `$unfold-debug-cleanup` for build/test breakage during packaging updates.
- Review: `$unfold-codex-reviewer`.

Context from code back-check
- Packaging exists, but metadata includes placeholder author/repository values.
- Build/runtime docs should reflect actual integration paths and supported flow.

Scope
- Update `pyproject.toml` metadata:
  - authors/URLs/license/classifiers consistency.
  - runtime dependency declaration sanity.
- Verify `MANIFEST.in` and hatch build targets ship required templates/static assets.
- Align README packaging and integration sections with real code paths and routes.
- Add/verify minimal import/build smoke checks used in local verification.

Non-goals
- No feature/UI behavior changes.

Deliverables
- Correct package metadata.
- Distribution config validated for templates/static inclusion.
- Updated documentation for current installation/use.

Acceptance Criteria
- `python -c "import unfold_fobi"` succeeds.
- `python -m build` succeeds and artifacts include `templates/` and `static/` content.

Tests to run
- `poetry run pytest -q`
- `python -m build`
