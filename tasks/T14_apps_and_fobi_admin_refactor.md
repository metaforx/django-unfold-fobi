# Task T14 - Source Structure Audit and Refactor for `apps.py` and `fobi_admin.py`

Goal
- Re-open the source audit with maintainability as the primary decision driver.
- Analyze which files in `src/unfold_fobi` can be removed, unified, or split by responsibility.
- Perform an explicit deep review of `apps.py` and `fobi_admin.py`, which currently carry too many concerns.
- Keep behavior stable while moving toward clearer Django-native module boundaries.

Requested direction
- Audit `src/unfold_fobi` before changing structure.
- Identify files/modules that are:
  - `KEEP_AS_IS`,
  - `UNIFY`,
  - `SPLIT`,
  - `REMOVE`.
- Re-check whether all logic in `apps.py` and `fobi_admin.py` is still needed.
- If logic is required, separate it into smaller modules/folders using Django best-practice structure.
- Keep documentation short:
  - add short docstrings only where purpose is not obvious,
  - avoid long narrative comments.

Suggested Skills
- Primary: `$unfold-dev-advanced`.
- Review: `$unfold-codex-reviewer`.
- Debug fallback: `$unfold-debug-refactor`.

Model / Agent Routing
- Use a high-level model for:
  - Phase 0 audit and refactor plan,
  - all `apps.py` and `fobi_admin.py` design decisions,
  - any extraction/removal that changes import flow, monkey patches, admin registration, or signals.
- Route only bounded mechanical work to smaller/faster agents, for example:
  - file inventory,
  - dead-reference search,
  - focused test runs,
  - formatting/lint-only follow-up.
- Do not delegate the main architectural decision-making for this task to a lightweight model.

Dependencies
- Requires T13 baseline behavior to be stable.
- Reuse outcomes from T11/T12 analysis, but do not treat earlier `KEEP` decisions as final if the code is still hard to maintain.

Phase 0 (Mandatory): Removal / Unification / Split Audit
- Create analysis note: `reviews/development-integrated__T14-analysis.md`.
- For each file in `src/unfold_fobi`, classify it as:
  - `KEEP_AS_IS`,
  - `UNIFY`,
  - `SPLIT`,
  - `REMOVE`.
- For each `UNIFY`, `SPLIT`, or `REMOVE` decision, document:
  - why the current boundary is weak,
  - what the target boundary should be,
  - what imports/contracts must remain stable.
- Include special focus on:
  - `apps.py`,
  - `fobi_admin.py`,
  - `admin.py`,
  - `views.py`,
  - `services.py`,
  - `forms.py`,
  - any patch/helper modules that overlap in responsibility.

Phase 1 (Mandatory): Deep Review of `apps.py` and `fobi_admin.py`
- In `apps.py`, explicitly classify each responsibility:
  - widget patching,
  - popup response patching,
  - owner-filter patching,
  - signal registration,
  - startup imports,
  - helper functions.
- Decide which parts should stay in `apps.py` and which should move to dedicated modules such as:
  - `patches/`,
  - `signals.py`,
  - `admin/` support modules,
  - other clearly named helpers.
- Keep `apps.py` thin after refactor:
  - app config,
  - minimal startup orchestration,
  - idempotent setup only.
- In `fobi_admin.py`, explicitly classify:
  - unregister/reregister flow,
  - proxy-only permission mixins,
  - inline definitions,
  - redirect behavior,
  - saved-entry permission behavior,
  - plain admin re-registrations.
- Decide whether `fobi_admin.py` should become:
  - a thinner entry module,
  - or a package-backed admin composition with smaller modules imported from one stable entrypoint.

Phase 2: Structural Refactor
- Remove files/modules proven obsolete in Phase 0.
- Unify files/modules that duplicate responsibilities.
- Split `apps.py` and `fobi_admin.py` by concern where that improves readability without changing behavior.
- Prefer small, explicit modules over one large compatibility bucket.
- Preserve Django admin autodiscovery and existing registration/import behavior.
- Keep monkey patches and signals idempotent and easy to trace.
- Add short docstrings to extracted modules/classes/functions where intent is not immediately clear.

Scope
- Python modules and closely related tests/docs in this repo.
- Refactor for maintainability, not feature expansion.

Non-goals
- No redesign of Fobi plugin architecture.
- No broad UI rewrite.
- No URL contract changes unless strictly required and covered by tests.
- No speculative abstraction with unclear payoff.

Deliverables
- `reviews/development-integrated__T14-analysis.md` with file-by-file keep/unify/split/remove decisions.
- Refactored source structure for approved extractions/removals.
- `apps.py` reduced to a thin app-config/startup entrypoint if behavior allows.
- `fobi_admin.py` simplified or split into smaller admin modules with one stable import path.
- Short documentation/docstrings for non-obvious extracted responsibilities.
- Brief before/after summary covering:
  - files removed,
  - files unified,
  - files split,
  - line-count reduction for `apps.py` and `fobi_admin.py`.

Acceptance Criteria
- Every file in `src/unfold_fobi` has an explicit structure decision in the analysis note.
- `apps.py` and `fobi_admin.py` each have clear responsibility boundaries after the refactor.
- Required logic is kept, but unnecessary coupling and oversized modules are reduced.
- Extracted modules use short, targeted docstrings where needed.
- Admin registration, popup behavior, permissions, widget patching, and signal behavior continue to work.
- `poetry run pytest -q` passes.
- Playwright coverage for impacted admin flows still passes.

Tests to run
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent for impacted admin/popup flows)
