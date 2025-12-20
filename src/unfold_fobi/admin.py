# admin.py
from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import FormEntryProxy

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
        edit_url = reverse('fobi.edit_form_entry', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', edit_url, obj.name)
    name_link.short_description = 'Name'
    name_link.admin_order_field = 'name'
    
    def get_urls(self):
        """Add custom URLs for create, import, and wizards."""
        from django.views.generic import RedirectView
        from django.shortcuts import redirect
        
        urls = super().get_urls()
        
        # Add redirect views for create, import, and wizards
        # Use lambda to defer reverse() call until request time
        def redirect_to_create(request):
            return redirect('fobi.create_form_entry')
        
        def redirect_to_import(request):
            return redirect('fobi.import_form_entry')
        
        def redirect_to_wizards(request):
            return redirect('fobi.form_wizards_dashboard')
        
        custom_urls = [
            path('create/', 
                 self.admin_site.admin_view(redirect_to_create),  # Use admin_view to ensure proper processing
                 name='%s_%s_create' % (self.model._meta.app_label, self.model._meta.model_name)),
            path('import/', 
                 self.admin_site.admin_view(redirect_to_import),  # Use admin_view to ensure proper processing
                 name='%s_%s_import' % (self.model._meta.app_label, self.model._meta.model_name)),
            path('wizards/', 
                 self.admin_site.admin_view(redirect_to_wizards),  # Use admin_view to ensure proper processing
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
        return redirect('fobi.edit_form_entry', form_entry_id=obj.pk)
