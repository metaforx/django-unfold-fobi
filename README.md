# django-unfold-fobi

[![PyPI - Version](https://img.shields.io/pypi/v/django-unfold-fobi.svg?style=for-the-badge)](https://pypi.org/project/django-unfold-fobi/)
[![Build](https://img.shields.io/github/actions/workflow/status/metaforx/django-unfold-fobi/ci.yml?style=for-the-badge&event=pull_request)](https://github.com/metaforx/django-unfold-fobi/actions/workflows/ci.yml)

## Introduction

`django-unfold-fobi` integrates [django-fobi](https://github.com/barseghyanartur/django-fobi)
into [django-unfold](https://github.com/unfoldadmin/django-unfold).
It provides an Unfold-native admin experience for managing Fobi forms, plus a
small compatibility and patch layer for modern Django/DRF stacks.

## Intention

This package is an integration layer, not a replacement for standalone Fobi
usage. You can still use standard Fobi public forms and existing plugins; this
project focuses on making the admin and integration surface fit naturally into
Unfold-based back offices.

## Features

- Unfold-native admin integration for Fobi form management.
- Unfold widget styling applied across Fobi admin/plugin form surfaces.
- DRF-oriented improvements for Fobi API submissions and handler behavior.
- Admin workflow enhancements (import/clone/popup behavior, staff editing).
- Optional Sites extension (`unfold_fobi.contrib.sites`) for site-scoped forms,
  queryset scoping, and reusable admin mixins.
- Optional django CMS plugin (`unfold_fobi.contrib.cms`) for embedding forms in
  CMS placeholders, with site-aware form selection.
- Optional ALTCHA protection (`unfold_fobi.contrib.altcha`) for proof-of-work
  anti-bot verification on public form submissions.
- Fobi AppConfig overrides with `AutoField` pinning and i18n `verbose_name`
  labels for projects using `BigAutoField`.

## Requirements

- Python `>=3.10,<4.0`
- Django `>=5.0`
- django-unfold `>=0.80.0`
- django-fobi `>=0.19`
- django-crispy-forms `>=2.0`
- djangorestframework `>=3.14`
- django-unfold-modal `>=0.1.0`

## Patches & Compatibility

`unfold_fobi` applies a few startup patches to keep Fobi integration stable on
newer dependency versions:

- DRF compatibility shim restores `rest_framework.fields.set_value` for DRF
  3.15+ where Fobi still expects it.
- DRF `db_store` improvements include active-date enforcement and safer
  integration behavior.
- Admin patches align popup/modal responses with Unfold workflows.
- Additional Fobi patches improve widget consistency, staff editing behavior,
  and mail sender handler field handling.

## Limitations

- Main focus is DRF + admin integration; this package does not try to redesign
  every standalone Fobi rendering path.
- For REST-based usage, you need to implement your own frontend form rendering
  using the API metadata returned for each form.
- Non-Unfold form rendering should still work, but may not be styled like
  Unfold unless your project applies matching templates/styles.
- Form wizards are currently linked/redirected, but not fully covered as a
  first-class Unfold-integrated workflow.

## Quickstart

Install and enable the integration with minimum settings.

1. Install package:

```bash
pip install django-unfold-fobi
```

2. Add apps (order matters):

```python
INSTALLED_APPS = [
    "unfold",  # must be before django.contrib.admin
    "crispy_forms",
    "fobi.contrib.themes.simple",
    "unfold_fobi",
    # If using DEFAULT_AUTO_FIELD = "BigAutoField", use these instead of
    # bare "fobi" and "fobi.contrib.plugins.form_handlers.db_store":
    "unfold_fobi.fobi_app_configs.FobiConfig",
    "unfold_fobi.fobi_app_configs.FobiDbStoreConfig",
]
```

3. Add required template hooks:

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

4. Enable theme settings:

```python
FOBI_THEME = "unfold"
FOBI_DEFAULT_THEME = "unfold"

CRISPY_TEMPLATE_PACK = "unfold_crispy"
CRISPY_ALLOWED_TEMPLATE_PACKS = ["unfold_crispy"]
```

5. Add URLs (keep `admin/fobi/` before `admin.site.urls`):

```python
from django.urls import include, path

urlpatterns = [
    path("api/", include("fobi.contrib.apps.drf_integration.urls")),
    path("api/", include("unfold_fobi.api.urls")),
    path("fobi/", include("unfold_fobi.urls.public")),
    path("admin/fobi/", include("unfold_fobi.urls.admin")),
]
```

6. Run migrations:

```bash
python manage.py migrate
```

## Comprehensive Installation Guide

Use this when you need the full integration, including optional Sites support.

### 1) Install and baseline setup

- Follow standard `django-fobi` installation first (plugins, handlers, base
  settings).
- Then add `unfold_fobi` and the Quickstart settings from above.

### 2) Optional Sites integration

Enable only if your project needs form-to-site bindings.

```python
INSTALLED_APPS += [
    "django.contrib.sites",
    "unfold_fobi.contrib.sites",
]

SITE_ID = 1
UNFOLD_FOBI_SITES_FOR_USER = "myproject.site_permissions.sites_for_user"
```

Then re-register your form admins with the mixins from
`unfold_fobi.contrib.sites.admin`:

- `SiteAwareFormEntryMixin`
- `RelationSiteScopeAdminMixin`

These provide site assignment UI, queryset scoping, and reusable
site-scoped permission helpers. Your project still owns user-to-site policy and
project-specific permission decisions.

### 3) Optional django CMS plugin

Enable only if your project uses django CMS and wants to embed Fobi forms in
CMS placeholders.

Requires `django-unfold-extra>=0.2.1`.

```python
INSTALLED_APPS += [
    "unfold_fobi.contrib.cms",
]
```

Then run migrations:

```bash
python manage.py migrate
```

The plugin appears as "Form" (module "Forms") in the CMS plugin picker. It
renders the selected form using fobi's standard form rendering.

When `unfold_fobi.contrib.sites` is also enabled, the form selection dropdown
is automatically filtered by the current site and the editor's allowed sites.

If `djangocms-rest` is installed, the plugin serializes the form reference as
`{"form_entry": {"name": "...", "slug": "..."}}` instead of a bare FK integer.

### 4) Optional ALTCHA protection

Enable to require proof-of-work verification on public form submissions.
Only public forms (`is_public=True`) are protected; non-public/preview forms
are unaffected.

Requires the `altcha` Python package (`>=2.0`).

```bash
pip install altcha
```

```python
INSTALLED_APPS += [
    "unfold_fobi.contrib.altcha",
]

UNFOLD_FOBI_ALTCHA_HMAC_SECRET = "your-secret-key"  # required to enable
```

Add the challenge endpoint URL:

```python
urlpatterns += [
    path("api/", include("unfold_fobi.contrib.altcha.urls")),
]
```

Optional settings:

```python
UNFOLD_FOBI_ALTCHA_MAX_NUMBER = 100_000       # difficulty (default: 100000)
UNFOLD_FOBI_ALTCHA_ALGORITHM = "SHA-256"      # hash algorithm
UNFOLD_FOBI_ALTCHA_FIELD_NAME = "altcha"      # payload field name in PUT body
UNFOLD_FOBI_ALTCHA_CACHE_ALIAS = "default"    # cache backend for replay protection
UNFOLD_FOBI_ALTCHA_CHALLENGE_EXPIRY = 300     # challenge TTL in seconds
```

**How it works:**

1. `GET /api/fobi-form-fields/<slug>/` includes an `AltchaField` entry for
   public forms when ALTCHA is enabled.
2. Frontend fetches a challenge from `GET /api/altcha-challenge/`.
3. Frontend solves the challenge client-side (e.g. using the `altcha` web
   component) and includes the base64 payload as `"altcha"` in the PUT body.
4. Backend verifies the payload before processing the form submission.
   Missing, invalid, expired, or replayed payloads return `400`.

### 5) DRF notes

- Include both Fobi DRF URLs and `unfold_fobi.api.urls`.
- Use `GET /api/fobi-form-fields/<slug>/` to fetch per-form field metadata
  (including available field types/widgets/choices) for frontend rendering.
- Ensure each form has the `db_store` handler enabled for persisted API
  submissions.

### 6) Fobi AppConfig overrides (recommended for BigAutoField projects)

If your project uses `DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"`,
replace the bare fobi entries in `INSTALLED_APPS` with the package-provided
configs. These pin `AutoField` (fobi lacks a BigAutoField migration) and add
translatable `verbose_name` labels.

```python
INSTALLED_APPS = [
    # Replace "fobi" with:
    "unfold_fobi.fobi_app_configs.FobiConfig",
    # Replace "fobi.contrib.plugins.form_handlers.db_store" with:
    "unfold_fobi.fobi_app_configs.FobiDbStoreConfig",
]
```

## Notes

- `unfold_fobi.apps.UnfoldFobiConfig.ready()` runs during Django app startup
  and performs integration bootstrap in this order:
  DRF compatibility shim, Fobi admin re-registration for Unfold,
  monkey-patches, and signal registration.
- If you want explicit app config wiring, use this in `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "unfold_fobi.apps.UnfoldFobiConfig",
]
```

- Startup signals auto-attach a `db_store` handler to saved forms and
  deduplicate duplicates created during JSON import.
- The Unfold theme for Fobi is registered as `uid="unfold"`.
