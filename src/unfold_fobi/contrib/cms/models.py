from cms.models import CMSPlugin
from django.db import models
from django.utils.translation import gettext_lazy as _


class FobiFormPluginModel(CMSPlugin):
    """CMS plugin that references a Fobi form entry."""

    form_entry = models.ForeignKey(
        "fobi.FormEntry",
        verbose_name=_("Form"),
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = _("Fobi form plugin")
        verbose_name_plural = _("Fobi form plugins")

    def __str__(self):
        return self.form_entry.name if self.form_entry_id else ""
