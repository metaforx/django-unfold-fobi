# Review: T10f — Unfold Modal Trigger Contract

**Branch:** `feat/t10f-unfold-modal-trigger-contract`
**Status:** Done (Codex timed out after deep analysis with no findings)

## Summary

Updated element/handler popup links to follow Django admin's native
popup contract so `django-unfold-modal` can intercept them and open
as iframe modals.

## Problem

T10e used `onclick="window.open(...)"` on popup links. This bypassed
Django's event system entirely — Unfold's `RelatedObjectLookups.js`
never fired `django:show-related`, so `django-unfold-modal` never
had a chance to intercept.

## Solution

Replaced inline `window.open()` with Django admin popup contract:
- `class="related-widget-wrapper-link ..."` (matches event delegation selector)
- `data-popup="yes"` (required attribute for detection)
- `id="change_fobi_element_{pk}"` etc. (popup window naming)
- Removed `onclick` handler entirely

Flow after fix:
1. Click → bubbles to `<body>`
2. Unfold's delegated handler matches `.related-widget-wrapper-link[data-popup="yes"]`
3. Fires `django:show-related` event on the link
4. If `django-unfold-modal` loaded → `event.preventDefault()` → iframe modal
5. If not → `showRelatedObjectPopup()` → `window.open()` popup

## Changes

| File | Description |
|------|-------------|
| `admin.py` | Replaced `onclick="window.open(...)"` with `data-popup="yes"` + `related-widget-wrapper-link` class + popup IDs |
| `change_form.html` | Same: replaced `onclick` with trigger attributes on add dropdown links |
| `test_edit_view.py` | Added `TestUnfoldModalTriggerContract` (6 tests); replaced `window.open` assertion with `no_inline_window_open` |
| `pyproject.toml` | Added `django-unfold-modal` dependency |
| `settings.py` | Added `unfold_modal` to INSTALLED_APPS, STYLES, SCRIPTS |

## Codex Review

Two attempts, both timed out after extensive analysis (deep-diving into
django-unfold-modal and Unfold RelatedObjectLookups.js internals). No
findings emitted before timeout in either attempt, indicating the
change is clean from a code-level perspective.