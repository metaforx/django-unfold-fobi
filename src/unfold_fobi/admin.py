# admin.py
from django.contrib import admin
from django.db import models
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from fobi.forms import FormEntryForm
from django.utils.dateparse import parse_datetime
from .models import FormEntryProxy
from .views import FormEntryCreateView, FormEntryEditView, FormEntryImportView, FormWizardsDashboardView

@admin.register(FormEntryProxy)
class FormEntryProxyAdmin(ModelAdmin):
    """
    FormEntryProxy admin that uses standard list view and links to custom edit views.
    
    This replaces the dashboard view with a standard admin list view.
    """
    list_display = ["name_link", "slug", "is_public", "created", "updated"]
    list_filter = ["is_public", "created", "updated"]
    search_fields = ["name", "slug"]
    readonly_fields = ["created", "updated"]
    list_display_links = ["name_link"]  # Make name clickable
    compressed_fields = True
    warn_unsaved_form = True

    def get_form(self, request, obj=None, **kwargs):
        """Use Fobi's FormEntryForm and inject request for validation/widgets."""
        kwargs["form"] = FormEntryForm
        form_class = super().get_form(request, obj, **kwargs)

        class RequestForm(form_class):
            def __init__(self, *args, **form_kwargs):
                form_kwargs["request"] = request
                super().__init__(*args, **form_kwargs)

            def clean(self):
                cleaned = super().clean()
                # Defensive: ensure DateTimeField values are datetimes, not strings.
                for name, field in self.fields.items():
                    if field.__class__.__name__ == "DateTimeField":
                        value = cleaned.get(name)
                        if isinstance(value, str):
                            parsed = parse_datetime(value.strip())
                            if parsed is not None:
                                cleaned[name] = parsed
                return cleaned

        return RequestForm
    
    def name_link(self, obj):
        """Display name as link to custom edit view."""
        edit_url = reverse('admin:unfold_fobi_formentryproxy_edit', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', edit_url, obj.name)
    name_link.short_description = _("Name")
    name_link.admin_order_field = 'name'

    def _collect_editable_fields(self):
        return [
            field
            for field in self.model._meta.fields
            if getattr(field, "editable", False)
        ]

    def get_fieldsets(self, request, obj=None):
        form_fields = set(FormEntryForm.base_fields)
        editable_fields = [
            field for field in self._collect_editable_fields()
            if field.name in form_fields
        ]
        remaining = [field.name for field in editable_fields]
        extra_fields = [
            name for name in FormEntryForm.base_fields
            if name not in remaining
        ]

        def take(names):
            selected = [name for name in names if name in remaining]
            for name in selected:
                remaining.remove(name)
            return selected

        date_fields = [
            field.name
            for field in editable_fields
            if isinstance(field, (models.DateField, models.DateTimeField))
            and field.name in remaining
        ]
        for name in date_fields:
            remaining.remove(name)

        basic_fields = take(["name", "slug", "title", "description"])
        visibility_fields = take(
            ["is_public", "is_cloneable", "is_current", "is_private"]
        )
        success_fields = take(["success_page_title", "success_page_message"])
        appearance_fields = take(
            ["form_template_name", "form_css_class", "form_js_class"]
        )
        ownership_fields = take(
            ["user", "owner", "created_by", "updated_by", "user_id"]
        )

        fieldsets = []
        if basic_fields:
            fieldsets.append(
                (_("Basic information"), {"fields": basic_fields})
            )
        if visibility_fields:
            fieldsets.append(
                (_("Visibility"), {"fields": visibility_fields})
            )
        if success_fields:
            fieldsets.append(
                (_("Success page"), {"fields": success_fields})
            )
        if appearance_fields:
            fieldsets.append(
                (_("Appearance"), {"fields": appearance_fields})
            )
        if ownership_fields:
            fieldsets.append(
                (_("Ownership"), {"fields": ownership_fields})
            )
        if date_fields:
            fieldsets.append(
                (
                    _("Active dates"),
                    {"fields": ["active_date_from", "active_date_to"]},
                )
            )
        if remaining or extra_fields:
            remaining.extend(
                [name for name in extra_fields if name not in remaining]
            )
            fieldsets.append(
                (_("Advanced"), {"fields": remaining})
            )

        if fieldsets:
            return fieldsets
        return super().get_fieldsets(request, obj)
    
    def get_urls(self):
        """Add custom URLs for create, import, and wizards."""
        urls = super().get_urls()

        custom_urls = [
            path('edit/<int:form_entry_id>/',
                 self.admin_site.admin_view(
                     FormEntryEditView.as_view(model_admin=self)
                 ),
                 name='%s_%s_edit' % (self.model._meta.app_label, self.model._meta.model_name)),
            path('create/', 
                 self.admin_site.admin_view(
                     FormEntryCreateView.as_view(model_admin=self)
                 ),
                 name='%s_%s_create' % (self.model._meta.app_label, self.model._meta.model_name)),
            path('import/', 
                 self.admin_site.admin_view(
                     FormEntryImportView.as_view(model_admin=self)
                 ),
                 name='%s_%s_import' % (self.model._meta.app_label, self.model._meta.model_name)),
            path('wizards/', 
                 self.admin_site.admin_view(
                     FormWizardsDashboardView.as_view(model_admin=self)
                 ),
                 name='%s_%s_wizards' % (self.model._meta.app_label, self.model._meta.model_name)),
        ]
        
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        """Override changelist to add custom buttons."""
        extra_context = extra_context or {}
        extra_context["title"] = _("Forms")
        return super().changelist_view(request, extra_context)
    
    def response_change(self, request, obj):
        """Override to redirect to custom edit view after save."""
        from django.shortcuts import redirect
        return redirect('admin:unfold_fobi_formentryproxy_edit', form_entry_id=obj.pk)

    def response_add(self, request, obj, post_url_continue=None):
        """Redirect add flow to the builder edit view after save."""
        from django.shortcuts import redirect
        return redirect('admin:unfold_fobi_formentryproxy_edit', form_entry_id=obj.pk)

    def save_model(self, request, obj, form, change):
        """Ensure creator is set when using the native admin add view."""
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)
