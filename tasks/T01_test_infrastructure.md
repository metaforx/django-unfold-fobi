# Task T01 - Test Infrastructure for Form Builder

Goal
- Add a minimal, repo-local test setup for `unfold_fobi` form-building flows.

Scope
- Create a Django test project under `tests/` (settings, urls, wsgi/asgi optional).
- Configure installed apps for Unfold + Fobi + `unfold_fobi` integration.
- Add only models required to exercise form-building scenarios.
- Do not introduce unrelated demo/domain models.
- Add pytest configuration and basic fixtures (`admin_client`, test users, URL helpers).
- Add Playwright runner/config scaffold (no UI cases yet).

Non-goals
- No add/edit UI refactors.
- No package metadata refactor.

Deliverables
- `tests/` Django test project bootstrapped.
- `pytest` config and smoke test(s) proving setup works.
- Playwright config scaffold wired to local test server.

Acceptance Criteria
- `pytest -q` runs and collects tests successfully.
- Test Django project starts and serves admin with `unfold_fobi` enabled.

Tests to run
- `poetry run pytest -q`
