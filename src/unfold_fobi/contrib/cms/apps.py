from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UnfoldFobiCmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "unfold_fobi.contrib.cms"
    label = "unfold_fobi_cms"
    verbose_name = _("Fobi CMS integration")
