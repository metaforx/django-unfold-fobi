# T21 Analysis — Safe FormEntryProxy Delete

## Unlink strategy

`SavedFormDataEntry.form_entry` is nullable (`null=True, blank=True`) with
`on_delete=CASCADE`. Before deleting a form, `unlink_saved_entries()` runs
`UPDATE SET NULL` on all related saved entries. The form is then deleted
normally — elements and handlers cascade-delete (correct), saved data survives
with `form_entry=NULL`.

## Delete paths

- **Bulk action**: `safe_delete_selected` — custom admin action added to
  `actions` list. Checks `has_delete_permission(request, obj)` per form.
  With app-level delete permission, selected forms are deleted regardless of
  ownership.
- **Single delete**: `delete_model` override — unlinks before delete.
- **`delete_queryset`**: Still overridden for compatibility with any code path
  that calls it (e.g. Django's built-in `delete_selected` if re-enabled).

## Permission rule

- Delete is allowed when the user has `fobi.delete_formentry`.
- There is no additional ownership gate in admin delete checks.

## Why not `delete_selected`

`FormEntryProxyAdmin.actions` explicitly lists only `export_selected_forms`,
`clone_selected_forms`, and now `safe_delete_selected`. Django's built-in
`delete_selected` is not included — it would bypass the unlink step and
cascade-delete saved data.
