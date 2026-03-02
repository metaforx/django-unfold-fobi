"""Widget mapping helpers for Unfold form integration."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout
from django import forms
from unfold.widgets import (
    UnfoldAdminCheckboxSelectMultiple,
    UnfoldAdminDateWidget,
    UnfoldAdminEmailInputWidget,
    UnfoldAdminFileFieldWidget,
    UnfoldAdminImageFieldWidget,
    UnfoldAdminIntegerFieldWidget,
    UnfoldAdminIntegerRangeWidget,
    UnfoldAdminNullBooleanSelectWidget,
    UnfoldAdminRadioSelectWidget,
    UnfoldAdminSelectMultipleWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminSplitDateTimeVerticalWidget,
    UnfoldAdminSplitDateTimeWidget,
    UnfoldAdminTextareaWidget,
    UnfoldAdminTextInputWidget,
    UnfoldAdminTimeWidget,
    UnfoldAdminURLInputWidget,
    UnfoldBooleanSwitchWidget,
)


class _SplitDateTimeStringValueMixin:
    """
    Ensure MultiWidget date/time inputs return a single string.

    Django's ``DateTimeField`` expects a string, but ``SplitDateTimeWidget`` and
    subclasses return a list. That causes ``DateTimeField.to_python`` to call
    ``strip`` on a list and explode. We join non-empty parts so the field
    receives the expected string value.
    """

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)

        if isinstance(value, (list, tuple)):
            non_empty = [part for part in value if part not in (None, "")]
            if not non_empty:
                return ""

            return " ".join(filter(None, value))

        return value


class UnfoldAdminSplitDateTimeWidgetCompat(
    _SplitDateTimeStringValueMixin, UnfoldAdminSplitDateTimeWidget
):
    """Unfold split datetime widget that returns a string for Django's DateTimeField."""


class UnfoldAdminSplitDateTimeVerticalWidgetCompat(
    _SplitDateTimeStringValueMixin, UnfoldAdminSplitDateTimeVerticalWidget
):
    """Vertical variant that also returns a string."""


