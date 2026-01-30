# admin.py
from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import FormEntryProxy
from .views import FormEntryCreateView, FormEntryEditView, FormEntryImportView, FormWizardsDashboardView

@admin.register(FormEntryProxy)
class FormEntryProxyAdmin(ModelAdmin):
    """
    FormEntryProxy admin that uses standard list view and links to custom edit views.
    
    This replaces the dashboard view with a standard admin list view.
    """
    list_display = ['name_link', 'slug', 'is_public', 'is_cloneable', 'created', 'updated']
    list_filter = ['is_public', 'is_cloneable', 'created', 'updated']
    search_fields = ['name', 'slug']
    readonly_fields = ['created', 'updated']
    list_display_links = ['name_link']  # Make name clickable
    
    def name_link(self, obj):
        """Display name as link to custom edit view."""
        edit_url = reverse('admin:unfold_fobi_formentryproxy_edit', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', edit_url, obj.name)
    name_link.short_description = 'Name'
    name_link.admin_order_field = 'name'
    
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
        extra_context['title'] = 'Forms'
        return super().changelist_view(request, extra_context)
    
    def response_change(self, request, obj):
        """Override to redirect to custom edit view after save."""
        from django.shortcuts import redirect
        return redirect('admin:unfold_fobi_formentryproxy_edit', form_entry_id=obj.pk)
