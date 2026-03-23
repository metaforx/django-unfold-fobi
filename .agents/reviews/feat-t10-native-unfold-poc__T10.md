# Codex Review — feat/t10-native-unfold-poc (T10)

**Status: DONE — No issues found.**

## Iterations

### Round 1
- **P1** `admin.py:92` — `handler_actions` built HTML via `str` concatenation losing `SafeString` safety; final `format_html("{}", actions_html)` escaped the links. **Fixed:** accumulate parts in a list and return `mark_safe(" &nbsp; ".join(parts))`.
- **P2** `urls.py:41` — Legacy edit redirect captured `form_entry_id` but `RedirectView.as_view(pattern_name=...)` passed it unchanged to admin change URL which expects `object_id`, causing `NoReverseMatch`. **Fixed:** replaced with explicit `_edit_form_entry_redirect` view function.

### Round 2
- **P1** `admin.py:116` — `get_custom_actions` called with `request=None`, preventing plugins from reading user/language context. **Fixed:** override `get_formset` to cache `self._request`, forward it to `get_plugin` and `get_custom_actions`.
- **P2** `admin.py:22` — Inlines described as read-only but `position` was editable and no `has_add/delete_permission` guards. **Fixed:** add `position` to `readonly_fields`; add `has_add_permission`/`has_delete_permission` returning `False` on both inlines.

### Round 3
No issues found — review clean.