# T10d Analysis: Sort Handle Contract on Native Change Inline

## Status: Markup Present but Handles Invisible — Field Order Bug

All 7 contract markers are present in the rendered HTML, but the drag
handles are **not visible** because they render inside a hidden `<td>`.

## Root Cause

Unfold's `tabular_field.html` renders the drag handle inside the **first
field's `<td>`** (the `forloop.counter == 1` check at line 2). Meanwhile,
`tabular_row.html` line 18 applies `hidden!` to any `<td>` whose field
name matches `ordering_field` when `hide_ordering_field = True`.

With our original field order:
```python
fields = ("position", "plugin_uid", "plugin_data_preview", "element_actions")
```
`position` is the first field → drag handle renders in the `position` cell →
that cell gets `hidden!` → handle is in the DOM but invisible.

## Fix

Move `position` out of the first slot:
```python
fields = ("plugin_uid", "position", "plugin_data_preview", "element_actions")
```
Now the drag handle renders in the `plugin_uid` cell (always visible),
while `position` remains hidden in its own separate `<td>`.

Classification: `NATIVE` — pure field ordering fix, no custom code.

## Additional Gap

Existing tests only checked HTML presence, not visibility. Tightened
`TestSortableInline` with precise contract assertions in the same commit.

## Verification

After fix:
- `PASS`: drag handle is inside a VISIBLE `<td>` (field-plugin_uid)
- `PASS`: position `<td>` is hidden
- All 7 contract markers still present