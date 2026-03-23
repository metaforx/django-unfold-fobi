# Task T10f - Unfold Modal Trigger Contract for Element Popup

Goal
- Ensure element add/edit popup opens in the exact Django admin popup way required to trigger `django-unfold-modal`.
- Do this without changing anything in the `django-unfold-modal` package.

Context
- `django-unfold-modal==0.1.0` was added in test environment for verification.
- Current behavior opens a browser popup window, but not via standard Django admin popup contract.
- Result: unfold modal integration is not triggered correctly.

Primary requirement
- Popup opening must match native Django admin related-widget behavior closely enough that Unfold modal interception works out of the box.

Suggested Skills
- Primary: `$unfold-dev-advanced`.
- Debug fallback: `$unfold-debug-refactor`.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires T10e feasibility context.

Phase 0 (Mandatory): Contract Analysis
- Create analysis note: `.agents/reviews/feat-t10e-popup-modal-compat__T10f-analysis.md`.
- Analyze and document:
  - Which HTML attributes/classes/query params/events are present in Django admin related popup links.
  - Which of those are required for `django-unfold-modal` trigger detection.
  - What is currently missing in element add/edit links.
  - Minimal changes needed in `unfold_fobi` only.

Scope
- Focus on popup trigger mechanism only (open behavior/contract).
- Do not redesign plugin forms.
- Do not modify `django-unfold-modal`.

Implementation requirements
- Update element add/edit link generation so it follows standard admin popup semantics.
- Ensure links are rendered in a way that Unfold modal JS can detect/intercept.
- Keep URLs, permissions, and save logic intact.
- Keep native `FormEntryProxy` change flow as primary.

Non-goals
- No changes to `django-unfold-modal` source.
- No broad template rewrites.
- No plugin logic changes.

Deliverables
- `.agents/reviews/feat-t10e-popup-modal-compat__T10f-analysis.md`.
- Code changes in `unfold_fobi` to align popup trigger behavior.
- Tests verifying trigger contract and modal/open behavior expectations.

Acceptance Criteria
- Element add/edit popup links use Django admin-compatible popup trigger semantics.
- `django-unfold-modal` is triggered by these links without package modifications.
- Existing element add/edit backend logic remains unchanged.
- `poetry run pytest -q` passes for updated scope.

Tests to run
- `poetry run pytest -q`
- UI test (Playwright or equivalent) asserting modal-triggered open behavior.