# Immutable Base Plan - unfold_fobi

## 1. Purpose
This document is the immutable execution contract for integrating `django-fobi` form building into Unfold admin via `unfold_fobi`.

Primary objective:
- Deliver a reusable, production-ready `unfold_fobi` package with consistent Unfold UX, correct Django behavior, i18n readiness, and automated verification.

## 2. Project Reality
- The project already works and contains significant custom integration code.
- Work is incremental and verification-driven.
- Do not rebuild from scratch.

## 3. Source of Truth
- Product goals are defined by `plans/UNFOLD_FOBI_PLAN.md`.
- If task wording conflicts with goal intent, `UNFOLD_FOBI_PLAN` wins.

## 4. Immutable Engineering Rules
- Use Django-native patterns (views, forms, admin, permissions, i18n).
- Use Unfold-native UI patterns (tabs, actions, fieldsets, breadcrumbs, legends, buttons, selects).
- Keep template overrides minimal and targeted.
- Keep changes scoped to `unfold_fobi` integration concerns.
- Preserve existing behavior unless a task explicitly changes it.
- Establish test gates early and run them after each implementation task.
- Never push or merge a feature branch automatically; push/merge only when explicitly requested by the human reviewer.

## 5. Explicit Non-Goals
- No changes to public form rendering/submission behavior outside admin builder requirements.
- No changes to Fobi plugin architecture or plugin business logic.
- No database schema redesign; only minimal test-support data structures are allowed.
- No URL contract breaks for existing admin/form-builder routes.
- No broad template forks of upstream Fobi/Unfold templates.
- No redesign of unrelated admin pages (outside target add/edit builder views).
- No new frontend frameworks or third-party UI libraries.

## 6. Allowed Integration Surface
Python:
- `src/unfold_fobi/admin.py`
- `src/unfold_fobi/views.py`
- `src/unfold_fobi/context_processors.py`
- `src/unfold_fobi/forms.py` (only where required for builder consistency)
- `src/unfold_fobi/fobi_themes.py` and `src/unfold_fobi/apps.py` only for integration cleanup required by goals

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

## 7. Back-Check Findings (Current Code)
### 7.1 Add View
Code-verified complete:
- Add view is Unfold admin based (`FormEntryProxyAdmin(ModelAdmin)`).
- Fieldsets are grouped by purpose in `get_fieldsets`.
- Date fields are grouped under translated "Active dates".

Still required:
- i18n extraction verification workflow (`django.po`) is not yet codified in tests/tasks.

### 7.2 Edit View
Code-verified complete:
- Custom edit view exists via `FormEntryEditView(UnfoldModelAdminViewMixin, FobiEditFormEntryView)`.
- Legend/action components are present and translated.
- Ordering auto-save is implemented; no "Save ordering" button in template.

Code-verified gaps or inconsistencies:
- Tabs still carry legacy residue (`tab-links` class, legacy `fobi_unfold.js` logic expecting `#tabs`).
- "Add form element" action is rendered in legend/action row inside tab content, not clearly on the same top nav row as tabs.
- Handler section still uses `unfold_result_list` changelist-style rendering (not full grid/card builder layout).
- Breadcrumb contract for `Unfold_Fobi -> Forms (builder) -> <form name>` is not explicitly implemented in view/template logic.
- H1 suppression is not explicitly guaranteed by template overrides.

### 7.3 Project Infrastructure
- No `tests/` infrastructure exists yet.
- Packaging metadata exists but still includes placeholder author/repository values.

## 8. Goal Baseline from UNFOLD_FOBI_PLAN
### Add View (`FormEntryProxy` add)
Completed:
- [x] Add view renders through Unfold layout.
- [x] Fieldsets grouped by purpose.
- [x] Date/time fields grouped in dedicated section.

Pending:
- [ ] Complete i18n wrapping/extraction verification for all add-view UI strings.

### Edit View (`FormEntryProxy` edit)
Completed:
- [x] Legend/action components integrated.
- [x] Ordering auto-save implemented and "Save ordering" removed.

Pending:
- [ ] Finalize Unfold custom-page structure details (including guaranteed H1 removal behavior).
- [ ] Remove legacy tab residue and fully align tabs with Unfold native patterns.
- [ ] Enforce breadcrumb structure and active item contract.
- [ ] Align "Add form element" control placement to target nav row behavior.
- [ ] Replace remaining changelist/table-like sections with Unfold grid/card-style builder presentation.
- [ ] Confirm all edit-view actions consistently use Unfold styling.

## 9. Mandatory Delivery Sequence
1. `tasks/T01_test_infrastructure.md`
2. `tasks/T02_package_scaffold.md`
3. `tasks/T03_pytest_cases.md`
4. `tasks/T04_playwright_ui.md`
5. `tasks/T05_add_view_i18n.md`
6. `tasks/T06_edit_view_structure_tabs.md`
7. `tasks/T07_edit_view_actions_grid.md`

Execution rule:
- T03/T04 are verification gates and must be run after each subsequent implementation task.

## 10. Verification Contract
Per task:
- Run `poetry run pytest -q`.
- Run Playwright suite for UI-impacting tasks.

Coverage outcomes required:
- Add view grouping and date fieldset behavior verified.
- i18n string extraction/rendering workflow verified.
- Edit view tabs/legend/actions/breadcrumbs behavior verified.
- Ordering auto-save verified.
- No regression of existing working behavior.

## 11. Definition of Done
All must be true:
- Tasks T01-T07 completed in order.
- Pending goals from `UNFOLD_FOBI_PLAN` are implemented or explicitly deferred with reason.
- Pytest passes locally.
- Playwright passes locally.
- Package metadata/build and runtime docs are consistent with shipped integration.
