# T10b Analysis: Native Change Flow Hardening

## 1. Element Edit 404

### Root Cause

`EditFormElementEntryView._get_queryset()` in `fobi/views/class_based.py:918-922` filters by `form_entry__user__pk=request.user.pk`. When an admin user who is NOT the form's original creator tries to edit an element, the queryset returns empty and `get_object_or_404` raises 404.

Same owner filter exists in:
- `EditFormHandlerEntryView._get_queryset()` (line 1343-1350)
- `AbstractDeletePluginEntryView._get_queryset()` (line 164-168)

Note: the **add** views (`AddFormElementEntryView`, `AddFormHandlerEntryView`) do NOT filter by user — they use a direct PK lookup. This is why adding works but editing/deleting fails.

### Fix Classification: `UNAVOIDABLE_PATCH`

Fobi hardcodes owner filtering in `_get_queryset` with no hook/setting to disable it. A monkey-patch in `apps.py` is needed to allow staff users to bypass the filter.

### Minimal Patch

Override `_get_queryset` on all three view classes: for `is_staff` users, remove the `form_entry__user__pk` filter. Keep original behavior for non-staff users.

## 2. Sortable Inline

### Unfold Native Sortable

Unfold provides built-in sortable inline support via two attributes on `BaseInlineMixin`:
- `ordering_field = "position"` — activates drag-and-drop (data-ordering-field on table, x-sort Alpine directives)
- `hide_ordering_field = True` — hides numeric input, shows drag handle icon only

JS (`app.js:113-125`) auto-updates position values (0-indexed) on drag-drop. Persistence happens on form submit (standard Django formset save).

### Compatibility

- Works with `has_add_permission=False` / `has_delete_permission=False` ✓
- `position` must be in `fields` and NOT in `readonly_fields` ✓ (already the case from T10a)
- Works with `tab = True` ✓

### Fix Classification: `NATIVE`

Set two attributes. No custom code needed.

## 3. Inline Tabs

### Unfold Native Inline Tabs

Set `tab = True` on any inline class. Unfold automatically:
- Generates tab navigation buttons using `verbose_name_plural`
- Controls visibility via Alpine.js `x-show="activeTab == '{{ formset.prefix|slugify }}'"`
- Hides inline heading (replaced by tab button)
- Preserves active tab in URL hash

### Interaction with `after_field_sets`

The `after_field_sets` block (line 72 of Unfold's change_form.html) has NO `x-show` directive — content is always visible regardless of active tab. Our "Add element"/"Add handler" dropdowns will always be accessible.

### Fix Classification: `NATIVE`

Set one attribute per inline. No template changes needed.

## 4. Handler Add

### Current State

Already functional from T10a. The `change_form.html` template renders "Add handler" dropdown with single-use filtering. Add views use fobi's `AddFormHandlerEntryView` which does NOT filter by user.

### Fix Classification: already `NATIVE`

No changes needed. Regression test already exists.

## 5. Implementation Plan

| # | Change | Classification | Lines |
|---|--------|---------------|-------|
| 1 | Monkey-patch fobi view `_get_queryset` for staff users | `UNAVOIDABLE_PATCH` | ~25 |
| 2 | Set `ordering_field` + `hide_ordering_field` on element inline | `NATIVE` | +2 |
| 3 | Set `tab = True` on both inlines | `NATIVE` | +2 |
| 4 | Add test: element edit by non-owner admin | test | ~15 |
| 5 | Add test: inline tabs present | test | ~5 |
| 6 | Add test: sortable ordering persistence | test | ~10 |

Net new code: ~60 lines (including tests). All non-test changes are either pure Unfold configuration or a justified unavoidable patch.
