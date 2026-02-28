# Task T10g - Modal Iframe Content Refused (`127.0.0.1 refused to connect`)

Goal
- Diagnose and fix why modal opens but iframe content does not render for element edit URLs.
- Keep `django-unfold-modal` unchanged; fix must be in project configuration/integration.

Observed issue
- Modal opens.
- Iframe shows connection refusal:
  - `127.0.0.1 refused to connect`
- Iframe URL:
  - `http://127.0.0.1:8080/de/admin/fobi/forms/elements/edit/11/?_popup=1`
- Same URL can be opened manually in browser tab.

Hypothesis
- Likely iframe embedding/security/session constraint (not URL existence):
  - `X-Frame-Options` / CSP `frame-ancestors`,
  - admin popup response headers for embedded context,
  - cookie/session/auth behavior inside iframe.

Suggested Skills
- Primary: `$unfold-dev-advanced`.
- Debug fallback: `$unfold-debug-refactor`.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires T10f trigger contract work.

Phase 0 (Mandatory): Diagnostic Analysis
- Create analysis note: `reviews/feat-t10f-unfold-modal-trigger-contract__T10g-analysis.md`.
- Collect evidence for failing iframe request:
  - response status, headers, and redirect chain for `?_popup=1`,
  - browser console/network error type,
  - effective `X-Frame-Options` and CSP values,
  - auth/session behavior when request is made inside iframe.
- Determine root cause and classify fix:
  - `SETTINGS_FIX`,
  - `VIEW_HEADER_FIX`,
  - `TEMPLATE/URL_FIX`,
  - `OTHER` (with strict justification).

Scope
- Fix modal iframe content rendering for element add/edit popup URLs.
- Preserve native admin/unfold flow and existing element logic.

Implementation requirements
- Do not modify `django-unfold-modal`.
- Prefer minimal config/header changes over custom JS hacks.
- Keep popup URL contract (`?_popup=1`) compatible with admin semantics.
- Ensure solution works for localized admin URLs (`/de/admin/...`).

Non-goals
- No plugin business logic changes.
- No broad UI redesign.
- No fallback to standalone popup window if modal iframe can be fixed.

Deliverables
- `reviews/feat-t10f-unfold-modal-trigger-contract__T10g-analysis.md`.
- Code/config changes fixing iframe content load in modal.
- Tests or reproducible checks for modal iframe render success.

Acceptance Criteria
- Opening element edit/add from native change view renders form content inside modal iframe.
- No `refused to connect` for valid popup URL in same host/port context.
- Existing permissions and popup behavior remain correct.
- `poetry run pytest -q` passes for updated scope.

Tests to run
- `poetry run pytest -q`
- UI test/manual check verifying modal iframe shows element form content (not blank/error).
