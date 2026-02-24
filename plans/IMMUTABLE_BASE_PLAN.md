# Immutable Base Plan - unfold_fobi

## 1. Purpose
This document is the immutable execution contract for integrating `django-fobi` form building into Unfold admin via `unfold_fobi`.

Primary objective:
- Deliver a reusable, production-ready `unfold_fobi` package with consistent Unfold UX, correct Django behavior, i18n readiness, and automated verification.

## 2. Project Reality
- The project already works.
- Implementation is incremental and verification-driven.
- Do not restart architecture or rebuild from scratch.

## 3. Source of Truth
All product goals come from `plans/UNFOLD_FOBI_PLAN.md`.
If a conflict appears between task wording and implementation details, `UNFOLD_FOBI_PLAN` goals win.

## 4. Immutable Engineering Rules
- Use Django-native patterns (views, forms, admin, templates, permissions, i18n).
- Use Unfold-native UI patterns (tabs, actions, fieldsets, breadcrumbs, legends, buttons, selects).
- Keep template overrides minimal and targeted.
- Keep changes scoped to `unfold_fobi` integration concerns.
- Preserve existing behavior unless a task explicitly changes it.
- Add/extend tests before broad refactors.
- Run verification at each step (pytest and Playwright where applicable).

## 5. Explicit Non-Goals
- No modal/popup strategy work.
- No iframe/fetch/drawer architecture decisions.
- No unrelated admin redesign.
- No new frontend frameworks.
- No unrelated domain model expansion.

## 6. Allowed Integration Surface
Python:
- `src/unfold_fobi/admin.py`
- `src/unfold_fobi/views.py`
- `src/unfold_fobi/context_processors.py`
- `src/unfold_fobi/forms.py` (only when required for Unfold form-builder consistency)

Templates:
- `src/unfold_fobi/templates/unfold_fobi/*.html`
- `src/unfold_fobi/templates/override_simple_theme/*.html`
- `src/unfold_fobi/templates/override_simple_theme/snippets/*.html`
- `src/unfold_fobi/templates/unfold_fobi/components/*.html`

Static assets:
- `src/unfold_fobi/static/unfold_fobi/js/*`
- `src/unfold_fobi/static/unfold_fobi/css/*`

Project/test/docs:
- `tests/*`
- `pyproject.toml`, `MANIFEST.in`, `README.md`
- `plans/*`, `tasks/*`

## 7. Goal Baseline from UNFOLD_FOBI_PLAN
### Add View (`FormEntryProxy` add)
Completed:
- [x] Add view renders through Unfold layout.
- [x] Fieldsets grouped by purpose.
- [x] Date/time fields grouped in dedicated section.

Pending:
- [ ] Complete i18n wrapping of all add-view UI strings.
- [ ] Verify translation extraction (`django.po` workflow).

### Edit View (`FormEntryProxy` edit)
Completed:
- [x] "Add form element" uses Unfold select pattern.
- [x] "Add form element" aligned right on tabs/action row.
- [x] "Save ordering" removed; ordering auto-saves.
- [x] Legend styling applied.

Pending:
- [ ] Ensure full Unfold custom-page structure.
- [ ] Remove H1 and keep H2/legend structure.
- [ ] Replace remaining legacy/jQuery tabs with Unfold tabs.
- [ ] Finalize active-tab behavior and accessibility.
- [ ] Update breadcrumbs to: `Unfold_Fobi -> Forms (builder) -> <form name>`.
- [ ] Apply consistent Unfold action button styling.
- [ ] Replace legacy table-striped areas with Unfold-style grid/card presentation.

## 8. Mandatory Delivery Sequence
1. `tasks/T01_test_infrastructure.md`
2. `tasks/T02_package_scaffold.md`
3. `tasks/T03_pytest_cases.md`
4. `tasks/T04_playwright_ui.md`
5. `tasks/T05_add_view_i18n.md`
6. `tasks/T06_edit_view_structure_tabs.md`
7. `tasks/T07_edit_view_actions_grid.md`

Execution rule:
- T03/T04 are early gates and must be run after each subsequent implementation task.

## 9. Verification Contract
Per task verification:
- Run `poetry run pytest -q`.
- Run Playwright suite for UI-impacting tasks.

Required coverage outcomes:
- Add view structure and grouping verified.
- i18n strings verified for extraction and rendering.
- Edit view layout/tabs/actions/breadcrumbs verified.
- Ordering auto-save behavior verified.
- No regression of existing completed behaviors.

## 10. Definition of Done
All conditions must be true:
- All items in mandatory sequence are completed.
- `UNFOLD_FOBI_PLAN` pending goals are either implemented or explicitly marked deferred with reason.
- Pytest passes locally.
- Playwright passes locally.
- Integration remains reusable as `unfold_fobi` package.
