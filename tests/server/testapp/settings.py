"""
Django settings for the unfold_fobi test server.

Used for:
- pytest-django automated tests
- Manual runserver for local development / visual inspection
"""

import os
from pathlib import Path

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from unfold_modal.utils import get_modal_scripts, get_modal_styles

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "test-secret-key-not-for-production"

DEBUG = True

ALLOWED_HOSTS = ["*"]

SITE_ID = 1

INSTALLED_APPS = [
    # Unfold must be before django.contrib.admin
    "unfold",
    "unfold_modal",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third-party
    "crispy_forms",
    "rest_framework",
    # Fobi integration
    "unfold_fobi",
    "unfold_fobi.contrib.sites",
    "fobi.contrib.themes.simple",
    "fobi",
    # Standard Fobi plugins (form builder elements)
    "fobi.contrib.plugins.form_elements.fields.boolean",
    "fobi.contrib.plugins.form_elements.fields.checkbox_select_multiple",
    "fobi.contrib.plugins.form_elements.fields.date",
    "fobi.contrib.plugins.form_elements.fields.date_drop_down",
    "fobi.contrib.plugins.form_elements.fields.datetime",
    "fobi.contrib.plugins.form_elements.fields.decimal",
    "fobi.contrib.plugins.form_elements.fields.email",
    "fobi.contrib.plugins.form_elements.fields.file",
    "fobi.contrib.plugins.form_elements.fields.float",
    "fobi.contrib.plugins.form_elements.fields.hidden",
    "fobi.contrib.plugins.form_elements.fields.integer",
    "fobi.contrib.plugins.form_elements.fields.ip_address",
    "fobi.contrib.plugins.form_elements.fields.null_boolean",
    "fobi.contrib.plugins.form_elements.fields.password",
    "fobi.contrib.plugins.form_elements.fields.radio",
    "fobi.contrib.plugins.form_elements.fields.regex",
    "fobi.contrib.plugins.form_elements.fields.select",
    "fobi.contrib.plugins.form_elements.fields.select_multiple",
    "fobi.contrib.plugins.form_elements.fields.slug",
    "fobi.contrib.plugins.form_elements.fields.text",
    "fobi.contrib.plugins.form_elements.fields.textarea",
    "fobi.contrib.plugins.form_elements.fields.time",
    "fobi.contrib.plugins.form_elements.fields.url",
    "fobi.contrib.plugins.form_handlers.db_store",
    "fobi.contrib.plugins.form_handlers.mail",
    # DRF integration (optional, mirrors production usage)
    "fobi.contrib.apps.drf_integration",
    "fobi.contrib.apps.drf_integration.form_elements.fields.boolean",
    "fobi.contrib.apps.drf_integration.form_elements.fields.checkbox_select_multiple",
    "fobi.contrib.apps.drf_integration.form_elements.fields.date",
    "fobi.contrib.apps.drf_integration.form_elements.fields.date_drop_down",
    "fobi.contrib.apps.drf_integration.form_elements.fields.datetime",
    "fobi.contrib.apps.drf_integration.form_elements.fields.decimal",
    "fobi.contrib.apps.drf_integration.form_elements.fields.email",
    "fobi.contrib.apps.drf_integration.form_elements.fields.file",
    "fobi.contrib.apps.drf_integration.form_elements.fields.float",
    "fobi.contrib.apps.drf_integration.form_elements.fields.hidden",
    "fobi.contrib.apps.drf_integration.form_elements.fields.integer",
    "fobi.contrib.apps.drf_integration.form_elements.fields.ip_address",
    "fobi.contrib.apps.drf_integration.form_elements.fields.null_boolean",
    "fobi.contrib.apps.drf_integration.form_elements.fields.password",
    "fobi.contrib.apps.drf_integration.form_elements.fields.radio",
    "fobi.contrib.apps.drf_integration.form_elements.fields.regex",
    "fobi.contrib.apps.drf_integration.form_elements.fields.select",
    "fobi.contrib.apps.drf_integration.form_elements.fields.select_multiple",
    "fobi.contrib.apps.drf_integration.form_elements.fields.slug",
    "fobi.contrib.apps.drf_integration.form_elements.fields.text",
    "fobi.contrib.apps.drf_integration.form_elements.fields.textarea",
    "fobi.contrib.apps.drf_integration.form_elements.fields.time",
    "fobi.contrib.apps.drf_integration.form_elements.fields.url",
    "fobi.contrib.apps.drf_integration.form_handlers.db_store",
    "fobi.contrib.apps.drf_integration.form_handlers.mail",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "testapp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "fobi.context_processors.theme",
                "unfold_fobi.context_processors.admin_site",
            ],
            "builtins": [
                "unfold_fobi.templatetags.unfold_fobi_tags",
            ],
        },
    },
]

WSGI_APPLICATION = "testapp.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# For automated tests, use an in-memory database for speed
if os.environ.get("TESTING"):
    DATABASES["default"]["NAME"] = ":memory:"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", _("English")),
    ("de", _("German")),
]
LOCALE_PATHS = [
    Path(__file__).resolve().parent.parent.parent.parent
    / "src"
    / "unfold_fobi"
    / "locale",
]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Allow same-origin iframe embedding (required for django-unfold-modal)
X_FRAME_OPTIONS = "SAMEORIGIN"

# Email (console backend for testing — emails are printed to stdout)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "test@example.com"

# --- Fobi ---
FOBI_THEME = "unfold"
FOBI_DEFAULT_THEME = "unfold"

# --- Crispy Forms ---
CRISPY_TEMPLATE_PACK = "unfold_crispy"
CRISPY_ALLOWED_TEMPLATE_PACKS = ["unfold_crispy"]

# --- Unfold ---
UNFOLD = {
    "SITE_TITLE": "Unfold Fobi Test",
    "SITE_HEADER": "Unfold Fobi Test",
    "SHOW_LANGUAGES": True,
    "SIDEBAR": {
        "show_search": True,
        "command_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Forms"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("All Forms"),
                        "icon": "list",
                        "link": reverse_lazy(
                            "admin:unfold_fobi_formentryproxy_changelist"
                        ),
                    },
                ],
            },
        ],
    },
    "STYLES": [
        *get_modal_styles(),
    ],
    "SCRIPTS": [
        *get_modal_scripts(),
    ],
}
