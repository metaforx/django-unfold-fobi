# T10c Analysis: Enable Native Unfold Sortable Elements Inline

## Status: Already Implemented in T10b

T10c was authored before T10b was implemented. All T10c acceptance criteria
are already met by the T10b commit (`efc4e9b`).

## Verification

| Requirement | T10b State | Evidence |
|---|---|---|
| `ordering_field = "position"` set | ✓ | `admin.py:34` |
| `hide_ordering_field = True` set | ✓ | `admin.py:35` |
| Drag handles rendered | ✓ | Test `test_drag_handle_icon` asserts `drag_indicator` |
| `x-sort` directives present | ✓ | Test `test_sort_directive_present` asserts `x-sort` |
| `data-ordering-field` attribute | ✓ | Test `test_ordering_field_data_attribute` asserts attribute |
| Position persistence on save | ✓ | Test `test_position_change_persisted_on_save` (single element) |
| No add/edit/delete regression | ✓ | T10a/T10b tests cover all flows |

## Gap Identified

One test gap: no multi-element ordering persistence test. The existing
`test_position_change_persisted_on_save` only tests a single element.
After drag-and-drop, `sortRecords()` JS sets positions to 0-indexed
values (0, 1, 2, ...) — we should verify this contract with 2+ elements.

## Implementation Plan

| # | Change | Classification |
|---|--------|---------------|
| 1 | Add multi-element fixture (`form_entry_multi`) | test |
| 2 | Add `test_multi_element_position_reorder_persisted` | test |

Net new code: ~40 lines (test only). No source changes needed.

## Unfold Sortable Inline Internals (Reference)

- Template: `tabular.html` line 16 conditionally renders `x-sort.ghost` + `x-on:end="sortRecords"`
- Drag handle: `tabular_field.html` lines 2-10 renders `drag_indicator` for existing rows
- JS: `app.js:113-125` `sortRecords()` finds hidden inputs matching `[name$=-${orderingField}]` and sets values to 0..N-1
- Hidden field: `tabular_row.html` line 18 applies `hidden!` class when `hide_ordering_field=True`
- Compatible with `has_add_permission=False`, `has_delete_permission=False`, and `tab=True`