def apply_unfold_widgets_to_form(form_instance):
    """
    Apply Unfold widgets to all fields in a form instance.

    This function maps Django field types to Unfold widgets:
    - CharField -> UnfoldAdminTextInputWidget
    - EmailField -> UnfoldAdminEmailInputWidget
    - URLField -> UnfoldAdminURLInputWidget
    - IntegerField, DecimalField, FloatField -> UnfoldAdminIntegerFieldWidget
    - DateField -> UnfoldAdminDateWidget
    - TimeField -> UnfoldAdminTimeWidget
    - DateTimeField -> UnfoldAdminSplitDateTimeWidget
    - FileField -> UnfoldAdminFileFieldWidget
    - ImageField -> UnfoldAdminImageFieldWidget
    - ChoiceField, ModelChoiceField -> UnfoldAdminSelectWidget
    - MultipleChoiceField, ModelMultipleChoiceField -> UnfoldAdminSelectMultipleWidget
    - RadioSelect -> UnfoldAdminRadioSelectWidget
    - BooleanField -> UnfoldBooleanSwitchWidget
    - PasswordInput, SearchInput, TelInput -> UnfoldAdminTextInputWidget
    - Textarea fields -> UnfoldAdminTextareaWidget

    This should be called in the form's __init__ method to ensure widgets
    are applied at instantiation time, not at class definition time.
    """

    def set_widget(field, widget_class):
        """Replace widget while preserving attrs/choices when possible."""
        old_widget = getattr(field, "widget", None)
        new_widget = widget_class() if isinstance(widget_class, type) else widget_class

        if old_widget and hasattr(old_widget, "attrs") and hasattr(new_widget, "attrs"):
            merged_attrs = dict(new_widget.attrs)
            old_attrs = old_widget.attrs or {}

            # Merge CSS classes rather than overwriting Unfold defaults
            new_classes = merged_attrs.get("class", "")
            old_classes = old_attrs.get("class", "")
            merged_classes = " ".join(filter(None, [new_classes, old_classes])).strip()

            merged_attrs.update(old_attrs)

            if isinstance(new_widget, forms.MultiWidget):
                # Avoid overriding per-input classes; push merged class to each subwidget
                class_to_merge = merged_classes
                merged_attrs.pop("class", None)
                for sub_widget in getattr(new_widget, "widgets", []):
                    sub_attrs = sub_widget.attrs or {}
                    sub_classes = sub_attrs.get("class", "")
                    combined = " ".join(
                        filter(None, [sub_classes, class_to_merge])
                    ).strip()
                    if combined:
                        sub_widget.attrs["class"] = combined
                new_widget.attrs = merged_attrs
            else:
                if merged_classes:
                    merged_attrs["class"] = merged_classes
                new_widget.attrs = merged_attrs

        if hasattr(new_widget, "choices"):
            if getattr(old_widget, "choices", None):
                new_widget.choices = old_widget.choices
            elif getattr(field, "choices", None):
                new_widget.choices = field.choices

        field.widget = new_widget

    widget_map = {
        forms.CharField: UnfoldAdminTextInputWidget,
        forms.EmailField: UnfoldAdminEmailInputWidget,
        forms.URLField: UnfoldAdminURLInputWidget,
        forms.IntegerField: UnfoldAdminIntegerFieldWidget,
        forms.DecimalField: UnfoldAdminIntegerFieldWidget,
        forms.FloatField: UnfoldAdminIntegerFieldWidget,
        forms.DateField: UnfoldAdminDateWidget,
        forms.TimeField: UnfoldAdminTimeWidget,
        forms.DateTimeField: UnfoldAdminSplitDateTimeWidgetCompat,
        forms.FileField: UnfoldAdminFileFieldWidget,
        forms.ImageField: UnfoldAdminImageFieldWidget,
        forms.ChoiceField: UnfoldAdminSelectWidget,
        forms.ModelChoiceField: UnfoldAdminSelectWidget,
        forms.MultipleChoiceField: UnfoldAdminSelectMultipleWidget,
        forms.ModelMultipleChoiceField: UnfoldAdminSelectMultipleWidget,
        forms.BooleanField: UnfoldBooleanSwitchWidget,
    }

    for _field_name, field in form_instance.fields.items():
        field_type = type(field)

        # Check if field is a Textarea
        if hasattr(field, "widget") and isinstance(field.widget, forms.Textarea):
            set_widget(field, UnfoldAdminTextareaWidget)
        # Map field types to Unfold widgets
        elif field_type in widget_map:
            set_widget(field, widget_map[field_type])
        # For fields with existing widgets, try to preserve widget attributes
        elif hasattr(field, "widget"):
            # Try to map based on widget type
            widget_type = type(field.widget)
            if widget_type == forms.TextInput:
                set_widget(field, UnfoldAdminTextInputWidget)
            elif widget_type == forms.Textarea:
                set_widget(field, UnfoldAdminTextareaWidget)
            elif widget_type == forms.EmailInput:
                set_widget(field, UnfoldAdminEmailInputWidget)
            elif widget_type == forms.URLInput:
                set_widget(field, UnfoldAdminURLInputWidget)
            elif widget_type == forms.PasswordInput:
                # PasswordInput uses TextInput styling
                set_widget(field, UnfoldAdminTextInputWidget)
            elif widget_type == forms.SearchInput:
                # SearchInput uses TextInput styling
                set_widget(field, UnfoldAdminTextInputWidget)
            elif widget_type == forms.TelInput:
                # TelInput uses TextInput styling
                set_widget(field, UnfoldAdminTextInputWidget)
            elif widget_type == forms.NumberInput:
                set_widget(field, UnfoldAdminIntegerFieldWidget)
            elif hasattr(forms, "RangeInput") and widget_type == forms.RangeInput:
                # RangeInput for numeric ranges (if available)
                try:
                    set_widget(field, UnfoldAdminIntegerRangeWidget)
                except (AttributeError, NameError):
                    # Fallback to IntegerFieldWidget if RangeInput not available
                    set_widget(field, UnfoldAdminIntegerFieldWidget)
            elif widget_type == forms.DateInput:
                set_widget(field, UnfoldAdminDateWidget)
            elif widget_type == forms.DateTimeInput:
                # Keep split widget styling but return a single string to the field
                set_widget(field, UnfoldAdminSplitDateTimeVerticalWidgetCompat)
            elif widget_type == forms.TimeInput:
                set_widget(field, UnfoldAdminTimeWidget)
            elif widget_type == forms.SplitDateTimeWidget:
                # Use vertical split for better mobile experience
                set_widget(field, UnfoldAdminSplitDateTimeVerticalWidgetCompat)
            elif widget_type == forms.Select:
                set_widget(field, UnfoldAdminSelectWidget)
            elif widget_type == forms.SelectMultiple:
                set_widget(field, UnfoldAdminSelectMultipleWidget)
            elif widget_type == forms.RadioSelect:
                # Keep RadioSelect as is - crispy forms will style it
                set_widget(field, UnfoldAdminRadioSelectWidget)
            elif widget_type == forms.CheckboxInput:
                set_widget(field, UnfoldBooleanSwitchWidget)
            elif widget_type == forms.FileInput:
                # Check if it's an ImageField by checking the field type
                if isinstance(field, forms.ImageField):
                    set_widget(field, UnfoldAdminImageFieldWidget)
                else:
                    set_widget(field, UnfoldAdminFileFieldWidget)
            elif widget_type == forms.ClearableFileInput:
                # ClearableFileInput for file fields that can be cleared
                if isinstance(field, forms.ImageField):
                    set_widget(field, UnfoldAdminImageFieldWidget)
                else:
                    set_widget(field, UnfoldAdminFileFieldWidget)
            elif widget_type == forms.CheckboxSelectMultiple:
                set_widget(field, UnfoldAdminCheckboxSelectMultiple)
            elif widget_type == forms.NullBooleanSelect:
                set_widget(field, UnfoldAdminNullBooleanSelectWidget)

    # Configure FormHelper for crispy forms if not already configured
    # This ensures crispy forms uses Unfold's fieldset template
    if not hasattr(form_instance, "helper"):
        form_instance.helper = FormHelper()
        form_instance.helper.template_pack = "unfold_crispy"
        # Create a layout with all fields in a fieldset
        # This ensures fieldsets are rendered using Unfold's fieldset template
        form_instance.helper.layout = Layout(
            Fieldset(
                None,  # No legend by default
                *form_instance.fields.keys(),
                css_class="aligned",  # Match Django admin's 'aligned' class
            )
        )

    return form_instance
