from fobi.models import FormEntry

class FormEntryProxy(FormEntry):
    class Meta:
        proxy = True
        verbose_name = "Forms (builder)"
        verbose_name_plural = "Forms (builder)"