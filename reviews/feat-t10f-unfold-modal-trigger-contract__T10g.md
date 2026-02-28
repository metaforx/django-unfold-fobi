# Review: T10g — Modal Iframe Content Refused

**Branch:** `feat/t10g-modal-iframe-content-refused`
**Status:** Done

## Summary

Fixed `127.0.0.1 refused to connect` when django-unfold-modal opens fobi
popup views in an iframe. Root cause: Django's `XFrameOptionsMiddleware`
defaulting to `X-Frame-Options: DENY`.

## Root Cause

Django's `XFrameOptionsMiddleware` sets `X-Frame-Options: DENY` by default.
The test settings had the middleware but no `X_FRAME_OPTIONS` override.
All responses were blocked from iframe embedding.

## Solution

Two-part fix:

1. **Settings (global):** Added `X_FRAME_OPTIONS = "SAMEORIGIN"` to test
   settings — required for any project using `django-unfold-modal`.

2. **View-level (targeted):** Set `response["X-Frame-Options"] = "SAMEORIGIN"`
   on all fobi popup view responses in `apps.py`:
   - On `_popup_http_response()` (intercepted redirect → popup close HTML).
   - On non-intercepted responses when `_is_popup()` is true.

   This makes popup views self-sufficient: they work in iframes even if the
   host project has `X_FRAME_OPTIONS = "DENY"` globally.

## Changes

| File | Description |
|------|-------------|
| `settings.py` | Added `X_FRAME_OPTIONS = "SAMEORIGIN"` |
| `apps.py` | Set SAMEORIGIN header on popup responses (both intercepted and non-intercepted paths) |
| `test_edit_view.py` | Added `TestIframeXFrameOptions` (5 tests) |
| `T10g-analysis.md` | Phase 0 diagnostic analysis note |

## Codex Review

- Round 1: P1 — intercepted popup response missing header (fixed).
- Round 2: No issues found.
