# T14 Source Structure Audit – Analysis Note

Branch: `feat/t14-apps-fobi-admin-refactor`
Base: `development-integrated` (post-T13)

## File-by-File Decisions

### Python modules

| File | Lines | Decision | Rationale |
|------|-------|----------|-----------|
| `apps.py` | 544 | **SPLIT** | Carries 5+ concerns: widget patching, owner-filter patching, popup-response patching, signals, startup imports. Target: thin AppConfig + `patches/` + `signals.py` |
| `fobi_admin.py` | 293 | **KEEP_AS_IS** | Single purpose: unregister fobi admins, re-register with Unfold. ProxyOnlyFobiAdminMixin + inlines are tightly coupled to the registrations. Already well-bounded. |
| `admin/__init__.py` | 5 | **KEEP_AS_IS** | Clean re-export of FormEntryProxyAdmin |
| `admin/form_entry_proxy.py` | 372 | **KEEP_AS_IS** | Main admin — already extracted from monolithic admin.py in T12 |
| `admin/inlines.py` | 188 | **KEEP_AS_IS** | Element/handler inline definitions — clean separation |
| `views.py` | 21 | **KEEP_AS_IS** | Two redirect views, minimal |
| `services.py` | 106 | **KEEP_AS_IS** | clone_form_entry + helper, single responsibility |
| `fobi_compat.py` | 27 | **KEEP_AS_IS** | DRF set_value shim — needed until fobi drops DRF <3.15 |
| `fobi_themes.py` | 49 | **KEEP_AS_IS** | Theme registration, minimal |
| `context_processors.py` | 39 | **KEEP_AS_IS** | Admin site context injection, minimal |
| `models.py` | 9 | **KEEP_AS_IS** | FormEntryProxy proxy model |
| `forms/__init__.py` | 21 | **KEEP_AS_IS** | Clean re-exports (remove dead exports after cleanup) |
| `forms/form_entry.py` | 28 | **KEEP_AS_IS** | FormEntryFormWithCloneable |
| `forms/import_json.py` | 80 | **KEEP_AS_IS** | ImportFormEntryJsonForm with validation |
| `forms/layout.py` | 51 | **REMOVE** | `align_visibility_fields_in_layout` is commented out everywhere it was used. No live callers. Dead code. |
| `forms/mixins.py` | 20 | **REMOVE** | `UnfoldFormMixin` is defined but never used by any form class in the project. Dead code. |
| `forms/widgets.py` | 239 | **KEEP_AS_IS** | Core widget mapping, heavily used by patches |
| `templatetags/unfold_fobi_tags.py` | 72 | **KEEP_AS_IS** | Template compatibility filters + captureas tag |
| `api/__init__.py` | 0 | **KEEP_AS_IS** | Package marker |
| `api/views.py` | 105 | **KEEP_AS_IS** | DRF form-fields endpoint |
| `api/urls.py` | 13 | **KEEP_AS_IS** | API URL config |
| `management/commands/*.py` | 508 | **KEEP_AS_IS** | Dev/test utilities |
| `migrations/0001_initial.py` | 26 | **KEEP_AS_IS** | Migration |
| `__init__.py` | 0 | **KEEP_AS_IS** | Package marker |

### Templates

All templates: **KEEP_AS_IS** — used by admin views and fobi theme.

### Static files

All static files: **KEEP_AS_IS** — popup bridge JS and CSS fixes are in use.

## Deep Review: `apps.py`

**Current responsibilities (544 lines):**

1. **`patch_form_init()` helper** (lines 7–33) — generic form-class monkey-patch utility
2. **`_patch_fobi_owner_filtering()`** (lines 41–111) — relaxes fobi queryset + permission checks for staff
3. **`_patch_fobi_popup_response()`** (lines 113–232) — intercepts fobi view redirects in popup mode
4. **Widget patching in `ready()`** (lines 257–504) — patches ~10 form classes, formsets, helpers, plugins, admin views, base plugin methods
5. **Signal registration** (lines 507–533) — `ensure_db_store_handler` + `deduplicate_db_store_handler`
6. **Startup orchestration** (lines 234–544) — imports fobi_compat, fobi_admin, DRF handler

**Target structure after split:**

```
patches/
├── __init__.py          # apply_all_patches() convenience function
├── owner_filtering.py   # _patch_fobi_owner_filtering
├── popup_response.py    # _patch_fobi_popup_response
└── widgets.py           # patch_form_init + all widget patching from ready()
signals.py               # db_store auto-attach + dedup
apps.py                  # ~40 lines: AppConfig.ready() calls patches + signals
```

**Contracts that must remain stable:**
- `apps.py` must import `fobi_compat` before any fobi imports
- `apps.py` must import `fobi_admin` to trigger admin registration
- All patches must be idempotent (guard with `_unfold_patched` flags)
- Signal handlers must use `dispatch_uid` to avoid double-registration

## Deep Review: `fobi_admin.py`

**Current responsibilities (293 lines):**

1. Unregister all fobi models from admin (lines 70–90)
2. `ProxyOnlyFobiAdminMixin` — hides raw fobi admins (lines 93–116)
3. Four inline admin classes for fobi models (lines 120–167)
4. Re-register all fobi models with Unfold ModelAdmin (lines 172–268)
5. `SavedFormDataEntry` special permissions (lines 270–286)
6. `FormEntryAdmin.get_urls` redirect to fobi edit view (lines 178–202)

**Decision: KEEP_AS_IS.** All six responsibilities are tightly coupled — they're all part of "make fobi admin use Unfold instead of default Django admin." Splitting would create artificial module boundaries with heavy cross-references. The 293-line module is already within reasonable size.

## Dead Code to Remove

1. `forms/layout.py` — `align_visibility_fields_in_layout` is commented out in its only caller (`forms/form_entry.py`). No live usage.
2. `forms/mixins.py` — `UnfoldFormMixin` is defined but never used by any form class.
3. Corresponding exports in `forms/__init__.py`.

**Note:** These were previously exported in `forms/__init__.__all__`, making them technically part of the public API surface. Since no internal or known external code uses them, this is an intentional API reduction. If downstream consumers exist in future, they would need to vendor or re-implement these trivial helpers.

## Summary of Changes

| Action | Count | Details |
|--------|-------|---------|
| SPLIT | 1 | `apps.py` → `apps.py` + `patches/` + `signals.py` |
| REMOVE | 2 | `forms/layout.py`, `forms/mixins.py` |
| KEEP_AS_IS | 22+ | All other modules, templates, static files |

**Expected line-count reduction for `apps.py`:** 544 → ~40 (with ~500 lines redistributed to `patches/` and `signals.py`)