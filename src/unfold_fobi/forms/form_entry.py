"""FormEntry model form variants used by Unfold admin."""

from django import forms

from .layout import align_visibility_fields_in_layout
from .widgets import apply_unfold_widgets_to_form


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

        # if "is_cloneable" not in self.fields:
        #     field = self._meta.model._meta.get_field("is_cloneable")
        #     self.fields["is_cloneable"] = field.formfield()

        #apply_unfold_widgets_to_form(self)
        #align_visibility_fields_in_layout(self)
