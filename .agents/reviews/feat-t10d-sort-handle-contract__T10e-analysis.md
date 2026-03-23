# T10e Feasibility Analysis: Admin-Popup Style Element Edit/Add

## Decision: `FEASIBLE_WITH_LIMITS`

## Current Flow

1. User clicks "Edit" link in element inline → full-page navigation to
   `/admin/fobi/forms/elements/edit/{id}/`
2. Fobi renders plugin config form using simple theme templates
3. On save → `redirect("fobi.edit_form_entry")` → user lands on fobi's
   standalone builder page (not the native change form)

**Key problem**: after editing an element, the user leaves the native
admin change page and lands on fobi's old builder view.

## Django Admin Popup Contract

| Step | Contract |
|------|----------|
| Open | Add `?_popup=1` to URL; open as `window.open()` or iframe |
| Detect | `IS_POPUP_VAR` (`_popup`) in `request.GET` or `request.POST` |
| Form | Hidden `<input name="_popup" value="1">` preserves flag across POST |
| Success | Render `popup_response.html` with JSON payload instead of redirect |
| Close | JS calls `window.opener.dismiss*Popup()` or `postMessage` to parent |

## Fobi View Architecture

- `AddFormElementEntryView(PermissionMixin, CreateView)` → on save calls
  `do_save_object()` which returns `redirect()`
- `EditFormElementEntryView(PermissionMixin, UpdateView)` → on save does
  `obj.save()` then returns `redirect()`
- Both inherit from Django CBVs — patchable
- Simple theme `base_edit.html` already checks `is_popup` (hides chrome)

## Compatibility with django-unfold-modal

django-unfold-modal bridges popups to iframe modals via postMessage:
- Expects `popup_response.html` template with JSON data
- Sends `django:popup:change` / `django:popup:add` messages to parent
- Parent calls `dismiss*Popup()` with fake window object
- No changes to django-unfold-modal needed

## Implementation Path

### Step 1: Append `_popup=1` to links
- In `element_actions()` and `handler_actions()` methods (admin.py)
- In change form template add-element/add-handler dropdowns

### Step 2: Patch fobi views for popup response
In `apps.py`, patch the post-save paths:
- `AddFormElementEntryView.do_save_object` → if `_popup`, return popup response
- `EditFormElementEntryView.post` → if response is redirect and `_popup`, swap
- Same for handler add/edit views

### Step 3: Provide popup response template
`templates/admin/unfold_fobi/popup_response.html` that:
- Sends `window.parent.postMessage({type: 'django:popup:change'})` for modals
- Falls back to `window.opener.location.reload(); window.close()` for popups
- Instructs parent to reload the change form (not update a select field)

### Step 4: Pass `is_popup` to fobi template context
Patch `get_context_data` on fobi views to set `is_popup=True` when
`_popup=1` is in request, so fobi's simple theme hides chrome.

## Limits

1. **Form rendering**: Still uses fobi simple theme, not native Unfold admin
   change form. Plugin forms are dynamic and plugin-specific — cannot be
   rendered through Django admin's `get_form()` without rewriting plugins.
2. **Monkey-patches**: Need 2 new patches (add save + edit post). Classified
   as `UNAVOIDABLE_PATCH` — fobi hardcodes redirect with no hook.
3. **Reload, not field update**: Parent page reloads entirely (not surgical
   field update) since we don't have a FK select to update.
4. **django-unfold-modal optional**: Works without the modal package too
   (plain window.open fallback). Package only needed for iframe-modal UX.

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Fobi template breaks in popup context | Simple theme already supports `is_popup` |
| Plugin form validation differs | Not touched — same `validate_plugin_data` path |
| Save logic changes | Not touched — same `save_plugin_data` + `obj.save()` |
| Widget styling missing | Existing apps.py patches apply in popup too |