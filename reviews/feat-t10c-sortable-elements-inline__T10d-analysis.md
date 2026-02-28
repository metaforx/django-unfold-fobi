# T10d Analysis: Sort Handle Contract on Native Change Inline

## Status: Already Rendered — Tests Need Tightening

All 7 contract markers are present in the rendered change page HTML:

| Marker | Present | Source |
|--------|---------|--------|
| `material-symbols-outlined` | ✓ | Unfold `tabular_field.html` |
| `cursor-move` | ✓ | Unfold `tabular_field.html` |
| `x-sort:handle` | ✓ | Unfold `tabular_field.html` |
| `drag_indicator` | ✓ | Unfold `tabular_field.html` |
| `data-ordering-field="position"` | ✓ | Unfold `tabular.html` |
| `x-sort.ghost` | ✓ | Unfold `tabular.html` |
| `x-on:end="sortRecords"` | ✓ | Unfold `tabular.html` |

Verified via live Django test client against the change page.

## Root Cause

T10d was authored before T10b set `ordering_field = "position"` and
`hide_ordering_field = True` on `FormElementEntryInline`. Once those
attributes are set, Unfold's tabular inline template automatically
renders the full drag handle markup. No custom code needed.

## Gap

Existing `TestSortableInline` tests use loose assertions:
- `"x-sort" in html` matches `x-sort.ghost` but doesn't specifically verify `x-sort:handle`
- No test for `material-symbols-outlined cursor-move` CSS classes
- No test for `x-on:end="sortRecords"` event binding

## Implementation Plan

| # | Change | Classification |
|---|--------|---------------|
| 1 | Tighten `TestSortableInline` with precise contract assertions | test |

Net new code: ~15 lines (test only). No source changes needed.
Classification: `NATIVE` — all functionality provided by Unfold template.
