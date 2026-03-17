"""FormEntry model form variants used by Unfold admin."""

from django import forms


class FormEntryFormWithCloneable(forms.ModelForm):
    """Ensure is_cloneable is included and rendered in Unfold views."""

    class Meta:
        from fobi.forms import FormEntryForm as FobiFormEntryForm

        model = FobiFormEntryForm._meta.model
        fields = getattr(FobiFormEntryForm._meta, "fields", None) or "__all__"
        exclude = getattr(FobiFormEntryForm._meta, "exclude", None)

    def __init__(self, *args, **kwargs):
        kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
