# T16 Analysis — Optional Sites Integration Extraction

## Extraction boundary

### Package-generic (goes into `unfold_fobi.contrib.sites`)

| Component | Source (GovOS) | Package location |
|-----------|---------------|------------------|
| `FobiFormSiteBinding` model | `fobi_site_forms/models.py` | `contrib/sites/models.py` |
| Migration (table + seed) | `fobi_site_forms/migrations/` | `contrib/sites/migrations/` |
| `RelationSiteScopeAdminMixin` | `fobi_site_forms/admin.py` | `contrib/sites/admin.py` |
| Synthetic `sites` field in form admin | `fobi_site_forms/admin.py` | `contrib/sites/admin.py` (as `SiteAwareFormEntryMixin`) |
| Clone/import binding propagation | `fobi_site_forms/admin.py` | `contrib/sites/services.py` |
| Binding CRUD helpers | inline in GovOS admin | `contrib/sites/services.py` |
| `sites_for_user` resolution | hardcoded import | `contrib/sites/conf.py` (configurable via setting) |

### Project-specific (stays in consuming project)

| Component | Reason |
|-----------|--------|
| `GroupSite` model | User-to-site resolution is project-specific |
| `sites_for_user()` implementation | Depends on `GroupSite` or equivalent |
| `SiteRestrictedAdmin` base class | GovOS-specific permission policy |
| `_assign_binding_sites_with_fallback` logic | Uses `GroupSite`, project-specific |
| CMS signal sync | GovOS CMS integration |
| German messages ("Publikationsort", etc.) | GovOS-specific UX copy |
| `has_*_permission` overrides | Project-specific admin permission policy |

## How optional Sites mode is activated

1. Add `"unfold_fobi.contrib.sites"` to `INSTALLED_APPS` (after `"unfold_fobi"`)
2. Run `manage.py migrate unfold_fobi_sites`
3. Optionally set `UNFOLD_FOBI_SITES_FOR_USER = "myproject.utils.sites_for_user"` in settings

When the contrib app is **not** installed:
- No imports from `django.contrib.sites` occur in the base `unfold_fobi` package
- No `FobiFormSiteBinding` table is created
- Admin works exactly as before
- No settings breakage

## Why proxy-model handling remains unchanged

`FormEntryProxy` is a proxy model on `fobi.FormEntry`. The site binding uses a
**separate** `FobiFormSiteBinding` model with a `OneToOneField` to `FormEntryProxy`.
This avoids:
- Adding a real `sites` field to the proxy (which would require modifying the parent table)
- Forcing a schema change on `fobi.FormEntry`
- Breaking the proxy model contract

The `site_binding` reverse relation enables filtering through `form_entry__site_binding__sites`
without any changes to the proxy model itself.

## GovOS adoption note

After extraction, GovOS would:

**Replace with package functionality:**
- `fobi_site_forms/models.py` → use `unfold_fobi.contrib.sites.models.FobiFormSiteBinding`
- `fobi_site_forms/migrations/` → use contrib app migrations
- `RelationSiteScopeAdminMixin` → import from `unfold_fobi.contrib.sites.admin`
- Synthetic `sites` field logic → provided by `SiteAwareFormEntryMixin`
- Clone/import binding propagation → provided by `contrib/sites/services.py`

**Thin adapter code remaining in GovOS:**
- `fobi_site_forms/admin.py` → slim subclass that:
  - Configures `UNFOLD_FOBI_SITES_FOR_USER = "site_permissions.utils.sites_for_user"`
  - Overrides `assign_default_sites()` to use `GroupSite` fallback logic
  - Overrides `has_*_permission()` to delegate to `_has_site_scoped_permission()`
- `site_permissions/` → unchanged (project-specific foundation)