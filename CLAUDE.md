# CLAUDE.md

This file defines how Claude Code should work in this repository.

## Project

`unfold_fobi` integrates `django-fobi` form building into Django Unfold admin.

Primary goal:
- deliver reusable `unfold_fobi` integration with consistent Unfold UX, correct Django behavior, i18n readiness, and automated verification.

## Source Of Truth

Read these first, in order:
1. `plans/IMMUTABLE_BASE_PLAN.md`
2. `plans/UNFOLD_FOBI_PLAN.md`
3. active task file in `tasks/` (T01-T07)

If there is any conflict, `UNFOLD_FOBI_PLAN.md` goals win.

## Mandatory Rules

- Work incrementally; do not rebuild from scratch.
- Keep changes scoped to `unfold_fobi` integration concerns.
- Use Django-native patterns (views/forms/admin/permissions/i18n).
- Use Unfold-native UI patterns (tabs/actions/fieldsets/breadcrumbs/legends/buttons/selects).
- Keep template overrides minimal and targeted.
- Preserve existing behavior unless the task explicitly changes it.
- Never push or merge a feature branch automatically.
- Push/merge only when explicitly requested by the human reviewer.

## Non-Goals

- No changes to public form rendering/submission outside admin builder scope.
- No changes to Fobi plugin architecture/business logic.
- No DB schema redesign (except minimal test-support structures).
- No URL contract breaks for existing admin/form-builder routes.
- No broad upstream template forks.
- No redesign of unrelated admin pages.
- No new frontend frameworks or third-party UI libraries.

## Allowed Files

Python:
- `src/unfold_fobi/admin.py`
- `src/unfold_fobi/views.py`
- `src/unfold_fobi/context_processors.py`
- `src/unfold_fobi/forms.py` (only when required)
- `src/unfold_fobi/fobi_themes.py`
- `src/unfold_fobi/apps.py` (only for goal-required cleanup)

Templates:
- `src/unfold_fobi/templates/unfold_fobi/*.html`
- `src/unfold_fobi/templates/override_simple_theme/*.html`
- `src/unfold_fobi/templates/override_simple_theme/snippets/*.html`
- `src/unfold_fobi/templates/unfold_fobi/components/*.html`

Static:
- `src/unfold_fobi/static/unfold_fobi/js/*`
- `src/unfold_fobi/static/unfold_fobi/css/*`

Project/test/docs:
- `tests/*`
- `pyproject.toml`, `MANIFEST.in`, `README.md`
- `plans/*`, `tasks/*`

## Task Order

Follow tasks in strict sequence:
1. `tasks/T01_test_infrastructure.md`
2. `tasks/T02_package_scaffold.md`
3. `tasks/T03_pytest_cases.md`
4. `tasks/T04_playwright_ui.md`
5. `tasks/T05_add_view_i18n.md`
6. `tasks/T06_edit_view_structure_tabs.md`
7. `tasks/T07_edit_view_actions_grid.md`

`T03` and `T04` are verification gates and must be reused after each later implementation step.

## Verification

Per task:
- run `poetry run pytest -q`
- run Playwright for UI-impacting tasks (`npx playwright test` or pytest-playwright equivalent)

Required coverage:
- add-view grouping/date fieldset behavior
- i18n extraction/rendering behavior
- edit-view tabs/legend/actions/breadcrumbs behavior
- ordering auto-save behavior
- no regressions in completed behavior

## Test Server Pattern

Use repo-local structure for tests:
- `tests/server/manage.py`
- `tests/server/testapp/`
- SQLite default for local/manual run (`tests/server/db.sqlite3`)

Manual run support is additive; automated tests remain the default verification path.

## Skills

Task files define suggested skills. Default mapping:
- T01-T05: `$unfold-dev-structured`
- T06-T07: `$unfold-dev-advanced`
- review: `$unfold-codex-reviewer`
- debug fallback: `$unfold-debug-cleanup` or `$unfold-debug-refactor`

## Definition Of Done

All must be true:
- task acceptance criteria met
- required tests pass locally
- pending `UNFOLD_FOBI_PLAN` goals implemented or explicitly deferred with reason
- docs/config remain consistent with shipped behavior
