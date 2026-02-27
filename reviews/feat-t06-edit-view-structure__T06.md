# Review: feat/t06-edit-view-structure — T06 Edit-view structure, tabs, breadcrumbs

## Round 1

P2: ARIA `aria-labelledby` on tabpanels referenced their own panel ID instead
of the tab anchor ID. Fixed by adding stable `id` attributes to tab anchors
and referencing them from each panel's `aria-labelledby`.

## Round 2

No issues found. Tab cleanup, breadcrumb contract, ARIA wiring, and legacy JS
removal are consistent with tests.

**Status: DONE**
