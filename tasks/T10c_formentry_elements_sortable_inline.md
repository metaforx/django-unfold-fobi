# Task T10c - Enable Native Unfold Sortable Elements Inline

Goal
- Make `Form elements` sortable on native change view using Unfold's sortable inline pattern.
- Ensure drag handles are visible and ordering persists correctly.

Problem statement
- On native change page:
  - `http://127.0.0.1:8080/de/admin/unfold_fobi/formentryproxy/2/change/#formelemententry_set`
- Elements are not draggable:
  - no drag handles,
  - no native sort UX.

Reference
- Unfold sortable inline guidance:
  - `https://unfoldadmin.com/docs/inlines/sortable/`

Suggested Skills
- Primary: `$unfold-dev-advanced`.
- Debug fallback: `$unfold-debug-refactor`.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires `T10a` and `T10b`.
- Reuse T03/T04 baseline regressions where applicable.

Phase 0 (Mandatory): Analysis Before Code
- Create analysis note: `reviews/feat-t10b-native-inline-tabs-sorting__T10c-analysis.md`.
- Confirm:
  - Which inline class currently renders `FormElementEntry`.
  - Which field should be used for sortable ordering (`position`).
  - Whether additional inline options are required by installed Unfold version.
  - Any conflicts with existing Fobi ordering/save logic.

Scope
- Configure `FormElementEntry` inline to use native Unfold sortable behavior.
- Keep change form flow native (no standalone custom builder reintroduction).
- Preserve existing element add/edit/delete behavior.

Implementation requirements
- Use Unfold-supported inline sortable configuration on the `Form elements` inline.
- Sorting must map to `position` and persist to DB after save.
- Drag handle UI must be visible in the inline rows.
- Remove or avoid redundant manual position UX where it conflicts with native sorting.

Non-goals
- No unrelated UI redesign.
- No plugin architecture changes.
- No broad template rewrites.

Deliverables
- Code changes enabling native drag-sort in `Form elements` inline.
- Analysis note with implementation rationale.
- Regression tests for ordering persistence and UI contract.

Acceptance Criteria
- `Form elements` inline shows drag handles on native change view.
- Drag-and-drop reordering updates `position` values correctly after save.
- No regression in element add/edit/delete flows.
- `poetry run pytest -q` passes for updated scope.

Tests to run
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent) for inline drag-sort interaction.
