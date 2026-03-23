# Task T10d - Sort Handle Contract on Native Change Inline

Goal
- Ensure native `Form elements` inline exposes real Unfold drag handles.
- Validate and enforce the HTML contract for sortable handles on the change page.

Problem
- On:
  - `http://127.0.0.1:8080/de/admin/unfold_fobi/formentryproxy/2/change/#formelemententry_set`
- No usable drag handler is visible.
- If `material-symbols-outlined cursor-move` is missing in rendered HTML, sortable drag-and-drop is not wired correctly.

Expected Unfold contract
- Sort handle markup should include:
  - `material-symbols-outlined cursor-move`
  - `x-sort:handle`
  - `drag_indicator` icon text
- Implementation should follow Unfold sortable inline behavior:
  - `https://unfoldadmin.com/docs/inlines/sortable/`

Suggested Skills
- Primary: `$unfold-dev-advanced`.
- Debug fallback: `$unfold-debug-refactor`.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires `T10c`.

Phase 0 (Mandatory): Verification and Root-Cause Analysis
- Create analysis note: `.agents/reviews/feat-t10c-sortable-elements-inline__T10d-analysis.md`.
- Confirm on rendered change HTML that:
  - `material-symbols-outlined cursor-move` exists for element inline rows.
  - Inline container includes sortable directives/attributes expected by Unfold.
- If missing, identify why (inline config, template path, field configuration, or CSS/JS not loaded).

Scope
- Fix sortable handle rendering for `FormElementEntry` inline in native change flow.
- Keep fix minimal and configuration-first:
  - prefer Unfold inline options/settings over custom JS or template patches.

Implementation requirements
- First try pure Unfold configuration:
  - proper inline class type/options,
  - ordering field configuration,
  - sortable-enabled inline rendering path.
- Only if config-only fails:
  - add minimal patch with explicit documented reason.
- Preserve existing add/edit/delete element behavior.

Non-goals
- No standalone custom builder fallback.
- No broad template rewrites.
- No unrelated UI redesign.

Deliverables
- `.agents/reviews/feat-t10c-sortable-elements-inline__T10d-analysis.md`.
- Code update that renders Unfold drag handles in native change inline.
- Tests that assert the handle class contract in response HTML.

Acceptance Criteria
- Change page HTML contains:
  - `material-symbols-outlined cursor-move`
  - `x-sort:handle`
  - `drag_indicator`
- Elements are drag-sortable with visible handle and persist order on save.
- Fix uses Unfold-native configuration unless a justified minimal patch is documented.
- `poetry run pytest -q` passes.

Tests to run
- `poetry run pytest -q`
- UI test (Playwright or equivalent) to verify visible drag handle + reorder persistence.