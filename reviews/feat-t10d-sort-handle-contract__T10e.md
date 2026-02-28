# Review: T10e — Popup Modal Compat for Element Edit/Add

**Branch:** `feat/t10e-popup-modal-compat`
**Status:** Done (7 Codex rounds → clean)

## Summary

Added popup-mode compatibility so that element/handler edit, add, and
delete actions open in a popup window and close-and-reload the parent
change form instead of navigating away.

## Changes

| File | Description |
|------|-------------|
| `admin.py` | Added `?_popup=1` + `onclick="window.open(...)"` to all element/handler action links |
| `apps.py` | Added `_patch_fobi_popup_response()` — intercepts fobi view redirects in popup mode, returns popup response HTML |
| `change_form.html` | Added `?_popup=1` + `onclick` to add-element/add-handler dropdown links |
| `popup_response.html` | New template: closes popup window and reloads parent via `window.opener.location.reload()` or `postMessage` for iframe modals |
| `test_edit_view.py` | 7 new tests (TestPopupModeLinks: 5, TestPopupResponse: 2) |

## Codex Rounds

| # | Finding | Fix |
|---|---------|-----|
| 1 | P1: popup flag lost on POST (fobi form `action="{{ request.path }}"` strips query) | Session-based counter (`_fobi_popup_count`) |
| 2 | P2: stale session on abandoned popup | Non-popup GET fully clears counter |
| 3 | P2: concurrent popup race (boolean cleared on first) | Changed to counter (increment/decrement) |
| 4 | P2: stale counter accumulation | Non-popup GET does `session.pop()` |
| 5 | P2: GET redirects intercepted for login/auth | POST-only interception for edit views |
| 6 | P1: same-tab dead-end (links not opened as popup) | Added `window.open()` onclick to all popup links |
| 6 | P2: no-form plugins save & redirect on GET | Intercept GET redirects for add views (like delete views) |
| 7 | P2: auth redirect intercepted as success | Login URL check in `_is_success_redirect()` |
| 7 | P2: stale counter leaks popup mode | Already mitigated by non-popup GET reset; narrow edge only |

## Known Limitations

- Session counter is a POC approach; production should use a per-popup
  token or rely on `django-unfold-modal` iframe integration.
- `postMessage` uses `'*'` origin — acceptable for POC, should be
  restricted in production.
