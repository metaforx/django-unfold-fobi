# unfold_fobi

Unfold integration for `django-fobi`: Unfold-styled admin, Unfold theme for the
form builder UI, DRF compatibility shims, and a few Unfold-friendly admin views.

This README shows the integration steps as they are used in
`djangocms_test/settings.py` and `djangocms_test/urls.py`.

## Quick Start

1. Install dependencies.

```bash
pip install django-unfold django-fobi[simple] django-crispy-forms djangorestframework
```

2. Add apps to `INSTALLED_APPS` (order matters).

```python
INSTALLED_APPS = [
    "django.contrib.sites",
    "unfold",  # must be before django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Fobi integration
    "unfold_fobi",
    "fobi.contrib.themes.simple",  # required, Unfold theme extends it
    "fobi",

    # Standard Fobi plugins (for wizard interface)
    "fobi.contrib.plugins.form_elements.fields.text",
    "fobi.contrib.plugins.form_elements.fields.textarea",
    "fobi.contrib.plugins.form_elements.fields.email",
    "fobi.contrib.plugins.form_elements.fields.integer",
    "fobi.contrib.plugins.form_elements.fields.boolean",
    "fobi.contrib.plugins.form_elements.fields.date",
    "fobi.contrib.plugins.form_elements.fields.select",
    "fobi.contrib.plugins.form_handlers.db_store",

    # DRF integration (optional, but used in this project)
    "fobi.contrib.apps.drf_integration",
    "fobi.contrib.apps.drf_integration.form_elements.fields.text",
    "fobi.contrib.apps.drf_integration.form_elements.fields.email",
    "fobi.contrib.apps.drf_integration.form_elements.fields.integer",
    "fobi.contrib.apps.drf_integration.form_elements.fields.boolean",
    "fobi.contrib.apps.drf_integration.form_elements.fields.textarea",
    "fobi.contrib.apps.drf_integration.form_elements.fields.date",
    "fobi.contrib.apps.drf_integration.form_elements.fields.select",
    "fobi.contrib.apps.drf_integration.form_handlers.db_store",
]
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
from django.urls import path, include, re_path
from django.views.generic import RedirectView
import unfold_fobi.views

urlpatterns = [
    # DRF integration endpoints (optional)
    path("api/", include("fobi.contrib.apps.drf_integration.urls")),
    path(
        "api/fobi-form-fields/<str:slug>/",
        unfold_fobi.views.get_form_fields,
        name="fobi-form-fields",
    ),

    # Public Fobi views and handlers
    re_path(r"^fobi/", include("fobi.urls.class_based.view")),
    re_path(r"^admin/fobi/", include("fobi.urls.class_based.edit")),
    re_path(r"^fobi/", include("fobi.contrib.plugins.form_handlers.db_store.urls")),

    # Redirect legacy Fobi admin routes to the Unfold admin views
    path(
        "admin/fobi/forms/create/",
        RedirectView.as_view(pattern_name="admin:unfold_fobi_formentryproxy_create"),
        name="fobi.create_form_entry",
    ),
    path(
        "admin/fobi/forms/edit/<int:form_entry_id>/",
        RedirectView.as_view(pattern_name="admin:unfold_fobi_formentryproxy_edit"),
        name="fobi.edit_form_entry",
    ),
]
```

6. Run migrations.

```bash
python manage.py migrate
```

## Optional: Unfold Sidebar Links

This is the "Forms" navigation block used in `djangocms_test/settings.py`.
It links to the `unfold_fobi` admin views.

```python
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
                                "admin:unfold_fobi_formentryproxy_edit",
                                "fobi.edit_form_entry",
                            }
                            or request.path.startswith("/admin/unfold_fobi/formentryproxy/")
                            or request.path.startswith("/admin/fobi/forms/")
                        ),
                    },
                    {
                        "title": _("Import Form"),
                        "icon": "upload",
                        "link": reverse_lazy("admin:unfold_fobi_formentryproxy_import"),
                        "active": lambda request: getattr(
                            getattr(request, "resolver_match", None), "view_name", ""
                        )
                        in {
                            "admin:unfold_fobi_formentryproxy_import",
                            "fobi.import_form_entry",
                        }
                        or request.path.startswith("/admin/fobi/forms/import/")
                        or request.path.startswith("/admin/unfold_fobi/formentryproxy/import/"),
                    },
                    {
                        "title": _("Wizards"),
                        "icon": "auto_awesome",
                        "link": reverse_lazy("admin:unfold_fobi_formentryproxy_wizards"),
                        "active": lambda request: getattr(
                            getattr(request, "resolver_match", None), "view_name", ""
                        )
                        in {
                            "admin:unfold_fobi_formentryproxy_wizards",
                            "fobi.form_wizards_dashboard",
                        }
                        or request.path.startswith("/admin/fobi/wizards/")
                        or request.path.startswith("/admin/unfold_fobi/formentryproxy/wizards/"),
                    },
                ],
            },
        ],
    },
}
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
