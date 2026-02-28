# T10 Analysis: Native Unfold Admin Integration POC

## 1. Current Customization Inventory

### 1.1 URL Rewrites / Redirects

| # | Location | What | Purpose |
|---|----------|------|---------|
| U1 | `admin.py:167-172` | `redirect_change_to_builder_edit` | Intercepts `/<id>/change/` and redirects to custom `edit/<id>/` |
| U2 | `admin.py:211-214` | `response_change` override | After save, redirects to custom `edit/<id>/` instead of changelist |
| U3 | `admin.py:216-219` | `response_add` override | After add, redirects to custom `edit/<id>/` instead of changelist |
| U4 | `urls.py:33-46` | `fobi.create_form_entry` / `fobi.edit_form_entry` | Redirect legacy fobi routes to custom admin views |
| U5 | `admin.py:60-63` | `name_link` method | Changelist name column links to custom `edit/<id>/` |

### 1.2 Custom Edit Views

| # | Location | Lines | What |
|---|----------|-------|------|
| V1 | `views.py:38-267` | 230 | `FormEntryEditView` — full custom edit view wrapping `FobiEditFormEntryView` with Unfold mixin. Includes: handler changelist builder, breadcrumb context, ordering POST handler, T07 action URL rewrite. |
| V2 | `views.py:28-35` | 8 | `FormEntryCreateView` — wraps `FobiCreateFormEntryView` with Unfold mixin. |
| V3 | `views.py:270-278` | 9 | `FormWizardsDashboardView` / `FormEntryImportView` — simple redirects. |
| V4 | `views.py:282-390` | 109 | `get_form_fields` DRF endpoint — independent API, not part of edit flow. |

### 1.3 Template Overrides

| # | File | Lines | What |
|---|------|-------|------|
| T1 | `edit_form_entry_ajax.html` | 207 | Full custom edit template with Alpine.js tabs, element ordering JS, handler changelist rendering, properties form. |
| T2 | `base_edit.html` | 28 | Base template wrapping fobi edit in Unfold admin base. |
| T3 | `create_form_entry_ajax.html` | 1 | Extends fobi create template (thin wrapper). |
| T4 | `components/legend.html` | 17 | Reusable legend component for tab sections. |
| T5 | `components/action_dropdown.html` | 16 | Reusable dropdown component for add-element/handler actions. |
| T6 | `snippets/form_edit_snippet.html` | varies | Form edit snippet override. |
| T7 | `snippets/form_properties_snippet.html` | varies | Properties snippet override. |
| T8 | `unfold/layouts/skeleton.html` | 92 | Full Unfold skeleton layout override. |
| T9 | `admin/fobi_embed.html` | 12 | Iframe embed for fobi dashboard (legacy, unused in main flow). |

### 1.4 JS Behavior

| # | Location | What |
|---|----------|------|
| J1 | `edit_form_entry_ajax.html:62-138` | Ordering autosave — monitors jQuery UI sortable events, auto-submits position changes. |
| J2 | `edit_form_entry_ajax.html:3` | Alpine.js tab switching with localStorage persistence. |
| J3 | `fobi_unfold.js` | Dead file (2-line comment), already cleared in T06. |

### 1.5 Monkey Patches in `apps.py` (306 lines)

| # | Lines | Target | Purpose | Classification |
|---|-------|--------|---------|---------------|
| P1 | 68-114 | `fobi_forms.*` (8 form classes + 2 formsets) | Apply Unfold widgets to all fobi form `__init__` | **KEEP** — needed regardless of view approach |
| P2 | 117-132 | `fobi_helpers.get_form` | Apply Unfold widgets to dynamically assembled forms | **KEEP** — needed for any fobi form rendering |
| P3 | 136-168 | `fobi_base.FormElementPlugin._get_form_field_instances` / `FormFieldPlugin._get_form_field_instances` | Apply Unfold widgets to dynamically created plugin form fields | **KEEP** — needed for plugin config forms |
| P4 | 173-204 | `fobi_admin.FormElementEntryAdmin.get_form` / `FormHandlerEntryAdmin.get_form` | Apply Unfold widgets to admin-rendered plugin edit forms | **KEEP** — needed for element/handler editing in admin |
| P5 | 208-238 | `fobi_edit_views.EditFormElementEntryView.get_form` / `AddFormElementEntryView.get_form` | Apply Unfold widgets to fobi class-based element edit/add views | **KEEP** — needed for element config popup flows |
| P6 | 243-291 | `fobi_base.BasePlugin.get_form` / `get_initialised_edit_form_or_404` / `get_initialised_create_form_or_404` | Apply Unfold widgets to plugin forms at base level | **KEEP** — comprehensive fallback for all plugin forms |
| P7 | 294-306 | `post_save` signal on `FormEntry` | Auto-attach `db_store` handler to every form | **KEEP** — business logic, not view-related |

