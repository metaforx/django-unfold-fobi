# T10c Review: Enable Native Unfold Sortable Elements Inline

## Scope
- Confirm T10b already implemented all sortable inline requirements.
- Add multi-element sort persistence tests (gap from T10b).

## Status: Already Implemented in T10b

All T10c acceptance criteria were met by T10b commit `efc4e9b`:
- `ordering_field = "position"` and `hide_ordering_field = True` configured
- Drag handles, `x-sort`, `data-ordering-field` rendered by Unfold template
- Single-element position persistence tested

## Changes (T10c delta)

| File | Change | Classification |
|------|--------|---------------|
| `tests/test_edit_view.py` | 2 new tests in `TestMultiElementSortPersistence` | test |
| `.agents/reviews/...T10c-analysis.md` | Phase 0 analysis | docs |
| `.agents/reviews/...T10c.md` | This review note | docs |

No source changes needed.

## Codex CLI Review
- **Round 1**: 2 findings (P2: formset id pairing, P3: render order assertion)
- **Round 2** (after fixes): No issues found.

## Test Results
- 115 tests pass (113 existing + 2 new)
- `poetry run pytest -q` — all green

## Status: DONE