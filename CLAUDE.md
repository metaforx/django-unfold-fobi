# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**unfold-modal** is a Django app package that replaces admin related-object popups with Unfold-styled modals using iframes. It integrates with django-unfold (a Tailwind CSS-based Django admin theme) without modifying Django or Unfold internals.

Key constraints from `plans/IMMUTABLE_BASE_PLAN.md`:
- No monkeypatching or runtime patching
- Only override templates listed in Integration Surface
- Use iframe strategy for v1 with clean seam for future fetch-inject/drawer variants
- Reuse existing Django dismiss functions (dismissAddRelatedObjectPopup, etc.)

## Musts (Strict)
- Follow `plans/IMMUTABLE_BASE_PLAN.md` exactly; deviations require human approval.
- Template overrides are limited to `admin/base_site.html` and `admin/popup_response.html`.
- No edits to Django or Unfold internals.
- No inline formset add/remove UI changes (only related fields inside inline forms).
- Use Hatch for packaging `unfold-modal`.
- Local tests only; no CI assumptions.

## UX Constraints
- ESC closes modal.
- Modal body scrolls; background does not.
- Locking background scroll must not cause page jump.

## Development Commands

```bash
# Run tests
pytest -q

# Start test server (after T01 infrastructure is set up)
python manage.py runserver

# Linting (uses Ruff, follows django-unfold patterns)
ruff check .
ruff format .

# Playwright browser tests (after T07 setup)
pytest --browser chromium
```

## Architecture

### Integration Surface (allowed modifications only)
- `admin/base_site.html` - Extend Unfold base; add JS include
- `admin/popup_response.html` - Replace opener calls with postMessage + fallback
- `unfold_modal/static/unfold_modal/js/related_modal.js` - Modal JS module
- `unfold_modal/static/unfold_modal/css/related_modal.css` - Optional styling

### Settings
- `UNFOLD_MODAL_ENABLED` (default: True)
- `UNFOLD_MODAL_VARIANT` = "iframe" (reserved for future "fetch")
- `UNFOLD_MODAL_PRESENTATION` = "modal" (reserved for future "drawer")

### Data Flow
1. User clicks related widget action
2. JS intercepts `django:show-related` or `django:lookup-related`, prevents default
3. Opens modal with iframe loading popup URL (`_popup=1`)
4. On success, `popup_response.html` posts payload via postMessage to parent
5. Parent calls existing Django dismiss functions to update widget

### Package Structure
```
unfold_modal/
├── __init__.py
├── apps.py              # AppConfig with settings defaults
├── static/
│   └── unfold_modal/
│       ├── js/related_modal.js
│       └── css/related_modal.css
└── templates/
    └── admin/
        ├── base_site.html
        └── popup_response.html
pyproject.toml            # Hatch build config (project root)
```

## Compatibility

- Django 5.x
- Unfold 0.52.0+
- Supported widgets: ForeignKey select, ManyToMany select, OneToOne select, raw_id_fields, autocomplete_fields (Select2), inline form related fields

## Task Reference

Tasks are in `tasks/` directory (T01-T07). Follow in order:
- T01: Test infrastructure and demo project
- T02: Package scaffold with Poetry (deps) + Hatch (build)
- T03: Modal JS core
- T04: popup_response template override
- T05: Admin template injection
- T06: Pytest cases
- T07: Playwright UI tests

## Git Workflow

- Create new feature branches from `development`.
- Feature branches: `feat/<short-name>`
- Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`
- Run tests before committing; commit only after tests pass

## Review Workflow

Workflow: code → review → fix → merge → stop
- Code changes on feature branch.
- Run review using `$unfold-codex-reviewer`.
- Apply fixes if needed.
- Re-run review until clean.
- Merge into `development`.
- Stop (do not continue on the same branch).
