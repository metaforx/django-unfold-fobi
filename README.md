# django-unfold-fobi

[![PyPI - Version](https://img.shields.io/pypi/v/django-unfold-fobi.svg?style=for-the-badge)](https://pypi.org/project/django-unfold-fobi/)
[![Build](https://img.shields.io/github/actions/workflow/status/metaforx/django-unfold-fobi/ci.yml?style=for-the-badge&event=pull_request)](https://github.com/metaforx/django-unfold-fobi/actions/workflows/ci.yml)

Unfold integration for `django-fobi`: Unfold-styled admin, Unfold theme for the
form builder UI, DRF compatibility shims, and a few Unfold-friendly admin views.
The optional Sites extension lives in `unfold_fobi.contrib.sites`.

This README shows the integration steps as they are used in
`djangocms_test/settings.py` and `djangocms_test/urls.py`.

## Quick Start

1. Install dependencies.

```bash
pip install django-unfold-fobi
```

2. Follow the standard `django-fobi` installation and plugin setup first, then add the `unfold_fobi` integration apps to `INSTALLED_APPS` (order matters).

```python
INSTALLED_APPS = [
    "unfold",  # must be before django.contrib.admin
    "crispy_forms",  # required by unfold_fobi layouts/templates
    "fobi.contrib.themes.simple",  # required, Unfold theme extends it
    "unfold_fobi",
]
```

Add your normal `django-fobi` apps, plugins, and optional DRF integration exactly as documented by `django-fobi`.

If you want site-aware form bindings, add the optional app too:

```python
INSTALLED_APPS += [
    "django.contrib.sites",
    "unfold_fobi.contrib.sites",
]

SITE_ID = 1
```

3. Add template context processors and builtins.

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "fobi.context_processors.theme",
                "unfold_fobi.context_processors.admin_site",
            ],
            "builtins": [
                "unfold_fobi.templatetags.unfold_fobi_tags",
            ],
        },
    },
]
```

4. Enable the Unfold Fobi theme and crispy forms pack.

```python
FOBI_THEME = "unfold"
FOBI_DEFAULT_THEME = "unfold"

CRISPY_TEMPLATE_PACK = "unfold_crispy"
CRISPY_ALLOWED_TEMPLATE_PACKS = ["unfold_crispy"]
```

5. Add URLs from `djangocms_test/urls.py`.

```python
from django.urls import include, path

urlpatterns = [
    # DRF integration endpoints (optional)
    path("api/", include("fobi.contrib.apps.drf_integration.urls")),
    path("api/", include("unfold_fobi.api.urls")),

    # Public Fobi routes
    path("fobi/", include("unfold_fobi.urls.public")),

    # Admin/Fobi edit + legacy compatibility routes
    # Place before admin.site.urls to avoid admin catch_all_view shadowing.
    path("admin/fobi/", include("unfold_fobi.urls.admin")),
]
```

6. Run migrations.

```bash
python manage.py migrate
```

## Settings Reference (Unfold Sidebar)

This is the "Forms" navigation block used in `djangocms_test/settings.py`.
It links to `unfold_fobi` admin views and Fobi routes. Include the
`reverse_lazy`/`gettext_lazy` imports.

```python
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SIDEBAR": {
        "navigation": [
            {
                "title": _("Forms"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("All Forms"),
                        "icon": "list",
                        "link": reverse_lazy("admin:unfold_fobi_formentryproxy_changelist"),
                        "active": lambda request: (
                            getattr(getattr(request, "resolver_match", None), "view_name", "")
                            in {
                                "admin:unfold_fobi_formentryproxy_changelist",
                                "admin:unfold_fobi_formentryproxy_add",
                                "admin:unfold_fobi_formentryproxy_change",
                                "fobi.edit_form_entry",
                            }
                            or request.path.startswith("/admin/unfold_fobi/formentryproxy/")
                            or request.path.startswith("/admin/fobi/forms/")
                        ),
                    },
                    {
                        "title": _("Import Form"),
                        "icon": "upload",
                        "link": reverse_lazy("admin:unfold_fobi_formentryproxy_import_form_entry_action"),
                        "active": lambda request: getattr(
                            getattr(request, "resolver_match", None), "view_name", ""
                        )
                        in {
                            "admin:unfold_fobi_formentryproxy_import_form_entry_action",
                            "fobi.import_form_entry",
                        }
                        or request.path.startswith("/admin/fobi/forms/import/")
                        or request.path.startswith("/admin/unfold_fobi/formentryproxy/import-json/"),
                    },
                    {
                        "title": _("Wizards"),
                        "icon": "auto_awesome",
                        "link": reverse_lazy("fobi.form_wizards_dashboard"),
                        "active": lambda request: getattr(
                            getattr(request, "resolver_match", None), "view_name", ""
                        )
                        in {
                            "fobi.form_wizards_dashboard",
                        }
                        or request.path.startswith("/admin/fobi/wizards/")
                    },
                ],
            },
        ],
    },
}
```

## Optional Sites Integration

The base package does not require `django.contrib.sites`. Enable the Sites
extension only if your project needs form-to-site bindings.

1. Add the optional apps:

```python
INSTALLED_APPS += [
    "django.contrib.sites",
    "unfold_fobi.contrib.sites",
]

