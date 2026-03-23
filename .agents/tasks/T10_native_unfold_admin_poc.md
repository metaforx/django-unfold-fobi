# Task T10 - Native Unfold Admin Integration POC (Complexity Reduction)

Goal
- Validate a lower-complexity architecture where form add/edit primarily uses native Django admin + Unfold (`FormEntryProxy` add/change).
- Reduce custom builder/view/template/patch surface, not increase it.
- Keep existing Fobi plugin capabilities working (elements/handlers configuration), while minimizing custom glue code.

Suggested Skills
- Primary: `$unfold-dev-advanced` (admin/view/template integration with compatibility constraints).
- Debug fallback: `$unfold-debug-refactor` (routing, permissions, and plugin edit flow regressions).
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires T03, T04, and T09 baseline behavior/tests as guard rails.

Context from code back-check
- Current `FormEntryProxy` admin rewires change flow to custom `edit/<id>/` view.
- Custom edit builder has bespoke tabs (`Elements/Handlers/Properties`) and ordering JS.
- Runtime monkey patching in `apps.py` is extensive (admin views, class-based views, plugin form init paths).
- Legacy Fobi route names are still used as compatibility endpoints and callback targets.

Scope
- Build a POC branch proving whether native admin change view can replace the custom builder route safely.
- Integrate builder concerns into native Unfold admin in a minimal way:
  - Core form properties: native change form.
  - Elements: integrated as a native-page section/tab/panel that links into Fobi element add/edit endpoints.
  - Handlers: inline-based where practical, with no custom table renderer unless strictly required.
- Preserve functional compatibility for Fobi URLs/callbacks and existing permission semantics.

Non-goals
- No rewrite of Fobi plugin architecture.
- No schema changes.
- No broad upstream template forks.
- No frontend redesign unrelated to complexity reduction.

Phase 0 (Mandatory Gate): Thorough Analysis First
- Do not implement POC changes before this analysis is documented.
- Create an analysis note: `.agents/reviews/feat-t10-native-unfold-poc__analysis.md`.
- Analysis checklist:
  - Enumerate every current customization involved in add/edit flows:
    - URL rewrites/redirects.
    - Custom edit views and template overrides.
    - JS behavior (tabs, ordering autosave).
    - `apps.py` monkey patches (with exact purpose).
  - Classify each customization as one of:
    - `REMOVE` (no longer needed with native admin),
    - `KEEP` (still required for plugin flow),
    - `REPLACE` (native Django/Unfold alternative).
  - Define at least two architecture options (minimal hybrid vs. deeper native alignment) with risks/trade-offs.
  - Recommend one option with explicit rationale focused on complexity reduction.
  - Provide a rollback strategy if the POC fails.

Phase 1: POC Implementation (After Gate Approval)
- Rewire `FormEntryProxy` edit flow to native change view (`/<id>/change/`) as primary path.
- Keep `add/` as native admin add path.
- Integrate Elements into native change page in the least invasive way:
  - Add clear entry points for add/edit/delete element plugin actions.
  - Reuse existing Fobi endpoints for plugin configuration forms.
  - Prefer popup/related-widget style only if it reduces custom code and keeps UX coherent.
- Move Handlers to native inline strategy where feasible.
- Keep compatibility route behavior for `fobi.edit_form_entry` and related callbacks.
- Remove only the custom code proven redundant by the new flow.

Phase 2: Verification and Complexity Audit
- Add/update tests for routing, page structure, element/handler actions, and permissions.
- Produce a complexity delta in the analysis note:
  - Files removed/simplified.
  - Lines reduced in custom views/templates/patches.
  - Monkey patches removed vs. remaining (with justification for remaining).
- Confirm no regressions in critical builder behavior.

Deliverables
- `.agents/reviews/feat-t10-native-unfold-poc__analysis.md` (mandatory analysis + decision record).
- POC code on branch `feat/t10-native-unfold-poc`.
- Updated tests covering new native-flow behavior.
- Short summary of removed vs. retained customization points.

Acceptance Criteria
- Form add/edit primary flows use native `FormEntryProxy` admin add/change views.
- Elements and handlers remain operable from native edit context.
- URL compatibility (`fobi.edit_form_entry` and dependent callbacks) is preserved.
- Net custom complexity is reduced (documented with before/after evidence).
- Test suite passes for scoped behavior.

Tests to run
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent for affected UI flows)

Definition of Done
- Analysis gate completed before implementation.
- POC demonstrates native-view integration without increasing patch surface.
- Any remaining monkey patching has explicit, documented necessity.