# T13 Analysis — Unfold Actions, Tab-Scoped Controls, Handler Modal Fixes

## 1. Popup/Modal Add/Delete Flow Analysis

### Current flow
1. User clicks "Add element/handler" link with `data-popup="yes"` + `?_popup=1`
2. `django-unfold-modal` intercepts click, opens iframe modal pointing to fobi view
3. Fobi view processes add/edit/delete
4. On success, `apps.py` `_wrap_method` intercepts redirect → returns `popup_response.html`
5. `popup_response.html` sends `postMessage({type: 'django:popup:change', reload: true})`

### Root cause of stale-state bugs
- `django-unfold-modal` receives `POPUP_CHANGE` message and calls `dismissChangeRelatedObjectPopup(fakeWin, data.objId, data.newRepr, data.newId)`
- Since popup_response.html sends NO `objId`/`newRepr`/`newId`, the dismiss callback gets `undefined` for all params
- `dismissChangeRelatedObjectPopup` does nothing useful (designed for related-object popups, not fobi element/handler add)
- **Result: modal closes but parent page does NOT reload → UI shows stale state**

### Fix
Replace `window.parent.postMessage(...)` with `window.parent.location.reload()` in iframe case.
This directly reloads the parent, closing the modal and refreshing all data/Alpine state.

## 2. Tab Scoping Analysis

### Current state
- Add Element/Handler buttons are in `{% block after_field_sets %}` (outside all tabs)
- Always visible regardless of which tab is active

### Tab mechanism (from Unfold skeleton.html)
- Alpine.js variable `activeTab` is initialized on `<body>` x-data
- Tab switching: `x-on:click="activeTab = '{slugified_prefix}'"`
- Inline visibility: `x-show="activeTab == '{slugified_prefix}'"`
- Formset prefixes: `formelemententry_set`, `formhandlerentry_set`

### Fix
Wrap each button group with `x-show="activeTab == '{prefix}'"` to scope visibility.

## 3. Import Action Analysis

### Pattern: Unfold `actions_list`
- Method decorated with `@action(description=..., url_path=..., icon=...)`
- Receives `(self, request)` — no queryset parameter
- Must return `HttpResponse`
- Auto-wired URL: `admin/<app>/<model>/<url_path>/`

### Fobi import internals
- `fobi.utils.perform_form_entry_import(request, form_data)` handles all creation
- JSON format: `{name, slug, is_public, form_elements: [...], form_handlers: [...]}`
- Missing plugins skipped with warnings
- Always sets `request.user` as owner

## 4. Email Handler

### Available plugin
- `fobi.contrib.plugins.form_handlers.mail` (UID: `mail`)
- Sends to fixed recipient address configured in handler settings
- No DRF integration counterpart needed (only admin-side)

### Setup
- Add to `INSTALLED_APPS`
- Set `EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"`

## Status: ANALYSIS COMPLETE — proceeding to implementation