### 1.6 Other Custom Code

| # | File | Lines | What | Classification |
|---|------|-------|------|---------------|
| O1 | `admin.py:36-58` | 23 | `get_form` — injects request kwarg, datetime parsing | **KEEP** — needed for FormEntryForm compatibility |
| O2 | `admin.py:74-161` | 88 | `get_fieldsets` — dynamic fieldset grouping | **KEEP** — core Unfold UX for add/change view |
| O3 | `admin.py:227-266` | 40 | Export/clone/delete actions | **KEEP** — list actions, unrelated to edit flow |
| O4 | `forms.py` | 364 | Widget mapping + FormEntryFormWithCloneable | **KEEP** — widget layer, view-independent |
| O5 | `fobi_admin.py` | 227 | Re-registration of all fobi models with Unfold ModelAdmin | **KEEP** — needed for Unfold styling of all admin pages |
| O6 | `fobi_themes.py` | 37 | UnfoldSimpleTheme registration with CSS/JS overrides | **REPLACE** — only needed for custom builder template |
| O7 | `context_processors.py` | 40 | Inject admin context + title mapping for fobi views | **REPLACE** — only needed because fobi views render outside admin |
| O8 | `models.py` | 7 | `FormEntryProxy` | **KEEP** — used for admin registration |
| O9 | `services.py` | 107 | Clone service | **KEEP** — business logic |
| O10 | `fobi_compat.py` | 26 | DRF `set_value` shim | **KEEP** — DRF compatibility |

---

## 2. Classification Summary

### REMOVE (no longer needed with native admin change view)

| Item | What | Lines saved |
|------|------|-------------|
| U1 | `redirect_change_to_builder_edit` | 6 |
| U2 | `response_change` → custom edit redirect | 4 |
| U3 | `response_add` → custom edit redirect | 4 |
| U5 | `name_link` custom edit URL | 6 (rewrite to change URL) |
| V1 | `FormEntryEditView` (entire class) | ~230 |
| T1 | `edit_form_entry_ajax.html` | 207 |
| T2 | `base_edit.html` | 28 |
| T4 | `components/legend.html` | 17 |
| T5 | `components/action_dropdown.html` | 16 |
| J1 | Ordering autosave JS | 77 (inline) |
| J2 | Alpine.js tab switching | part of T1 |
| O6 | `fobi_themes.py` | 37 |
| O7 | `context_processors.py` | 40 |
| | Custom edit URL registration in `get_urls` | 8 |

**Total removable: ~680 lines**

### KEEP (still required regardless of approach)

| Item | What | Lines |
|------|------|-------|
| P1-P7 | Monkey patches for Unfold widgets | 230 |
| O1-O2 | get_form + get_fieldsets | 111 |
| O3 | Export/clone/delete actions | 40 |
| O4 | forms.py widget mapping | 364 |
| O5 | fobi_admin.py re-registration | 227 |
| O8-O10 | Models, services, compat | 140 |

### REPLACE (native Django/Unfold alternative)

| Item | Current | Replacement |
|------|---------|-------------|
| V1 | Custom `FormEntryEditView` with tabs | Native admin change view + inlines |
| T1 | Custom edit template with tabs | Native change_form.html (Unfold auto-renders fieldsets + inlines) |
| O6 | UnfoldSimpleTheme | Not needed — fobi element/handler config pages use admin base directly |
| O7 | context_processors.py | Not needed — native admin views have context built in |
| U4 | Legacy route redirects | Keep `fobi.edit_form_entry` redirect but point to native `/<id>/change/` |

---

## 3. Architecture Options

### Option A: Minimal Hybrid — Native Change + Fobi Element/Handler Popups

**Approach:**
- Use native admin `/<id>/change/` for form properties (name, slug, dates, visibility, etc.)
- Add `FormElementEntry` and `FormHandlerEntry` as **read-only inlines** showing current elements/handlers
- Element/handler add/edit/delete actions link to existing Fobi class-based views (popup-style or same-page redirects)
- Remove the entire custom edit view, tabs template, Alpine.js, ordering JS, handler changelist renderer

**What stays:**
- `get_fieldsets` — organizes properties into logical groups (already working for add view)
- `get_form` — injects request kwarg
- All monkey patches for Unfold widgets
- Fobi element/handler edit URLs (they render in admin base layout already)
- `fobi.edit_form_entry` redirect now points to native change view

