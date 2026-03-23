# T11 Analysis: Source/Function Necessity Audit

**Branch:** `feat/t11-src-test-rationalization`
**Date:** 2026-02-28

## Methodology

Every file in `src/unfold_fobi/` was read. Each class/function was classified as:
- **KEEP_NATIVE** — aligned with Django/Unfold default usage
- **KEEP_CUSTOM_REQUIRED** — unavoidable integration logic
- **SIMPLIFY** — can be reduced
- **REMOVE** — obsolete after T10-series

Template references were verified by searching for includes, extends, and
fobi theme attribute usage. The fobi package source was inspected to confirm
which theme templates are used during element/handler popup editing vs. the
old builder views.

---

## Python Files

### `admin.py` (415 lines)

| Item | Classification | Rationale |
|------|---------------|-----------|
| `FormElementEntryInline` | KEEP_CUSTOM_REQUIRED | T10 native inline for elements with drag-drop, actions |
| `FormHandlerEntryInline` | KEEP_CUSTOM_REQUIRED | T10 native inline for handlers with custom actions |
| `FormEntryProxyAdmin` | KEEP_CUSTOM_REQUIRED | Central T10 native change view with fieldsets, plugins |
| `get_form()` | KEEP_CUSTOM_REQUIRED | Injects request into Fobi's FormEntryForm |
| `get_fieldsets()` | KEEP_CUSTOM_REQUIRED | Dynamic fieldset layout from model fields |
| `change_view()` | KEEP_CUSTOM_REQUIRED | Passes plugin lists to template context |
| `export_selected_forms` | KEEP_NATIVE | Standard admin action |
| `clone_selected_forms` | KEEP_CUSTOM_REQUIRED | Uses services.clone_form_entry |

### `models.py` (8 lines)

| Item | Classification | Rationale |
|------|---------------|-----------|
| `FormEntryProxy` | KEEP_CUSTOM_REQUIRED | Proxy model with translatable verbose_name |

### `apps.py` (503 lines)

| Item | Classification | Rationale |
|------|---------------|-----------|
| `patch_form_init()` | KEEP_CUSTOM_REQUIRED | Unfold widget application to fobi forms |
| `_patch_fobi_owner_filtering()` | KEEP_CUSTOM_REQUIRED | T10b: staff can edit non-owned elements |
| `_patch_fobi_popup_response()` | KEEP_CUSTOM_REQUIRED | T10e/T10g: popup + iframe compat |
| `ready()` — widget patches | KEEP_CUSTOM_REQUIRED | All fobi forms get Unfold widgets |
| `ready()` — db_store signal | KEEP_CUSTOM_REQUIRED | Auto-attach handler on form save |

### `views.py` (124 lines)

| Item | Classification | Rationale |
|------|---------------|-----------|
| `FormWizardsDashboardView` | KEEP_CUSTOM_REQUIRED | Redirect registered in admin.py get_urls |
| `FormEntryImportView` | KEEP_CUSTOM_REQUIRED | Redirect registered in admin.py get_urls |
| `normalize_field_choices()` | KEEP_CUSTOM_REQUIRED | Used by get_form_fields DRF endpoint |
| `_fallback_choices()` | KEEP_CUSTOM_REQUIRED | Fallback for normalize_field_choices |
| `_coerce_choice_pair()` | KEEP_CUSTOM_REQUIRED | Helper for _fallback_choices |
| `get_form_fields()` | KEEP_CUSTOM_REQUIRED | DRF API endpoint for frontend form rendering |

### `forms.py` (365 lines)

| Item | Classification | Rationale |
|------|---------------|-----------|
| `_SplitDateTimeStringValueMixin` | KEEP_CUSTOM_REQUIRED | Fix for MultiWidget returning list |
| `UnfoldAdminSplitDateTimeWidgetCompat` | KEEP_CUSTOM_REQUIRED | Used in widget_map |
| `apply_unfold_widgets_to_form()` | KEEP_CUSTOM_REQUIRED | Core widget replacement logic |
| `UnfoldFormMixin` | KEEP_CUSTOM_REQUIRED | Mixin for manual form widget application |
| `_layout_contains_field()` | KEEP_CUSTOM_REQUIRED | Crispy layout helpers |
| `ensure_field_in_helper_layout()` | KEEP_CUSTOM_REQUIRED | Ensures is_cloneable in layout |
| `align_visibility_fields_in_layout()` | KEEP_CUSTOM_REQUIRED | Groups is_public + is_cloneable in row |
| `FormEntryFormWithCloneable` | KEEP_CUSTOM_REQUIRED | Adds is_cloneable field |

### `services.py` (108 lines)

| Item | Classification | Rationale |
|------|---------------|-----------|
| `clone_form_entry()` | KEEP_CUSTOM_REQUIRED | Admin action "Clone selected forms" |
| `_generate_clone_name_slug()` | KEEP_CUSTOM_REQUIRED | Helper for clone_form_entry |

### `context_processors.py` (41 lines)

| Item | Classification | Rationale |
|------|---------------|-----------|
| `FOBI_TITLES` dict | KEEP_CUSTOM_REQUIRED | Provides content_title for fobi views in admin context |
| `admin_site()` | KEEP_CUSTOM_REQUIRED | Injects branding/sidebar for fobi theme templates |

### `fobi_themes.py` (38 lines)

