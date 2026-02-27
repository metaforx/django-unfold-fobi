"""
Custom admin configuration for django-fobi models using django-unfold.

This module unregisters all fobi admin classes and re-registers them
using django-unfold's ModelAdmin while preserving all existing functionality.
"""
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

# Import existing fobi admin classes
from fobi.admin import (
    FormEntryAdmin as FobiFormEntryAdmin,
    FormWizardEntryAdmin as FobiFormWizardEntryAdmin,
    FormFieldsetEntryAdmin as FobiFormFieldsetEntryAdmin,
    FormElementEntryAdmin as FobiFormElementEntryAdmin,
    FormHandlerEntryAdmin as FobiFormHandlerEntryAdmin,
    FormElementAdmin as FobiFormElementAdmin,
    FormHandlerAdmin as FobiFormHandlerAdmin,
    FormWizardHandlerAdmin as FobiFormWizardHandlerAdmin,
)

# Import fobi models
from fobi.models import (
    FormEntry,
    FormElementEntry,
    FormHandlerEntry,
    FormFieldsetEntry,
    FormWizardEntry,
    FormWizardFormEntry,
    FormWizardHandlerEntry,
    FormElement,
    FormHandler,
    FormWizardHandler,
)

# Import db_store models and admin classes
from fobi.contrib.plugins.form_handlers.db_store.models import (
    SavedFormDataEntry,
    SavedFormWizardDataEntry,
)
from fobi.contrib.plugins.form_handlers.db_store.admin import (
    SavedFormDataEntryAdmin as FobiSavedFormDataEntryAdmin,
    SavedFormWizardDataEntryAdmin as FobiSavedFormWizardDataEntryAdmin,
)

# Unregister all fobi models from admin
# This ensures we can re-register them with unfold ModelAdmin
_models_to_unregister = [
    FormEntry,
    FormElementEntry,
    FormHandlerEntry,
    FormFieldsetEntry,
    FormWizardEntry,
    FormWizardFormEntry,
    FormWizardHandlerEntry,
    FormElement,
    FormHandler,
    FormWizardHandler,
    SavedFormDataEntry,
    SavedFormWizardDataEntry,
]

for model in _models_to_unregister:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        # Model not registered yet, skip
        pass


# Update inline admins to use unfold's base classes
# Import fobi forms for inline admins
from fobi.forms import (
    FormElementEntryForm,
    FormHandlerEntryForm,
    FormWizardHandlerEntryForm,
)

# Create inline admins using unfold's base classes but with fobi's configuration
class FormElementEntryInlineAdmin(TabularInline):
    """FormElementEntry inline admin using django-unfold."""
    model = FormElementEntry
    form = FormElementEntryForm
    fields = (
        "form_entry",
        "plugin_uid",
        "plugin_data",
        "position",
    )
    extra = 0


class FormHandlerEntryInlineAdmin(TabularInline):
    """FormHandlerEntry inline admin using django-unfold."""
    model = FormHandlerEntry
    form = FormHandlerEntryForm
    fields = (
        "form_entry",
        "plugin_uid",
        "plugin_data",
    )
    extra = 0


class FormWizardFormEntryInlineAdmin(TabularInline):
    """FormWizardFormEntry inline admin using django-unfold."""
    model = FormWizardFormEntry
    fields = (
        "form_entry",
        "position",
    )
    extra = 0


class FormWizardHandlerEntryInlineAdmin(TabularInline):
    """FormWizardHandlerEntry inline admin using django-unfold."""
    model = FormWizardHandlerEntry
    form = FormWizardHandlerEntryForm
    fields = (
        "plugin_uid",
        "plugin_data",
    )
    extra = 0


# Re-register admin classes with unfold ModelAdmin base
# Update FormEntryAdmin to use our new inline classes
@admin.register(FormEntry)
class FormEntryAdmin(FobiFormEntryAdmin, ModelAdmin):
    """FormEntry admin using django-unfold."""
    inlines = [FormElementEntryInlineAdmin, FormHandlerEntryInlineAdmin]
    
    def get_urls(self):
        """Override URLs to link change view to custom edit view."""
        from django.urls import path
        from django.shortcuts import redirect
        
        urls = super().get_urls()
        
        # Replace the change view URL to point to custom edit view
        def redirect_to_edit(request, object_id):
            return redirect('fobi.edit_form_entry', form_entry_id=object_id)
        
        # Find and replace the change view
        change_url_name = '%s_%s_change' % (self.model._meta.app_label, self.model._meta.model_name)
        for i, url_pattern in enumerate(urls):
            if hasattr(url_pattern, 'name') and url_pattern.name == change_url_name:
                urls[i] = path(
                    '<path:object_id>/change/',
                    self.admin_site.admin_view(redirect_to_edit),
                    name=change_url_name,
                )
                break
        
        return urls
    
    def response_change(self, request, obj):
        """Override to redirect to custom edit view after save."""
        from django.shortcuts import redirect
        return redirect('fobi.edit_form_entry', form_entry_id=obj.pk)


@admin.register(FormWizardEntry)
class FormWizardEntryAdmin(FobiFormWizardEntryAdmin, ModelAdmin):
    """FormWizardEntry admin using django-unfold."""
    inlines = [FormWizardFormEntryInlineAdmin, FormWizardHandlerEntryInlineAdmin]


@admin.register(FormFieldsetEntry)
class FormFieldsetEntryAdmin(FobiFormFieldsetEntryAdmin, ModelAdmin):
    """FormFieldsetEntry admin using django-unfold."""
    pass


@admin.register(FormElementEntry)
class FormElementEntryAdmin(FobiFormElementEntryAdmin, ModelAdmin):
    """FormElementEntry admin using django-unfold."""
    pass


@admin.register(FormHandlerEntry)
class FormHandlerEntryAdmin(FobiFormHandlerEntryAdmin, ModelAdmin):
    """FormHandlerEntry admin using django-unfold."""
    pass


@admin.register(FormElement)
class FormElementAdmin(FobiFormElementAdmin, ModelAdmin):
    """FormElement admin using django-unfold."""
    pass


@admin.register(FormHandler)
class FormHandlerAdmin(FobiFormHandlerAdmin, ModelAdmin):
    """FormHandler admin using django-unfold."""
    pass


@admin.register(FormWizardHandler)
class FormWizardHandlerAdmin(FobiFormWizardHandlerAdmin, ModelAdmin):
    """FormWizardHandler admin using django-unfold."""
    pass


@admin.register(SavedFormDataEntry)
class SavedFormDataEntryAdmin(FobiSavedFormDataEntryAdmin, ModelAdmin):
    """SavedFormDataEntry admin using django-unfold.

    Non-superuser staff can view entries but cannot modify or delete them.
    Superusers retain full access.
    """

    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(SavedFormWizardDataEntry)
class SavedFormWizardDataEntryAdmin(FobiSavedFormWizardDataEntryAdmin, ModelAdmin):
    """SavedFormWizardDataEntry admin using django-unfold."""
    pass
