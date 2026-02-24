# Task T07 - Edit View Actions and Grid Styling

Goal
- Align action controls and content layout in the edit builder with Unfold patterns.

Dependencies
- Requires T03-T04 passing before and after changes.

Scope
- Ensure all builder actions use Unfold button/select/dropdown styling consistently.
- Keep "Add form element" action placement aligned with nav row.
- Verify ordering auto-save behavior remains intact (no "Save ordering" reintroduction).
- Replace or restyle legacy striped/table sections to Unfold-style grid/card presentation where required.
- Extend T03/T04 suites with assertions for action/control/grid behavior.

Non-goals
- No new builder features.
- No API/REST changes.

Deliverables
- Finalized action/button styling consistency.
- Updated template structure for table/grid sections in scope.
- Regression tests covering the finalized UX.

Acceptance Criteria
- Action controls are visually and behaviorally consistent with Unfold.
- Elements/handlers sections match expected Unfold presentation.
- T03-T04 suites stay green with extended checks.

Tests to run
- `poetry run pytest -q`
- `npx playwright test` (or pytest-playwright equivalent)
