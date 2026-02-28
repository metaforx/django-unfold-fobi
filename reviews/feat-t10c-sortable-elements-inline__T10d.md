# T10d Review: Sort Handle Contract on Native Change Inline

## Scope
- Verify drag handle HTML contract is met on native change page.
- Tighten test assertions to enforce the full Unfold handle markup.

## Status: Already Rendered by T10b — Tests Tightened

All contract markers were already present in rendered HTML from T10b.
T10d adds precise regression tests using a contiguous fragment assertion.

## Changes

| File | Change | Classification |
|------|--------|---------------|
| `tests/test_edit_view.py` | Tightened `TestSortableInline` — added `test_drag_handle_markup_contract`, `test_sort_ghost_directive`, `test_sort_end_event_binding`; replaced loose `test_sort_directive_present` | test |
| `reviews/...T10d-analysis.md` | Phase 0 analysis | docs |
| `reviews/...T10d.md` | This review note | docs |

No source changes needed.

## Codex CLI Review
- **Round 1**: P2 — CSS class assertions too broad (separate global substrings)
- **Round 2**: P2 — still two independent assertions instead of one fragment
- **Round 3**: No issues found (single contiguous fragment assertion)

## Test Results
- 117 tests pass
- `poetry run pytest -q` — all green

## Status: DONE
