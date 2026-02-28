# Task T13 - Unfold Actions, Tab-Scoped Add Controls, and Handler Modal Fixes

Goal
- Align `FormEntryProxy` admin actions/UI behavior with native Unfold patterns.
- Fix inconsistent add/delete behavior for handlers/elements in native change flow.
- Add a second handler option (email) for realistic multi-option verification.

Requested outcomes
1. Add JSON import as an Unfold changelist action
- Add an import action using Fobi import process (same underlying logic as existing Fobi import).
- Expose it via Unfold-standard changelist actions pattern:
  - `https://unfoldadmin.com/docs/actions/changelist/`
- Keep existing export behavior and ensure import/export roundtrip is practical.

2. Scope "Add Element" visibility to Elements tab only
- `Add Element` action must only appear on:
  - `/admin/unfold_fobi/formentryproxy/<id>/change/#formelemententry_set`
- It must not appear on:
  - `#general`
  - `#formhandlerentry_set`

3. Fix "Add Handler" UI/modal behavior
- Current observed issues:
  1. First click on button/dropdown appears to do nothing.
  2. Second click opens modal and may show `404` (`DB store plugin can be used only once in a form`).
  3. Refresh shows handler was actually added (backend state is changed).
  4. Delete handler appears to do nothing until refresh, then item is removed.
- Required fix:
  - UI state and backend state must be consistent without manual refresh.
  - No stale dropdown/modal interactions causing duplicate add attempts.
  - Proper user feedback after add/delete actions.

4. Add Email handler option for multi-option testing
- Enable/configure Fobi email handler plugin in available handler list.
- Keep `db_store` handler too.
- For test setup use Django console email backend so behavior is easy to verify.

Suggested Skills
- Primary: `$unfold-dev-advanced`.
- Debug fallback: `$unfold-debug-refactor`.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires T10a-T10g and T12 baseline context.

Phase 0 (Mandatory): Analysis Before Changes
- Create analysis note: `reviews/feat-t12-code-org-test-reduction__T13-analysis.md`.
- Analysis checklist:
  - Map current add/delete element/handler flow from click to server response to UI update.
  - Identify why first handler add click fails/duplicates and why stale modal actions occur.
  - Confirm tab-state source of truth for showing/hiding add controls.
  - Confirm Fobi email handler plugin availability and minimal config needed for tests.
  - Define minimal native Unfold-compatible fix path (avoid unnecessary custom JS).

Scope
- Native admin change page behavior for elements/handlers controls.
- Changelist-level import action integration via Unfold action conventions.
- Minimal settings/test setup for email handler verification.

Non-goals
- No redesign of plugin architecture.
- No broad frontend rewrite.
- No changes to unrelated admin pages.

Deliverables
- `reviews/feat-t12-code-org-test-reduction__T13-analysis.md`.
- Unfold changelist JSON import action wired to Fobi import logic.
- Tab-scoped add controls (`Add Element` only on elements tab).
- Fixed handler add/delete UX consistency (no refresh-required state sync).
- Email handler available and testable with console backend.
- Tests for all above behaviors.

Acceptance Criteria
- Import JSON is available via Unfold changelist action and uses Fobi import process.
- `Add Element` is visible only in `#formelemententry_set` tab.
- Handler add/delete works reliably in UI without requiring page refresh.
- Duplicate click race/stale modal behavior is eliminated.
- Email handler appears as option and works in simple console-backend test flow.
- `poetry run pytest -q` passes.

Tests to run
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent) for tab visibility and modal/add/delete behavior.
