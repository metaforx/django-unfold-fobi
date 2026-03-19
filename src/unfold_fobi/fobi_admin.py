"""
Custom admin configuration for django-fobi models using django-unfold.

This module unregisters all fobi admin classes and re-registers them
using django-unfold's ModelAdmin while preserving all existing functionality.
"""

from django.contrib import admin
from fobi.admin import (
    FormElementAdmin as FobiFormElementAdmin,
)
from fobi.admin import (
    FormElementEntryAdmin as FobiFormElementEntryAdmin,
)

# Import existing fobi admin classes
from fobi.admin import (
    FormEntryAdmin as FobiFormEntryAdmin,
)
from fobi.admin import (
    FormFieldsetEntryAdmin as FobiFormFieldsetEntryAdmin,
)
from fobi.admin import (
    FormHandlerAdmin as FobiFormHandlerAdmin,
)
from fobi.admin import (
    FormHandlerEntryAdmin as FobiFormHandlerEntryAdmin,
)
from fobi.admin import (
    FormWizardEntryAdmin as FobiFormWizardEntryAdmin,
)
from fobi.admin import (
    FormWizardHandlerAdmin as FobiFormWizardHandlerAdmin,
)
from fobi.contrib.plugins.form_handlers.db_store.admin import (
    SavedFormDataEntryAdmin as FobiSavedFormDataEntryAdmin,
)
from fobi.contrib.plugins.form_handlers.db_store.admin import (
    SavedFormWizardDataEntryAdmin as FobiSavedFormWizardDataEntryAdmin,
)

# Import db_store models and admin classes
from fobi.contrib.plugins.form_handlers.db_store.models import (
    SavedFormDataEntry,
    SavedFormWizardDataEntry,
)
from fobi.forms import (
    FormElementEntryForm,
    FormHandlerEntryForm,
    FormWizardHandlerEntryForm,
)

# Import fobi models
from fobi.models import (
    FormElement,
    FormElementEntry,
    FormEntry,
    FormFieldsetEntry,
    FormHandler,
    FormHandlerEntry,
    FormWizardEntry,
    FormWizardFormEntry,
    FormWizardHandler,
    FormWizardHandlerEntry,
)
from unfold.admin import ModelAdmin, TabularInline

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


class ProxyOnlyFobiAdminMixin:
    """Hide raw fobi model admins and deny direct access.

    We keep these admin classes registered for compatibility with existing
    patches/imports, but builder users should work through FormEntryProxyAdmin.
    """

    def has_module_permission(self, request):
        return False

    def get_model_perms(self, request):
        return {}

    def has_view_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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
class FormEntryAdmin(ProxyOnlyFobiAdminMixin, FobiFormEntryAdmin, ModelAdmin):
    """FormEntry admin using django-unfold."""

    inlines = [FormElementEntryInlineAdmin, FormHandlerEntryInlineAdmin]

    def get_urls(self):
        """Override URLs to link change view to custom edit view."""
        from django.shortcuts import redirect
        from django.urls import path

        urls = super().get_urls()

        # Replace the change view URL to point to custom edit view
        def redirect_to_edit(request, object_id):
            return redirect("fobi.edit_form_entry", form_entry_id=object_id)

        # Find and replace the change view
        change_url_name = (
            f"{self.model._meta.app_label}_{self.model._meta.model_name}_change"
        )
        for i, url_pattern in enumerate(urls):
            if hasattr(url_pattern, "name") and url_pattern.name == change_url_name:
                urls[i] = path(
                    "<path:object_id>/change/",
                    self.admin_site.admin_view(redirect_to_edit),
                    name=change_url_name,
                )
                break

        return urls

    def response_change(self, request, obj):
        """Override to redirect to custom edit view after save."""
        from django.shortcuts import redirect

        return redirect("fobi.edit_form_entry", form_entry_id=obj.pk)


@admin.register(FormWizardEntry)
class FormWizardEntryAdmin(
    ProxyOnlyFobiAdminMixin, FobiFormWizardEntryAdmin, ModelAdmin
):
    """FormWizardEntry admin using django-unfold."""

    inlines = [FormWizardFormEntryInlineAdmin, FormWizardHandlerEntryInlineAdmin]


@admin.register(FormFieldsetEntry)
class FormFieldsetEntryAdmin(
    ProxyOnlyFobiAdminMixin, FobiFormFieldsetEntryAdmin, ModelAdmin
):
    """FormFieldsetEntry admin using django-unfold."""

    pass


@admin.register(FormElementEntry)
class FormElementEntryAdmin(
    ProxyOnlyFobiAdminMixin, FobiFormElementEntryAdmin, ModelAdmin
):
    """FormElementEntry admin using django-unfold."""

    pass


@admin.register(FormHandlerEntry)
class FormHandlerEntryAdmin(
    ProxyOnlyFobiAdminMixin, FobiFormHandlerEntryAdmin, ModelAdmin
):
    """FormHandlerEntry admin using django-unfold."""

    pass


@admin.register(FormElement)
class FormElementAdmin(ProxyOnlyFobiAdminMixin, FobiFormElementAdmin, ModelAdmin):
    """FormElement admin using django-unfold."""

    pass


@admin.register(FormHandler)
class FormHandlerAdmin(ProxyOnlyFobiAdminMixin, FobiFormHandlerAdmin, ModelAdmin):
    """FormHandler admin using django-unfold."""

    pass


@admin.register(FormWizardHandler)
class FormWizardHandlerAdmin(
    ProxyOnlyFobiAdminMixin, FobiFormWizardHandlerAdmin, ModelAdmin
):
    """FormWizardHandler admin using django-unfold."""

    pass


@admin.register(SavedFormDataEntry)
class SavedFormDataEntryAdmin(FobiSavedFormDataEntryAdmin, ModelAdmin):
    """SavedFormDataEntry admin using django-unfold.

    Saved entries are created programmatically only.
    Non-superuser staff can view entries but cannot modify or delete them.
    Superusers retain edit/delete access, but cannot add entries manually.
    """

    def has_add_permission(self, request):
        return False

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
