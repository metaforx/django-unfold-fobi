# T10f Analysis: Unfold Modal Trigger Contract for Element Popup

## Decision: `FEASIBLE`

## Current State (T10e)

Element/handler action links use `onclick="window.open(...)"`:

```html
<a href="/fobi/.../edit/?_popup=1"
   onclick="window.open(this.href,'fobi_popup','width=800,height=600,scrollbars=yes');return false;"
   class="inline-flex items-center gap-1 text-primary-600 ...">
```

This bypasses Django's event system entirely. `django-unfold-modal`
never sees these clicks.

## django-unfold-modal Trigger Contract

`related_modal.js` intercepts via jQuery event delegation on `<body>`:

```javascript
$('body').on(
    'django:show-related',
    '.related-widget-wrapper-link[data-popup="yes"]',
    handleShowRelated
);
```

Required attributes on the `<a>` element:
1. `class` must include `related-widget-wrapper-link`
2. `data-popup="yes"` must be present
3. `id` must match pattern `^(change|add|delete)_<name>`
4. `href` must point to the target URL

When clicked, Unfold's `RelatedObjectLookups.js` fires a
`django:show-related` event. If `django-unfold-modal` is loaded, it
calls `event.preventDefault()` and opens the URL in an iframe modal.
If not loaded, Unfold's default handler opens `window.open()`.

## Gap Analysis

| Attribute | Django/Unfold contract | Current T10e links |
|-----------|------------------------|--------------------|
| CSS class `related-widget-wrapper-link` | Required | Missing |
| `data-popup="yes"` | Required | Missing |
| `id="(add\|change\|delete)_..."` | Required for naming | Missing |
| `onclick="window.open(...)"` | Not used | Present (blocks events) |
| `href` with `_popup=1` | Required | Present |

## Minimal Fix

1. **Add required attributes** to all action links:
   - `class="related-widget-wrapper-link ..."` (append to existing)
   - `data-popup="yes"`
   - `id="change_fobi_element_{pk}"` / `id="delete_fobi_element_{pk}"` / etc.

2. **Remove `onclick="window.open(...)"`** — Unfold's JS handles the
   open via `showRelatedObjectPopup()`. If `django-unfold-modal` is
   loaded, it intercepts and opens a modal. If not, Unfold opens a
   standard popup window.

3. **Keep `?_popup=1`** on URLs — `django-unfold-modal` ensures this
   param via `ensurePopupParam()`, but having it pre-set is safe.

4. **Keep popup response template** — The `popup_response.html` with
   `window.opener.location.reload()` / `postMessage` is still needed
   because fobi views are not standard Django admin views (no
   `popup_response.html` rendered by Django's admin machinery).

5. **Keep session-based popup tracking** — Still needed because fobi
   form `action="{{ request.path }}"` strips query params on POST.

## Scope

- `admin.py`: Update `element_actions()`, `handler_actions()` link HTML
- `change_form.html`: Update add-element/add-handler dropdown links
- `test_edit_view.py`: Update assertions for new attributes, remove
  `window.open` assertions
- No changes to `django-unfold-modal`
- No changes to fobi views or `apps.py`