| Item | Classification | Rationale |
|------|---------------|-----------|
| `UnfoldSimpleTheme` | KEEP_CUSTOM_REQUIRED | Theme registration; templates for element/handler popups |

### `fobi_admin.py` (228 lines)

| Item | Classification | Rationale |
|------|---------------|-----------|
| Model unregistration loop | KEEP_CUSTOM_REQUIRED | Re-register fobi models with Unfold ModelAdmin |
| `FormElementEntryInlineAdmin` | KEEP_CUSTOM_REQUIRED | Unfold inline for fobi's FormEntry admin |
| `FormEntryAdmin` | KEEP_CUSTOM_REQUIRED | Unfold-styled FormEntry admin (redirects to builder) |
| `FormWizardEntryAdmin` | KEEP_CUSTOM_REQUIRED | Unfold-styled wizard admin |
| `SavedFormDataEntryAdmin` | KEEP_CUSTOM_REQUIRED | T07: readonly for non-superuser |
| All other `@admin.register` | KEEP_NATIVE | Vanilla Unfold re-registrations |

### `fobi_compat.py` (26 lines)

| Item | Classification | Rationale |
|------|---------------|-----------|
| `set_value` shim | KEEP_CUSTOM_REQUIRED | DRF 3.15+ compat for fobi DRF integration |

### `templatetags/unfold_fobi_tags.py` (72 lines)

| Item | Classification | Rationale |
|------|---------------|-----------|
| `length_is` filter | KEEP_CUSTOM_REQUIRED | Django 5.0+ compat for fobi templates |
| `get_form_classes` tag | KEEP_CUSTOM_REQUIRED | Used by form snippets |
| `captureas` tag | KEEP_CUSTOM_REQUIRED | Used by skeleton.html |

### Management commands (4 files)

| File | Classification | Rationale |
|------|---------------|-----------|
| `create_test_form.py` | KEEP_CUSTOM_REQUIRED | Dev utility |
| `add_rest_api_form_data.py` | KEEP_CUSTOM_REQUIRED | Dev utility |
| `attach_db_store_handler.py` | KEEP_CUSTOM_REQUIRED | Operations utility |
| `cleanup_db_store_handlers.py` | KEEP_CUSTOM_REQUIRED | Operations utility |

---

## Template Files

### Templates actively used by T10 flow

| Template | Usage |
|----------|-------|
| `admin/unfold_fobi/formentryproxy/change_form.html` | T10 native change form — Add element/handler dropdowns |
| `admin/unfold_fobi/popup_response.html` | T10e — popup close/reload response |

### Templates used by fobi element/handler popup views

These are rendered when clicking Edit/Add on elements/handlers in popup mode.
The fobi views use: `base_edit_template` → `form_edit_snippet_template_name`.

| Template | Usage |
|----------|-------|
| `override_simple_theme/base_edit.html` | Base for fobi element/handler edit views |
| `override_simple_theme/snippets/form_edit_snippet.html` | Form rendering in element/handler popups |
| `override_simple_theme/snippets/form_properties_snippet.html` | Form properties rendering |
| `override_simple_theme/snippets/form_snippet.html` | Public form rendering |
| `override_simple_theme/snippets/form_wizard_properties_snippet.html` | Wizard properties |
| `unfold/layouts/skeleton.html` | Unfold skeleton override (used by base_edit.html chain) |

### Templates NOT used by T10 flow — REMOVE

Verified by:
- `edit_form_entry_ajax_template` is used ONLY by fobi's `EditFormEntryView` (old builder), NOT by element/handler views
- `action_dropdown.html` and `legend.html` are ONLY included by `edit_form_entry_ajax.html`
- `create_form_*` and `fobi_embed.html` have zero references in Python code

| Template | Reason for removal |
|----------|-------------------|
| `admin/fobi_embed.html` | Old iframe embed; no references in views/admin |
| `unfold_fobi/create.html` | Old builder create; extends generic fobi template |
| `override_simple_theme/create_form_entry_ajax.html` | Old AJAX create |
| `override_simple_theme/create_form_wizard_entry.html` | Old wizard create |
| `override_simple_theme/create_form_wizard_entry_ajax.html` | Old wizard AJAX create |
| `override_simple_theme/edit_form_entry_ajax.html` | Old builder edit; element/handler views use different templates |
| `unfold_fobi/components/action_dropdown.html` | Only used by edit_form_entry_ajax.html |
| `unfold_fobi/components/legend.html` | Only used by edit_form_entry_ajax.html |

---

## Static Files

| File | Classification | Rationale |
|------|---------------|-----------|
| `js/fobi_unfold.js` | **REMOVE** | Empty (2 comment lines); zero references |
| `css/fobi_unfold.css` | KEEP_CUSTOM_REQUIRED | Dark mode sidebar fixes; referenced in fobi_themes.py |

---

## Test Impact

No tests reference the templates or JS file being removed. All removals are
for old builder views that have zero test coverage (tests verify the new T10
native change flow). No test removals needed.

---

## Summary

| Category | Count |
|----------|-------|
| Files to REMOVE | 9 (8 templates + 1 JS) |
| Python functions to REMOVE | 0 |
| Python functions to SIMPLIFY | 0 |
| Templates to KEEP | 8 |
| Python files to KEEP | All |
| Tests to remove | 0 |

The codebase is already well-rationalized after T10. The main cleanup
opportunity is removing old builder templates that are no longer in the T10
navigation path. All Python code serves active integration purposes.