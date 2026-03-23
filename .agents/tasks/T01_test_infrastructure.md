# Task T01 - Test Infrastructure for Existing unfold_fobi Integration

Goal
- Create a repo-local test environment with a `tests/server/manage.py` + `tests/server/testapp/` structure and optional manual app run support.
- Keep automated testing as the default verification path (pytest + Playwright); manual runserver support is additive.

Suggested Skills
- Primary: `$unfold-dev-structured` (scoped infrastructure/setup task).
- Debug fallback: `$unfold-debug-cleanup` for small setup/test issues; `$unfold-debug-refactor` if root cause spans multiple modules.
- Review: `$unfold-codex-reviewer`.

Context from code back-check
- There is currently no `tests/` project.
- Existing implementation already includes custom admin/views/templates and should be tested as-is.

Required Structure
- `tests/server/manage.py`
- `tests/server/testapp/` (Django project package: settings/urls/wsgi/asgi)
- `tests/server/db.sqlite3` (default local/manual DB for the test server)
- `tests/` pytest modules and shared fixtures

Scope
- Build Django test server under `tests/server/testapp` with:
  - Unfold + Fobi + `unfold_fobi` configured.
  - URL wiring for admin, Fobi edit routes, and optional API endpoint coverage.
  - SQLite as default DB for local/manual runs.
- Add minimal seed setup for builder tests:
  - Admin user.
  - One editable `FormEntry` with at least one element and one handler.
- Add pytest bootstrap (`pytest.ini` or `pyproject` section), fixtures, and helper factories.
- Add Playwright scaffold for browser tests (runner config only, no heavy cases yet).
- Ensure server can be started manually via `python tests/server/manage.py runserver`.
- Add README guidance for test server setup and usage (`tests/server` structure, migrate, create admin user if needed, runserver, and test commands).

Non-goals
- No UI refactor.
- No package metadata changes.

Deliverables
- `tests/server/manage.py` and `tests/server/testapp/*`.
- SQLite-backed local test server config.
- Pytest collection smoke test.
- Playwright config scaffold usable by T04.
- README section describing how to set up and run the local test server.

Acceptance Criteria
- `poetry run pytest -q` collects and runs smoke tests.
- Manual run works: `python tests/server/manage.py runserver 8080`.
- Test server renders `admin:unfold_fobi_formentryproxy_add` and `admin:unfold_fobi_formentryproxy_edit`.
- README includes accurate, executable test server setup/run instructions.

Tests to run
- `poetry run pytest -q`