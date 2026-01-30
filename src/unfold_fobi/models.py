from django.utils.translation import gettext_lazy as _
from fobi.models import FormEntry

class FormEntryProxy(FormEntry):
    class Meta:
        proxy = True
        verbose_name = _("Forms (builder)")
        verbose_name_plural = _("Forms (builder)")