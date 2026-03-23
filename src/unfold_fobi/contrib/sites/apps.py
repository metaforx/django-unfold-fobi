from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UnfoldFobiSitesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "unfold_fobi.contrib.sites"
    label = "unfold_fobi_sites"
    verbose_name = _("Form site bindings")
