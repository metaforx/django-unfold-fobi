from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _

from unfold_fobi.models import FormEntryProxy


class FobiFormSiteBinding(models.Model):
    form_entry = models.OneToOneField(
        FormEntryProxy,
        on_delete=models.CASCADE,
        related_name="site_binding",
        verbose_name=_("Form"),
    )
    sites = models.ManyToManyField(
        Site,
        blank=True,
        related_name="fobi_form_bindings",
        verbose_name=_("Sites"),
    )

    class Meta:
        verbose_name = _("Form site binding")
        verbose_name_plural = _("Form site bindings")

    def __str__(self) -> str:
        return self.form_entry.name