SITE_ID = 1
UNFOLD_FOBI_SITES_FOR_USER = "myproject.site_permissions.sites_for_user"
```

2. Run migrations:

```bash
python manage.py migrate
```

3. Re-register your admin classes with the mixins from
`unfold_fobi.contrib.sites.admin`:

```python
from django.contrib import admin
from fobi.contrib.plugins.form_handlers.db_store.models import SavedFormDataEntry

from unfold_fobi.admin import FormEntryProxyAdmin as BaseFormEntryProxyAdmin
from unfold_fobi.contrib.sites.admin import (
    RelationSiteScopeAdminMixin,
    SiteAwareFormEntryMixin,
)
from unfold_fobi.fobi_admin import SavedFormDataEntryAdmin as BaseSavedEntryAdmin
from unfold_fobi.models import FormEntryProxy


admin.site.unregister(FormEntryProxy)


@admin.register(FormEntryProxy)
class FormEntryProxyAdmin(
    SiteAwareFormEntryMixin,
    RelationSiteScopeAdminMixin,
    BaseFormEntryProxyAdmin,
):
    site_relation_lookup = "site_binding__sites"

    def has_view_permission(self, request, obj=None):
        return self._has_site_scoped_permission(request, "view", obj)

    def has_change_permission(self, request, obj=None):
        return self._has_site_scoped_permission(request, "change", obj)

    def has_delete_permission(self, request, obj=None):
        return self._has_site_scoped_permission(request, "delete", obj)


admin.site.unregister(SavedFormDataEntry)


@admin.register(SavedFormDataEntry)
class SavedFormDataEntryAdmin(RelationSiteScopeAdminMixin, BaseSavedEntryAdmin):
    site_relation_lookup = "form_entry__site_binding__sites"

    def has_view_permission(self, request, obj=None):
        return self._has_site_scoped_permission(request, "view", obj)
```

What the package provides:
- `FobiFormSiteBinding` to persist form-to-site relations.
- `SiteAwareFormEntryMixin` to add the synthetic `sites` field to the form admin.
- `RelationSiteScopeAdminMixin` to filter querysets by a relation path such as
  `site_binding__sites` or `form_entry__site_binding__sites`.
- Binding helpers in `unfold_fobi.contrib.sites.services`.

What stays in the consuming project:
- Mapping users to allowed sites.
- Any fallback/default assignment logic when no sites are selected.
- Project-specific `has_*_permission()` policy.
- Project-specific clone/import wiring beyond the provided binding helpers.

## Development & Testing

### Prerequisites

Install [Poetry](https://python-poetry.org/) for dependency management.

### Setup

```bash
# Install all dependencies (runtime + dev)
poetry install

# Run database migrations for the test server
poetry run python tests/server/manage.py migrate
```

### Running Tests

```bash
# Run the full pytest suite
poetry run pytest -q

# Run with verbose output
poetry run pytest -v

# Run a specific test file
poetry run pytest tests/test_smoke.py -v
```

### Manual Test Server

A local Django test server is included for visual inspection and manual testing.

```bash
# Apply migrations (creates tests/server/db.sqlite3)
poetry run python tests/server/manage.py migrate

# Create a superuser for admin login
poetry run python tests/server/manage.py createsuperuser

# Optionally seed a test form with sample fields
poetry run python tests/server/manage.py create_test_form

# Start the server
poetry run python tests/server/manage.py runserver 8080
```

Then open:
- Admin: http://localhost:8080/admin/
- Add form: http://localhost:8080/admin/unfold_fobi/formentryproxy/add/
- Edit form: http://localhost:8080/admin/unfold_fobi/formentryproxy/edit/1/ (after creating a form)

### Test Server Structure

```
tests/
├── conftest.py                 # Shared fixtures (admin_user, form_entry)
├── test_smoke.py               # Smoke tests (setup, URLs, views, seed data)
├── e2e/                        # Playwright browser tests (T04)
│   ├── conftest.py             # Browser fixtures (admin_login)
│   └── test_placeholder.py    # Scaffold placeholder
└── server/
    ├── manage.py               # Django management entry point
    ├── db.sqlite3              # SQLite DB (created by migrate, gitignored)
    └── testapp/
        ├── settings.py         # Full Unfold + Fobi + unfold_fobi config
        ├── urls.py             # Admin + Fobi + DRF URL wiring
        ├── wsgi.py
        └── asgi.py
```

## Notes

- `unfold_fobi.apps.UnfoldFobiConfig.ready()` automatically loads the DRF
  compatibility shim and re-registers Fobi admin classes with Unfold, so you
  do not need manual imports.
- The Unfold Fobi theme is registered as `uid="unfold"` in
  `unfold_fobi/fobi_themes.py`.
- If you are using DRF integration, ensure the `db_store` handler is enabled
  for a form so REST submissions are stored. New forms get it automatically,
  but existing ones may need the handler attached.