"""Form mixins for Unfold integration."""

from .widgets import apply_unfold_widgets_to_form


class UnfoldFormMixin:
    """
    Mixin to automatically apply Unfold widgets to form fields.

    Usage:
        class MyForm(UnfoldFormMixin, forms.Form):
            name = forms.CharField()
            email = forms.EmailField()
    """

    def __init__(self, *args, **kwargs):
        kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        # Apply Unfold widgets to all fields at instantiation time
        apply_unfold_widgets_to_form(self)
