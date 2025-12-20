from django.apps import AppConfig
from django import forms
from collections import OrderedDict


class UnfoldFobiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'unfold_fobi'
    
    def ready(self):
        """
        Apply Unfold widgets to fobi forms when the app is ready.
        
        Instead of patching __init__, we use a cleaner approach:
        Monkey-patch the form classes to add widget application in their __init__
        using a mixin pattern that doesn't break super() calls.
        
        Also patches fobi's dynamic form creation to apply Unfold widgets.
        """
        # Import fobi compatibility patch first (must be before any fobi imports)
        from unfold_fobi import fobi_compat  # noqa
        
        # Import fobi admin to register admin classes with Unfold
        from unfold_fobi import fobi_admin  # noqa
        
        # Import here to avoid circular imports
        from unfold_fobi import forms as unfold_forms
        from fobi import forms as fobi_forms
        from fobi import helpers as fobi_helpers
        
        # Store original __init__ methods and create patched versions
        # Cover all fobi forms as per https://github.com/barseghyanartur/django-fobi/blob/main/src/fobi/forms.py
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
            # Formset forms (these are created via modelformset_factory, but we can try to patch them)
            # Note: _FormElementEntryForm and _FormWizardFormEntryForm are private and used in formsets
            # They will be covered when we patch the formset factory
        ]
        
        # Also patch formsets - these create forms dynamically
        try:
            from fobi.forms import (
                FormElementEntryFormSet,
                FormWizardFormEntryFormSet,
            )
            from django.forms.models import BaseModelFormSet
            
            # Patch FormElementEntryFormSet
            if hasattr(FormElementEntryFormSet, 'form'):
                original_form_class = FormElementEntryFormSet.form
                if original_form_class and not hasattr(original_form_class, '_unfold_widgets_applied'):
                    original_init = original_form_class.__init__
                    
                    def make_new_init(orig_init):
                        def new_init(self, *args, **kwargs):
                            orig_init(self, *args, **kwargs)
                            unfold_forms.apply_unfold_widgets_to_form(self)
                        return new_init
                    
                    original_form_class.__init__ = make_new_init(original_init)
                    original_form_class._unfold_widgets_applied = True
            
            # Patch FormWizardFormEntryFormSet
            if hasattr(FormWizardFormEntryFormSet, 'form'):
                original_form_class = FormWizardFormEntryFormSet.form
                if original_form_class and not hasattr(original_form_class, '_unfold_widgets_applied'):
                    original_init = original_form_class.__init__
                    
                    def make_new_init(orig_init):
                        def new_init(self, *args, **kwargs):
                            orig_init(self, *args, **kwargs)
                            unfold_forms.apply_unfold_widgets_to_form(self)
                        return new_init
                    
                    original_form_class.__init__ = make_new_init(original_init)
                    original_form_class._unfold_widgets_applied = True
        except (AttributeError, TypeError, ImportError):
            # Formset classes might not exist or have different structure
            pass
        
        for form_class in form_classes_to_patch:
            try:
                # Only patch if not already patched
                if not hasattr(form_class, '_unfold_widgets_applied'):
                    # Store the original __init__ - capture it in closure with default arg
                    original_init = form_class.__init__
                    
                    # Create a new __init__ that calls the original and then applies widgets
                    # Use default argument to capture original_init in closure
                    def make_new_init(orig_init):
                        def new_init(self, *args, **kwargs):
                            # Call the original __init__ - this preserves all super() calls
                            orig_init(self, *args, **kwargs)
                            # Apply Unfold widgets after form is fully initialized
                            unfold_forms.apply_unfold_widgets_to_form(self)
                        return new_init
                    
                    # Bind the new method to the class
                    form_class.__init__ = make_new_init(original_init)
                    form_class._unfold_widgets_applied = True
            except (AttributeError, TypeError, ImportError) as e:
                # Form class might not exist or have different structure
                # Silently skip if we can't patch it
                pass
        
        # Patch fobi's get_form function to apply Unfold widgets to dynamic forms
        try:
            if hasattr(fobi_helpers, 'get_form'):
                original_get_form = fobi_helpers.get_form
                
                def patched_get_form(form_entry, request=None):
                    """Patched get_form that applies Unfold widgets to dynamic forms."""
                    form = original_get_form(form_entry, request)
                    if form:
                        # Apply Unfold widgets to the dynamically created form
                        unfold_forms.apply_unfold_widgets_to_form(form)
                    return form
                
                fobi_helpers.get_form = patched_get_form
        except (AttributeError, TypeError):
            # get_form might not exist or have different signature
            pass
        
        # Patch fobi's FormElementPlugin/FormFieldPlugin _get_form_field_instances
        # so dynamically assembled forms get Unfold widgets (incl. switches)
        try:
            from fobi import base as fobi_base

            def make_patched_get_form_field_instances(original_func):
                def patched_get_form_field_instances(*args, **kwargs):
                    """Patched _get_form_field_instances that applies Unfold widgets to form fields."""
                    form_field_instances = original_func(*args, **kwargs)
                    if form_field_instances:
                        # Preserve order while mapping tuples to a fields dict
                        fields_dict = OrderedDict(form_field_instances)

                        class TempForm(forms.Form):
                            def __init__(self, fields_mapping):
                                super().__init__()
                                self.fields = fields_mapping

                        temp_form = TempForm(fields_dict)
                        unfold_forms.apply_unfold_widgets_to_form(temp_form)
                        # Rebuild list of tuples with updated widgets
                        return list(fields_dict.items())
                    return form_field_instances

                return patched_get_form_field_instances

            for cls_name in ("FormElementPlugin", "FormFieldPlugin"):
                cls = getattr(fobi_base, cls_name, None)
                if cls and hasattr(cls, "_get_form_field_instances"):
                    original = cls._get_form_field_instances
                    if not getattr(cls._get_form_field_instances, "_unfold_patched", False):
                        cls._get_form_field_instances = make_patched_get_form_field_instances(original)
                        cls._get_form_field_instances._unfold_patched = True
        except (AttributeError, TypeError, ImportError):
            # _get_form_field_instances might not exist or have different signature
            pass
        
        # Patch fobi admin views to apply Unfold widgets to forms created in edit/add views
        # These views create forms dynamically for editing/adding form elements
        try:
            from fobi import admin as fobi_admin
            
            # Patch FormElementEntryAdmin's get_form method
            # get_form returns a form class, not an instance, so we patch the class
            if hasattr(fobi_admin, 'FormElementEntryAdmin'):
                original_get_form = fobi_admin.FormElementEntryAdmin.get_form
                
                def patched_get_form(self, request, obj=None, **kwargs):
                    """Patched get_form that applies Unfold widgets to form element entry forms."""
                    form_class = original_get_form(self, request, obj=obj, **kwargs)
                    if form_class and not hasattr(form_class, '_unfold_widgets_applied'):
                        # Patch the form class's __init__ to apply widgets
                        original_init = form_class.__init__
                        
                        def make_new_init(orig_init):
                            def new_init(self, *args, **kwargs):
                                orig_init(self, *args, **kwargs)
                                unfold_forms.apply_unfold_widgets_to_form(self)
                            return new_init
                        
                        form_class.__init__ = make_new_init(original_init)
                        form_class._unfold_widgets_applied = True
                    return form_class
                
                fobi_admin.FormElementEntryAdmin.get_form = patched_get_form
            
            # Patch FormHandlerEntryAdmin's get_form method
            if hasattr(fobi_admin, 'FormHandlerEntryAdmin'):
                original_get_form = fobi_admin.FormHandlerEntryAdmin.get_form
                
                def patched_get_form(self, request, obj=None, **kwargs):
                    """Patched get_form that applies Unfold widgets to form handler entry forms."""
                    form_class = original_get_form(self, request, obj=obj, **kwargs)
                    if form_class and not hasattr(form_class, '_unfold_widgets_applied'):
                        # Patch the form class's __init__ to apply widgets
                        original_init = form_class.__init__
                        
                        def make_new_init(orig_init):
                            def new_init(self, *args, **kwargs):
                                orig_init(self, *args, **kwargs)
                                unfold_forms.apply_unfold_widgets_to_form(self)
                            return new_init
                        
                        form_class.__init__ = make_new_init(original_init)
                        form_class._unfold_widgets_applied = True
                    return form_class
                
                fobi_admin.FormHandlerEntryAdmin.get_form = patched_get_form
        except (AttributeError, TypeError, ImportError):
            # Admin classes might not exist or have different structure
            pass
        
        # Patch fobi's class-based views to apply Unfold widgets to forms
        # These are used for /admin/fobi/forms/elements/edit/ and /admin/fobi/forms/elements/add/
        try:
            from fobi.views.class_based import edit as fobi_edit_views
            
            # Patch EditFormElementEntryView
            if hasattr(fobi_edit_views, 'EditFormElementEntryView'):
                original_get_form = fobi_edit_views.EditFormElementEntryView.get_form
                
                def patched_get_form(self, form_class=None):
                    """Patched get_form that applies Unfold widgets to form element entry forms."""
                    form = original_get_form(self, form_class=form_class)
                    if form:
                        unfold_forms.apply_unfold_widgets_to_form(form)
                    return form
                
                fobi_edit_views.EditFormElementEntryView.get_form = patched_get_form
            
            # Patch AddFormElementEntryView
            if hasattr(fobi_edit_views, 'AddFormElementEntryView'):
                original_get_form = fobi_edit_views.AddFormElementEntryView.get_form
                
                def patched_get_form(self, form_class=None):
                    """Patched get_form that applies Unfold widgets to form element entry forms."""
                    form = original_get_form(self, form_class=form_class)
                    if form:
                        unfold_forms.apply_unfold_widgets_to_form(form)
                    return form
                
                fobi_edit_views.AddFormElementEntryView.get_form = patched_get_form
        except (AttributeError, TypeError, ImportError):
            # View classes might not exist or have different structure
            pass
        
        # Patch fobi's base plugin class to apply Unfold widgets when plugins create forms
        # This is the most comprehensive approach - plugins create forms via get_form method
        # and then instantiate them via get_initialised_edit_form_or_404, get_initialised_create_form_or_404, etc.
        try:
            from fobi import base as fobi_base
            
            # Patch BasePlugin's get_form method
            if hasattr(fobi_base, 'BasePlugin'):
                original_plugin_get_form = fobi_base.BasePlugin.get_form
                
                def patched_plugin_get_form(self, *args, **kwargs):
                    """Patched get_form that applies Unfold widgets to plugin forms."""
                    # Call original with whatever arguments it expects (no request parameter)
                    form = original_plugin_get_form(self, *args, **kwargs)
                    if form:
                        # If form is a class, we need to patch its __init__
                        if isinstance(form, type) and issubclass(form, forms.Form):
                            if not hasattr(form, '_unfold_widgets_applied'):
                                original_init = form.__init__
                                
                                def make_new_init(orig_init):
                                    def new_init(self, *args, **kwargs):
                                        orig_init(self, *args, **kwargs)
                                        unfold_forms.apply_unfold_widgets_to_form(self)
                                    return new_init
                                
                                form.__init__ = make_new_init(original_init)
                                form._unfold_widgets_applied = True
                        # If form is an instance, apply widgets directly
                        elif isinstance(form, forms.BaseForm):
                            unfold_forms.apply_unfold_widgets_to_form(form)
                    return form
                
                fobi_base.BasePlugin.get_form = patched_plugin_get_form
                
                # Also patch methods that instantiate forms
                if hasattr(fobi_base.BasePlugin, 'get_initialised_edit_form_or_404'):
                    original_get_initialised_edit = fobi_base.BasePlugin.get_initialised_edit_form_or_404
                    
                    def patched_get_initialised_edit(self, *args, **kwargs):
                        """Patched get_initialised_edit_form_or_404 that applies Unfold widgets."""
                        form = original_get_initialised_edit(self, *args, **kwargs)
                        if form:
                            unfold_forms.apply_unfold_widgets_to_form(form)
                        return form
                    
                    fobi_base.BasePlugin.get_initialised_edit_form_or_404 = patched_get_initialised_edit
                
                if hasattr(fobi_base.BasePlugin, 'get_initialised_create_form_or_404'):
                    original_get_initialised_create = fobi_base.BasePlugin.get_initialised_create_form_or_404
                    
                    def patched_get_initialised_create(self, *args, **kwargs):
                        """Patched get_initialised_create_form_or_404 that applies Unfold widgets."""
                        form = original_get_initialised_create(self, *args, **kwargs)
                        if form:
                            unfold_forms.apply_unfold_widgets_to_form(form)
                        return form
                    
                    fobi_base.BasePlugin.get_initialised_create_form_or_404 = patched_get_initialised_create
        except (AttributeError, TypeError, ImportError):
            # BasePlugin might not exist or have different structure
            pass