**What goes:**
- `FormEntryEditView` (230 lines)
- `edit_form_entry_ajax.html` (207 lines)
- `base_edit.html` (28 lines)
- `legend.html`, `action_dropdown.html` (33 lines)
- `fobi_themes.py` (37 lines)
- `context_processors.py` (40 lines)
- URL rewrites (redirect_change_to_builder_edit, response_change/add overrides)
- Ordering autosave JS

**Risks:**
- Inline for elements loses drag-to-reorder (elements show as a list with position field instead)
- Plugin add/edit UX changes from in-page tabs to click-through links
- Callback URLs from fobi element/handler edit must redirect back to change view

**Complexity reduction: ~575 lines removed, 0 lines added for inline registration**

### Option B: Deeper Native — Inlines with Admin Actions

**Approach:**
- Same as Option A, but make `FormElementEntry` inline fully editable (not read-only)
- Use `sortable_by` or Alpine.js `x-sort` for drag ordering within the inline
- Add "add element" as a related-widget popup link (Django's `+` button pattern)

**Risks:**
- Element plugin_data is JSON — editing inline is possible but UX degrades without the plugin config form
- Ordering within inlines is supported by Unfold's `x-sort` but requires template-level integration
- More new code to wire inline ordering than Option A saves

**Complexity reduction: ~575 lines removed, ~100 lines added for ordering integration**

---

## 4. Recommendation: Option A — Minimal Hybrid

**Rationale:**
1. **Maximum complexity reduction** — removes ~575 lines of custom view/template/JS code with near-zero new code.
2. **Lower risk** — fobi's element/handler config flows continue to work exactly as they do today (they already render in admin base layout via the monkey patches). Only the "container" changes.
3. **No loss of capability** — all plugin add/edit/delete actions remain functional via existing Fobi URLs.
4. **Native admin benefits** — Unfold automatically provides fieldsets, breadcrumbs, save buttons, permissions, history, without any custom code.
5. **Maintainable** — future Unfold/Django upgrades don't require maintaining a parallel edit view.

**Trade-off acknowledged:** Element drag ordering is lost. This is acceptable for a POC because:
- Position can be set via inline field values
- Ordering can be restored later with Unfold's `x-sort` if the POC is accepted

## 5. Rollback Strategy

If the POC fails:
1. `git checkout development` — the custom edit view code is untouched on `development`
2. No schema changes are involved — rollback is purely code-level
3. The POC branch (`feat/t10-native-unfold-poc`) can be abandoned without affecting any other branch

## 6. Implementation Plan (Phase 1)

1. **Remove the `redirect_change_to_builder_edit` URL** — let `/<id>/change/` render the native change view.
2. **Remove `response_change` / `response_add` overrides** — let Django redirect to changelist (default) or the change view.
3. **Update `name_link`** to use native change URL instead of custom edit URL.
4. **Add `FormElementEntry` inline** to `FormEntryProxyAdmin` — readonly, showing plugin_uid, position, with edit/delete action links to fobi URLs.
5. **Add `FormHandlerEntry` inline** to `FormEntryProxyAdmin` — readonly, showing plugin_uid with action links.
6. **Update `fobi.edit_form_entry` redirect** in urls.py to point to native change view.
7. **Remove `FormEntryEditView`** from views.py.
8. **Remove `FormEntryCreateView`** from views.py (native add view works).
9. **Remove `fobi_themes.py`** — no custom builder template to reference.
10. **Remove `context_processors.py`** — no fobi views rendered in admin context.
11. **Clean up `apps.py`** — remove settings reference to context processor.
12. **Remove dead templates** — `edit_form_entry_ajax.html`, `base_edit.html`, `legend.html`, `action_dropdown.html`.
13. **Update tests** — breadcrumb and edit view tests adapt to native change view.

## 7. Before/After Complexity Estimate

| Metric | Before | After (est.) | Delta |
|--------|--------|-------------|-------|
| `views.py` | 390 lines | ~160 lines | -230 |
| `admin.py` | 267 lines | ~280 lines | +13 (inlines) |
| `fobi_themes.py` | 37 lines | 0 (removed) | -37 |
| `context_processors.py` | 40 lines | 0 (removed) | -40 |
| `edit_form_entry_ajax.html` | 207 lines | 0 (removed) | -207 |
| `base_edit.html` | 28 lines | 0 (removed) | -28 |
| Component templates | 33 lines | 0 (removed) | -33 |
| **Net custom code** | **~1002 lines** | **~440 lines** | **-562 lines** |
