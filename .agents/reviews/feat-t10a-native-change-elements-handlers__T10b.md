# T10b Review: Native Change Flow Hardening

## Scope
- Fix element edit/delete 404 for non-owner admin users
- Unfold-native sortable inline for element ordering (drag-and-drop)
- Unfold-native inline tabs for elements and handlers
- Handler add regression safety (already working from T10a)

## Changes

| File | Change | Classification |
|------|--------|---------------|
| `src/unfold_fobi/admin.py` | Added `tab=True`, `ordering_field`, `hide_ordering_field` | NATIVE |
| `src/unfold_fobi/apps.py` | Added `_patch_fobi_owner_filtering()` — queryset + permission bypass for staff | UNAVOIDABLE_PATCH |
| `tests/test_edit_view.py` | 9 new tests in 3 classes (non-owner edit, tabs, sortable) | test |
| `.agents/reviews/...T10b-analysis.md` | Phase 0 analysis | docs |

## Codex CLI Review
- **Result**: No issues found.
- **Session**: 019ca3ca-9556-78f2-891d-fc9d6a1b12ff

## Test Results
- 113 tests pass (104 existing + 9 new)
- `poetry run pytest -q` — all green

## Status: DONE