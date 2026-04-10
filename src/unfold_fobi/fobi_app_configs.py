"""Custom AppConfigs for django-fobi with AutoField pinning and i18n labels.

django-fobi ships with AutoField PKs and no BigAutoField migration. When a
project uses ``DEFAULT_AUTO_FIELD = "BigAutoField"``, Django detects phantom
migration changes. These configs pin the original AutoField and add
translatable verbose names.

Usage in INSTALLED_APPS (replace the bare fobi entries)::

    INSTALLED_APPS = [
        # ...
        "unfold_fobi.fobi_app_configs.FobiConfig",                # replaces "fobi"
        "unfold_fobi.fobi_app_configs.FobiDbStoreConfig",         # replaces "fobi.contrib.plugins.form_handlers.db_store"
        # ...
    ]
"""

from django.utils.translation import gettext_lazy as _
from fobi.apps import Config as _FobiConfig
from fobi.contrib.plugins.form_handlers.db_store.apps import (
    Config as _FobiDbStoreConfig,
)


class FobiConfig(_FobiConfig):
    default_auto_field = "django.db.models.AutoField"
    verbose_name = _("Forms")


class FobiDbStoreConfig(_FobiDbStoreConfig):
    default_auto_field = "django.db.models.AutoField"
    verbose_name = _("Form data")
