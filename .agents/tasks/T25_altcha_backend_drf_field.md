# Task T25 - ALTCHA backend integration with DRF field support

Goal
- Add ALTCHA protection to backend form submission flows.
- Provide ALTCHA to API clients as a DRF-consumable field contract.
- Keep integration optional and safe for projects not using ALTCHA.
- Support Nuxt SSR public-form flows where ALTCHA is rendered on the Nuxt side
  and validated in backend DRF before Fobi processing.

Problem statement
- Current DRF submission flow (`PUT /api/fobi-form-entry/<slug>/`) accepts payloads
  without anti-bot proof.
- Frontend clients already consume `GET /api/fobi-form-fields/<slug>/`; ALTCHA
  must be exposed through this API so clients can render and submit the widget
  payload consistently.
- In Nuxt SSR deployments, ALTCHA must stay decoupled from Fobi HTML rendering.

Check: can/should we use `django-altcha`?
- Can use: **Yes**.
  - `django-altcha` is actively maintained and current (`0.10.0`, released
    March 10, 2026) and provides challenge generation + replay-protection
    primitives for Django projects.
- Should use as core DRF implementation: **No (not directly)**.
  - It is primarily a Django forms/widget integration (`AltchaField`,
    `AltchaChallengeView`), not a DRF serializer-field integration.
  - For this package’s API-first flow, implement a package-owned DRF field and
    backend validator, optionally with adapter hooks for django-altcha.

Suggested Skills
- Primary: `$unfold-dev-advanced`.
- Review: `$unfold-codex-reviewer`.

Dependencies
- T18/T23 API form-fields endpoint conventions.
- Existing patch mechanism in `src/unfold_fobi/patches/*` (used for DRF update
  interception).

Scope
- Add optional ALTCHA integration module:
  - `src/unfold_fobi/contrib/altcha/`
- Add API exposure for ALTCHA field metadata in
  `src/unfold_fobi/api/views.py`.
- Add DRF submission validation hook for ALTCHA in the submission path.
- Add settings contract and docs.
- Add tests for enabled/disabled and pass/fail verification cases.
- Document Nuxt SSR integration path (widget render, challenge fetch, payload
  submit).

Non-goals
- No mandatory dependency on ALTCHA for all users.
- No frontend framework implementation details.
- No Sentinel spam-filter integration in initial scope (keep extension points).
- No requirement to add ALTCHA as a persisted Fobi form element for API-first
  Nuxt flows.

Implementation requirements
1. Optional integration boundary
- ALTCHA integration must be opt-in.
- Base `unfold_fobi` must still load when ALTCHA deps/settings are absent.
- Use lazy imports to avoid startup errors when contrib app is disabled.

2. DRF field contract for clients
- Extend `GET /api/fobi-form-fields/<slug>/` with a synthetic field entry when
  ALTCHA is enabled, e.g.:
  - `name`: `"altcha"`
  - `type`: `"AltchaField"`
  - `widget`: `"AltchaWidget"`
  - `required`: `true`
  - include challenge endpoint metadata (URL, field name, optional options).
- When ALTCHA is disabled, response remains unchanged.
- This field contract is explicitly intended for Nuxt-side widget rendering and
  must not depend on Fobi server-side HTML form rendering.

3. Challenge endpoint
- Provide a backend endpoint that returns fresh ALTCHA challenge JSON.
- Keep endpoint package-owned and reusable by external frontends.
- Ensure challenge generation parameters are configurable via settings.

4. Submission verification via DRF field
- Introduce a package DRF validation component (serializer field or equivalent
  request validator) for ALTCHA payload.
- Wire validation into form submission flow (`/api/fobi-form-entry/<slug>/`)
  before data persistence.
- Remove/consume ALTCHA payload before passing form data to Fobi handlers to
  avoid unknown-field side effects.
- Return deterministic API errors (`400`) when ALTCHA payload is missing/invalid.
- Validation order is strict:
  1. parse ALTCHA payload from request body,
  2. verify challenge/signature/expiry/replay,
  3. only then hand off sanitized payload to Fobi submission processing.

5. Replay protection and cache behavior
- Enforce one-time payload usage (replay protection).
- Require/document shared cache backend for multi-worker deployments.
- Provide cache alias setting for ALTCHA verification state.

6. Provider strategy
- Default provider: package-owned DRF-oriented verification using official
  ALTCHA Python primitives (`altcha` package).
- Optional adapter path: allow integration points for `django-altcha` challenge
  and verification helpers, but do not make it the only path.
- Proposed Fobi plugin (`IntegrationFormFieldPlugin` + `django_altcha.AltchaField`)
  is considered optional and secondary:
  - useful for classic Django-rendered Fobi forms,
  - not the primary integration for Nuxt SSR over DRF,
  - must not be required for API submissions to be protected.

7. Settings contract
- Add explicit settings with safe defaults, e.g.:
  - enable/disable flag,
  - HMAC secret,
  - challenge endpoint path,
  - payload field name (default `"altcha"`),
  - cache alias for replay protection.

8. Security and error handling
- Reject expired challenges.
- Reject malformed/non-base64 payloads.
- Log verification failures at appropriate level without leaking secrets.

Deliverables
- Optional ALTCHA contrib module for backend + DRF.
- Synthetic ALTCHA field support in form-fields API.
- Submission-time ALTCHA validation and replay protection.
- Settings and README documentation.
- Tests covering enabled/disabled and verification outcomes.
- Integration notes for Nuxt:
  - widget rendering on frontend,
  - challenge endpoint consumption,
  - ALTCHA payload included in DRF submit body.

Acceptance Criteria
- With ALTCHA disabled:
  - existing API behavior is unchanged.
- With ALTCHA enabled:
  - `GET /api/fobi-form-fields/<slug>/` includes ALTCHA field metadata.
  - challenge endpoint returns valid challenge payloads.
  - valid ALTCHA payload allows submission.
  - missing/invalid/replayed payload is rejected with `400`.
  - ALTCHA validation occurs before Fobi submission handling is invoked.
- Base package remains import-safe without ALTCHA contrib activation.
- `poetry run pytest -q` passes.

Tests to run
- `poetry run pytest -q`
- Add targeted tests for:
  - form-fields response with ALTCHA disabled/enabled,
  - challenge endpoint response shape and freshness,
  - Nuxt-style API submission body containing ALTCHA payload,
  - submission success with valid payload,
  - submission failure for missing/invalid/expired/replayed payload,
  - disabled-mode import/app-loading safety.
