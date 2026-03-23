# T10a Codex Review — Native Change View Elements & Handlers

## Scope
- `src/unfold_fobi/admin.py` — change_view override, editable position inline
- `src/unfold_fobi/templates/admin/unfold_fobi/formentryproxy/change_form.html` — new template
- `tests/test_edit_view.py` — T10a test additions
- `.agents/reviews/feat-t10-native-unfold-poc__T10a-analysis.md` — Phase 0 analysis

## Round 1 (Codex CLI)

**P1**: Template not tracked in git — new file needs to be staged for commit.
- **Status**: Expected for new files. Will be staged.

Pre-existing ruff warnings (not T10a regressions):
- UP038: isinstance tuple → union syntax (line 233)
- UP031: % format → f-string (line 306)

## Bug Found During Development

**Critical**: `get_user_form_element_plugins_grouped()` and `get_user_form_handler_plugins()` take `user` not `request`.
The initial implementation passed `request` instead of `request.user`, causing empty plugin lists.
- **Fix**: Changed to `request.user` in both calls.

## Result

- 104 tests pass (97 original + 7 new T10a tests)
- Review: done