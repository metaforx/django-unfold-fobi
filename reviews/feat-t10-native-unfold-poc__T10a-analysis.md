# T10a Analysis: Elements & Handlers on Native Change Page

## 1. Current State (after T10)

The native change view at `/<id>/change/` renders:
- **Fieldsets**: form properties (name, slug, visibility, etc.)
- **FormElementEntryInline**: read-only list of elements with edit/delete links
- **FormHandlerEntryInline**: read-only list of handlers with edit/delete/custom-action links

**Missing capabilities** (the T10a gap):
- No "Add element" UI — can't add new elements from the change page
- No "Add handler" UI — can't add new handlers from the change page
- No element sorting — position is readonly, no drag-and-drop or manual reorder
- No "Add element/handler" dropdown listing available plugins

## 2. What Pieces Are Required for Parity?

### From the old builder (edit_form_entry_ajax.html)

| Piece | Lines | Needed? | Reuse strategy |
|-------|-------|---------|----------------|
| Alpine.js tab switching | 10 | No | Native inlines replace tabs |
| "Available Form Fields" dropdown | 15 | **Yes** | Reuse component templates + fobi utils |
| "Available Form Handlers" dropdown | 18 | **Yes** | Reuse component templates + fobi utils |
| Element ordering JS (jQuery UI sortable) | 77 | **Partial** | Simpler position-update endpoint replaces full-page form submit |
| Ordering form + management_form | 12 | No | Position updates via custom admin endpoint |
| Handler changelist renderer | 4 | No | Already replaced by handler inline |
| Properties form | 16 | No | Already native fieldsets |
| legend.html component | 17 | **Maybe** | Could reuse for section headers |
| action_dropdown.html component | 16 | **Yes** | Dropdown component for "Add" menus |

### From fobi internals

| Piece | Location | Needed? |
|-------|----------|---------|
| `get_user_form_element_plugins_grouped(request)` | `fobi.utils` | **Yes** — provides grouped list of available element plugins |
| `get_user_form_handler_plugins(request)` | `fobi.utils` | **Yes** — provides list of available handler plugins |
| `fobi.add_form_element_entry` URL | `fobi/urls/class_based/edit.py` | **Yes** — existing add view, just link to it |
| `fobi.add_form_handler_entry` URL | same | **Yes** — existing add view |
| `fobi.edit_form_entry` redirect | `tests/server/testapp/urls.py` | **Already done** — redirects to native change |

## 3. Minimal Integration Design

### Approach: Custom `change_form_template` + admin endpoint

**Why this is minimal:**
- No new views — reuse existing fobi add/edit/delete views entirely
- No inline template overrides — the inlines stay read-only (add/delete happen through fobi URLs)
- One custom template extending Unfold's change_form.html (inject "Add" dropdowns)
- One custom admin endpoint for position updates (AJAX)
- ~60 lines of template, ~40 lines of endpoint, ~10 lines of JS

**Integration points:**

1. **`change_form_template`** on `FormEntryProxyAdmin` — custom template that extends Unfold's `admin/change_form.html`
   - Block `after_field_sets`: inject "Add element" and "Add handler" dropdowns before the inlines
   - Block `admin_change_form_document_ready`: inject minimal ordering JS

2. **`change_view` override** — pass `user_form_element_plugins` and `user_form_handler_plugins` via `extra_context`

3. **Custom admin URL** — `update-positions/` endpoint accepting JSON `{element_id: position}` pairs

4. **Element inline** — make `position` editable (remove from `readonly_fields`) so admins can manually set positions. Also enable client-side drag-and-drop sorting with the custom endpoint.

### What can be removed

| Item | Why |
|------|-----|
| `edit_form_entry_ajax.html` (207 lines) | No longer the primary UI — native change + inlines + template override replace it |
| Alpine.js tab switching JS | Inlines render directly, no tabs needed |
| Full ordering form submit pattern (77 lines of JS) | Replaced by AJAX position update endpoint (~10 lines of JS) |

### What is kept/reused

| Item | Why |
|------|-----|
| `action_dropdown.html` component | Reused for "Add element" and "Add handler" dropdowns in the custom change_form template |
| `fobi.utils` plugin discovery functions | Used to populate the dropdowns |
| All fobi add/edit/delete URLs | No changes — they redirect back to `fobi.edit_form_entry` which lands on native change |
| Element/handler inline action links | Already working from T10 |

## 4. Complexity Delta

| Metric | Before (T10) | After (T10a) | Delta |
|--------|-------------|-------------|-------|
| `admin.py` | 365 lines | ~420 lines | +55 (change_view, position endpoint, editable position) |
| New template | 0 | ~60 lines | +60 (change_form.html with dropdowns) |
| Ordering JS | 0 | ~15 lines | +15 (inline in template) |
| `edit_form_entry_ajax.html` | 207 lines | 207 lines (dead) | 0 (not removed yet, just unused) |
| **Net new code** | - | **~130 lines** | — |

**Justification**: The 130 lines of new code (change_view context, position endpoint, template, JS) replace the need for the 207-line edit_form_entry_ajax.html + 230-line FormEntryEditView that were removed in T10. The result is a fully functional element/handler management UI integrated into the native change page.

## 5. Implementation Plan

1. Add `change_view` override to pass available plugins to extra_context
2. Add `update-positions/` custom admin URL endpoint
3. Create `change_form.html` template extending Unfold's default
4. Make `position` editable in element inline
5. Add tests for: add element link presence, add handler link presence, position update endpoint, single-use handler constraint
6. Verify all 97+ tests still pass
