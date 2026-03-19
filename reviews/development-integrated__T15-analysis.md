# T15 Analysis — Unfold Submit Row for Popup Modal Element/Handler Forms

## Template chain for popup element/handler forms

```
add_form_element_entry.html (fobi generic)
  extends: fobi_theme.base_edit_template
    → override_simple_theme/base_edit.html (extends admin/base.html)
  content block includes: fobi_theme.add_form_element_entry_ajax_template
    → fobi/generic/add_form_element_entry_ajax.html
      extends: fobi_theme.form_edit_ajax
        → simple/snippets/form_edit_ajax.html  ← NOT OVERRIDDEN
          includes: fobi_theme.form_edit_snippet_template_name
            → override_simple_theme/snippets/form_edit_snippet.html (Unfold-styled)
          submit row: <input type="submit" class="default" ...>  ← PLAIN DJANGO ADMIN STYLE
```

Same chain applies for:
- `edit_form_element_entry_ajax.html`
- `add_form_handler_entry_ajax.html`
- `edit_form_handler_entry_ajax.html`

## Root cause

`UnfoldSimpleTheme.form_edit_ajax` is **not overridden**, so it inherits
`SimpleTheme.form_edit_ajax = "simple/snippets/form_edit_ajax.html"`.

That template renders the submit button as:
```html
<div class="submit-row">
  <input type="submit" class="default" value="..."/>
</div>
```

This uses Django admin CSS classes (`submit-row`, `default`) which have no styling
in the Unfold modal iframe context. Result: the button exists in the DOM but is
invisible or unstyled — users see no save action.

## Comparison: native Unfold submit row vs current

| Aspect | Unfold `admin/submit_line.html` | Simple theme `form_edit_ajax.html` |
|--------|--------------------------------|-------------------------------------|
| Button element | `<button>` component | `<input type="submit">` |
| CSS | Tailwind (primary-600, rounded, etc.) | Bootstrap 3 / Django admin |
| Dark mode | Full dark mode support | None |
| Layout | Flex row-reverse, sticky | Static div |
| Form ID | Present | Missing (no `form_id` block consumed) |

## Minimal override point

**Override `form_edit_ajax` in `UnfoldSimpleTheme`.**

Create `override_simple_theme/snippets/form_edit_ajax.html` that:
1. Preserves all blocks used by child templates (`form_page_title`, `form_id`, `form_primary_button_text`, etc.)
2. Replaces the submit row with Unfold-styled button using the same Tailwind classes as `admin/submit_line.html`
3. Adds `form_id` block to the `<form>` tag (currently missing in simple theme version)
4. Uses Unfold heading style (H3 with legend classes) instead of raw H1

## Add vs edit — same template path

All four ajax templates (`add_form_element_entry_ajax.html`, `edit_form_element_entry_ajax.html`, `add_form_handler_entry_ajax.html`, `edit_form_handler_entry_ajax.html`) extend `fobi_theme.form_edit_ajax`. A single override covers all four flows.

## Popup compatibility

- `_popup=1` detection and popup response logic are handled by `patches/popup_response.py` — not affected by template changes.
- Sidebar suppression is in `base_edit.html` — not affected.
- `X-Frame-Options: SAMEORIGIN` header is set by the patch — not affected.

No changes to popup/modal mechanics are needed.
