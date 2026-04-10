from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UnfoldFobiAltchaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "unfold_fobi.contrib.altcha"
    label = "unfold_fobi_altcha"
    verbose_name = _("ALTCHA protection")
