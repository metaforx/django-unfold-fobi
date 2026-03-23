# T10g Analysis: Modal Iframe Content Refused

**Branch:** `feat/t10g-modal-iframe-content-refused`
**Date:** 2026-02-28

## Observed Issue

- `django-unfold-modal` opens a modal and creates an iframe.
- Iframe URL: `http://127.0.0.1:8080/de/admin/fobi/forms/elements/edit/11/?_popup=1`
- Iframe shows `127.0.0.1 refused to connect` (Chrome) / blank frame.
- Same URL opens fine in a standalone browser tab.

## Root Cause

**Classification: `SETTINGS_FIX` + `VIEW_HEADER_FIX`**

Django's `XFrameOptionsMiddleware` (line 72 of `settings.py`) sets the
`X-Frame-Options` response header on every response. When
`settings.X_FRAME_OPTIONS` is not explicitly configured, Django defaults to
`"DENY"`, which instructs the browser to block the page from being rendered
inside any `<iframe>`.

Evidence:
- `XFrameOptionsMiddleware` is present in MIDDLEWARE.
- No `X_FRAME_OPTIONS` setting exists in `tests/server/testapp/settings.py`.
- `django-unfold-modal`'s own test project sets `X_FRAME_OPTIONS = "SAMEORIGIN"`.
- The fobi popup views do not set `X-Frame-Options` on their responses.

The browser correctly refuses to load the iframe content because the server
response says `X-Frame-Options: DENY`.

## Fix Plan

### Part 1 — Settings (global)

Add `X_FRAME_OPTIONS = "SAMEORIGIN"` to `tests/server/testapp/settings.py`.
This allows same-origin iframe embedding for the entire admin site, which is
required for `django-unfold-modal` to function.

### Part 2 — View-level header (targeted)

In `apps.py` `_patch_fobi_popup_response`, explicitly set
`response["X-Frame-Options"] = "SAMEORIGIN"` on all responses from wrapped
fobi views when popup mode is detected. This ensures popup views work in
iframes even if a production deployment has `X_FRAME_OPTIONS = "DENY"`
globally. Django's middleware skips responses that already have the header set.

### Why both parts?

- Part 1 is required for the test/dev server and any project that uses
  `django-unfold-modal` — it must be documented as a setup requirement.
- Part 2 makes the integration self-sufficient: fobi popup views will render
  in iframes regardless of the global setting, since we only need SAMEORIGIN
  for these specific views.