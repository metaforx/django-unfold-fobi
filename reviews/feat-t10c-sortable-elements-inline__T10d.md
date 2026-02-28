# T10d Review: Sort Handle Contract on Native Change Inline

## Scope
- Fix invisible drag handles on the native change page.
- Enforce the full Unfold drag handle HTML contract in tests.

## Root Cause
Unfold's tabular template renders the drag handle in the **first field's
`<td>`**. With `position` as the first field and `hide_ordering_field=True`,
the entire `<td>` (including the handle) received `hidden!`.

## Fix
Reorder `fields` in `FormElementEntryInline` so `plugin_uid` is first:
```python
fields = ("plugin_uid", "position", "plugin_data_preview", "element_actions")
```
Classification: `NATIVE` — pure field ordering, no custom code.

## Changes

| File | Change | Classification |
|------|--------|---------------|
| `src/unfold_fobi/admin.py` | Move `position` after `plugin_uid` in `fields` | NATIVE |
| `tests/test_edit_view.py` | Tightened `TestSortableInline` — contiguous fragment assertion, event binding, ghost directive | test |
| `reviews/...T10d-analysis.md` | Phase 0 analysis with root cause | docs |
| `reviews/...T10d.md` | This review note | docs |

## Codex CLI Review
- **Round 1**: P2 — CSS class assertions too broad
- **Round 2**: P2 — still two independent assertions
- **Round 3**: No issues found

## Test Results
- 117 tests pass
- `poetry run pytest -q` — all green

## Status: DONE
