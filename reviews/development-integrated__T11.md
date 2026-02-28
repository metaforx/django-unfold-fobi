# Review: T11 — Source/Function Necessity Audit and Cleanup

**Branch:** `feat/t11-src-test-rationalization`
**Status:** Done

## Summary

Audited every file/function in `src/unfold_fobi/` for necessity after T10.
Removed 9 dead files (8 templates + 1 empty JS). All Python code confirmed
as actively required. No test removals needed.

## Audit Result

All Python files and functions serve active T10 integration purposes. The
main cleanup opportunity was removing old builder templates that are no longer
in the T10 navigation path (element/handler popup views use different fobi
theme templates).

## Files Removed

| File | Reason |
|------|--------|
| `js/fobi_unfold.js` | Empty (2 comment lines), zero references |
| `admin/fobi_embed.html` | Old iframe embed, zero references in code |
| `unfold_fobi/create.html` | Old builder create view override |
| `create_form_entry_ajax.html` | Old AJAX create (not used by element/handler views) |
| `create_form_wizard_entry.html` | Old wizard create |
| `create_form_wizard_entry_ajax.html` | Old wizard AJAX create |
| `edit_form_entry_ajax.html` | Old builder edit (element/handler views use form_edit_snippet) |
| `components/action_dropdown.html` | Only included by edit_form_entry_ajax.html |
| `components/legend.html` | Only included by edit_form_entry_ajax.html |

## Files Kept (with rationale in analysis note)

All Python files, active templates (change_form.html, popup_response.html,
base_edit.html, form_*_snippet.html, skeleton.html), CSS file, management
commands, and all test files.

## Complexity Summary

| Metric | Before | After |
|--------|--------|-------|
| Template files | 16 | 8 |
| Static JS files | 1 | 0 |
| Static CSS files | 1 | 1 |
| Python source files | 14 | 14 |
| Tests | 134 | 134 |
| Tests removed | — | 0 |

## Codex Review

Round 1: No issues found. Verified no runtime references to removed files
exist outside documentation/planning files.
