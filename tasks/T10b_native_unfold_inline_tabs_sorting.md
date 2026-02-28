# Task T10b - Native Change Flow Hardening (Edit 404, Sortable Inlines, Handler Add)

Goal
- Fix current native change-flow blockers while keeping `FormEntryProxy` add/change native.
- Reuse Unfold capabilities first; introduce patching only when absolutely necessary.

Current blockers
- Form element add works, but element edit returns `404`:
  - `http://127.0.0.1:8080/de/admin/fobi/forms/elements/edit/5/`
- Element sorting is plain integer input; target is native Unfold sortable behavior:
  - `https://unfoldadmin.com/docs/inlines/sortable/`
- Form handlers cannot be added from native flow.
- Evaluate using native inline tabs for `Form elements` and `Form handlers`:
  - `https://unfoldadmin.com/docs/tabs/inline/`

Suggested Skills
- Primary: `$unfold-dev-advanced`.
- Debug fallback: `$unfold-debug-refactor`.
- Review: `$unfold-codex-reviewer`.

Dependencies
- Requires `T10` and `T10a`.
- Reuse T03/T04/T09 regressions as baseline.

Phase 0 (Mandatory): Analysis Before Changes
- Create analysis note: `reviews/feat-t10a-native-change-elements-handlers__T10b-analysis.md`.
- Analysis checklist:
  - Root-cause the element edit `404` and document exact cause (URL wiring, permissions, owner filtering, or redirect contract).
  - Compare two options for sorting:
    - retain manual position fields,
    - switch to Unfold sortable inline.
  - Evaluate feasibility of native inline tabs for both inlines in current admin architecture.
  - Document handler-add gap and minimal native-compatible integration path.
  - For each issue, classify solution as:
    - `NATIVE` (pure Django/Unfold),
    - `MINIMAL_PATCH`,
    - `UNAVOIDABLE_PATCH` (with strict justification).

Scope
- Keep primary edit flow on native:
  - `/admin/unfold_fobi/formentryproxy/<id>/change/`
- Resolve the following:
  - Element edit must work from native change context (no `404`).
  - Elements must support intuitive sorting using Unfold sortable inline if technically compatible.
  - Handlers add flow must be available from native change context.
  - Inline tabs for elements/handlers should be used if feasible without added complexity.

Implementation requirements
- Element edit `404` fix:
  - Ensure edit links target valid endpoints under current routing and permissions.
  - Preserve language-prefixed admin URL behavior.
- Sorting:
  - Prefer Unfold sortable inline integration over manual integer editing.
  - Keep ordering persistence/validation deterministic.
- Inline tabs:
  - If feasible, implement native inline tabs for `Form elements` and `Form handlers`.
  - If not feasible, document exact blocker and fallback with minimal custom UI.
- Handler add:
  - Restore add functionality with plugin availability/single-use constraints respected.
  - Reuse existing Fobi add handler endpoint/logic where possible.

Non-goals
- No return to full custom standalone builder view.
- No broad template rewrites.
- No plugin architecture redesign.

Deliverables
- `reviews/feat-t10a-native-change-elements-handlers__T10b-analysis.md`.
- Code changes enabling native-flow element edit + sort and handler add.
- Tests covering:
  - element edit endpoint from native page,
  - sorting persistence,
  - handler add flow,
  - inline tabs presence (or documented fallback contract).

Acceptance Criteria
- Element edit from native change page no longer returns `404`.
- Elements can be reordered with native Unfold sortable approach, or a documented justified fallback.
- Handler add is functional from native change flow.
- Inline tabs for elements/handlers are used when feasible; otherwise fallback is explicitly documented.
- Native change handling remains primary and complexity does not increase without justification.
- `poetry run pytest -q` passes for updated scope.

Tests to run
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent) for native change interactions.
