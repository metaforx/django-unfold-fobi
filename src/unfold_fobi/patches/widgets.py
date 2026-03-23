"""Apply Unfold widgets to all fobi form classes and plugin forms.

Patches fobi form classes, formsets, helpers, admin views, class-based
views, and base plugin methods so every form rendered through fobi gets
Unfold-styled widgets.
"""

from collections import OrderedDict

from django import forms


def _patch_form_init(form_class, apply_fn):
    """Monkey-patch a form class's __init__ to apply Unfold widgets."""
    if not form_class or hasattr(form_class, "_unfold_widgets_applied"):
        return False
    try:
        original_init = form_class.__init__

        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            apply_fn(self)

        form_class.__init__ = new_init
        form_class._unfold_widgets_applied = True
        return True
    except (AttributeError, TypeError):
        return False


def apply():
    """Patch all fobi form surfaces with Unfold widgets — idempotent."""
    from fobi import forms as fobi_forms
    from fobi import helpers as fobi_helpers

    from unfold_fobi.forms.widgets import apply_unfold_widgets_to_form

    # --- Static form classes ---
    form_classes_to_patch = [
        fobi_forms.FormEntryForm,
        fobi_forms.FormFieldsetEntryForm,
        fobi_forms.FormElementForm,
        fobi_forms.FormElementEntryForm,
        fobi_forms.FormHandlerForm,
        fobi_forms.FormHandlerEntryForm,
        fobi_forms.FormWizardFormEntryForm,
        fobi_forms.FormWizardEntryForm,
        fobi_forms.FormWizardHandlerEntryForm,
    ]
    for form_class in form_classes_to_patch:
        try:
            _patch_form_init(form_class, apply_unfold_widgets_to_form)
        except (AttributeError, TypeError, ImportError):
            pass

    # --- Formset inner forms ---
    try:
        from fobi.forms import (
            FormElementEntryFormSet,
            FormWizardFormEntryFormSet,
        )

        if hasattr(FormElementEntryFormSet, "form"):
            _patch_form_init(FormElementEntryFormSet.form, apply_unfold_widgets_to_form)
        if hasattr(FormWizardFormEntryFormSet, "form"):
            _patch_form_init(
                FormWizardFormEntryFormSet.form, apply_unfold_widgets_to_form
            )
    except (AttributeError, TypeError, ImportError):
        pass

    # --- fobi_helpers.get_form ---
    try:
        if hasattr(fobi_helpers, "get_form"):
            original_get_form = fobi_helpers.get_form

            def patched_get_form(form_entry, request=None):
                form = original_get_form(form_entry, request)
                if form:
                    apply_unfold_widgets_to_form(form)
                return form

            fobi_helpers.get_form = patched_get_form
    except (AttributeError, TypeError):
        pass

    # --- Plugin _get_form_field_instances ---
    try:
        from fobi import base as fobi_base

        def make_patched_get_form_field_instances(original_func):
            def patched(*args, **kwargs):
                form_field_instances = original_func(*args, **kwargs)
                if form_field_instances:
                    fields_dict = OrderedDict(form_field_instances)

                    class TempForm(forms.Form):
                        def __init__(self, fields_mapping):
                            super().__init__()
                            self.fields = fields_mapping

                    temp_form = TempForm(fields_dict)
                    apply_unfold_widgets_to_form(temp_form)
                    return list(fields_dict.items())
                return form_field_instances

            return patched

        for cls_name in ("FormElementPlugin", "FormFieldPlugin"):
            cls = getattr(fobi_base, cls_name, None)
            if cls and hasattr(cls, "_get_form_field_instances"):
                if not getattr(cls._get_form_field_instances, "_unfold_patched", False):
                    cls._get_form_field_instances = (
                        make_patched_get_form_field_instances(
                            cls._get_form_field_instances
                        )
                    )
                    cls._get_form_field_instances._unfold_patched = True
    except (AttributeError, TypeError, ImportError):
        pass

    # --- Fobi admin get_form ---
    try:
        from fobi import admin as fobi_admin_module

        for admin_cls_name in ("FormElementEntryAdmin", "FormHandlerEntryAdmin"):
            admin_cls = getattr(fobi_admin_module, admin_cls_name, None)
            if not admin_cls:
                continue
            original = admin_cls.get_form

            def _make_patched_admin_get_form(orig):
                def patched_get_form(self, request, obj=None, **kwargs):
                    form_class = orig(self, request, obj=obj, **kwargs)
                    if form_class:
                        _patch_form_init(form_class, apply_unfold_widgets_to_form)
                    return form_class

                return patched_get_form

            admin_cls.get_form = _make_patched_admin_get_form(original)
    except (AttributeError, TypeError, ImportError):
        pass

    # --- Fobi class-based edit/add views ---
    try:
        from fobi.views.class_based import edit as fobi_edit_views

        for view_name in ("EditFormElementEntryView", "AddFormElementEntryView"):
            view_cls = getattr(fobi_edit_views, view_name, None)
            if not view_cls:
                continue
            original = view_cls.get_form

            def _make_patched_view_get_form(orig):
                def patched_get_form(self, form_class=None):
                    form = orig(self, form_class=form_class)
                    if form:
                        apply_unfold_widgets_to_form(form)
                    return form

                return patched_get_form

            view_cls.get_form = _make_patched_view_get_form(original)
    except (AttributeError, TypeError, ImportError):
        pass

    # --- BasePlugin.get_form + initialised form helpers ---
    try:
        from fobi import base as fobi_base

        if hasattr(fobi_base, "BasePlugin"):
            original_plugin_get_form = fobi_base.BasePlugin.get_form

            def patched_plugin_get_form(self, *args, **kwargs):
                form = original_plugin_get_form(self, *args, **kwargs)
                if form:
                    if isinstance(form, type) and issubclass(form, forms.Form):
                        _patch_form_init(form, apply_unfold_widgets_to_form)
                    elif isinstance(form, forms.BaseForm):
                        apply_unfold_widgets_to_form(form)
                return form

            fobi_base.BasePlugin.get_form = patched_plugin_get_form

            for method_name in (
                "get_initialised_edit_form_or_404",
                "get_initialised_create_form_or_404",
            ):
                if hasattr(fobi_base.BasePlugin, method_name):
                    original = getattr(fobi_base.BasePlugin, method_name)

                    def _make_patched(orig):
                        def patched(self, *args, **kwargs):
                            form = orig(self, *args, **kwargs)
                            if form:
                                apply_unfold_widgets_to_form(form)
                            return form

                        return patched

                    setattr(
                        fobi_base.BasePlugin,
                        method_name,
                        _make_patched(original),
                    )
    except (AttributeError, TypeError, ImportError):
        pass
