from django.apps import AppConfig
from django import forms
from collections import OrderedDict


def patch_form_init(form_class, apply_fn):
    """
    Helper to patch a form class's __init__ method to apply Unfold widgets.
    
    Args:
        form_class: The form class to patch
        apply_fn: Function to call after form initialization (e.g., apply_unfold_widgets_to_form)
    
    Returns:
        True if patching was successful, False if already patched or failed
    """
    if not form_class or hasattr(form_class, '_unfold_widgets_applied'):
        return False
    
    try:
        original_init = form_class.__init__
        
        def new_init(self, *args, **kwargs):
            """Patched __init__ that applies Unfold widgets after form initialization."""
            original_init(self, *args, **kwargs)
            apply_fn(self)
        
        form_class.__init__ = new_init
        form_class._unfold_widgets_applied = True
        return True
    except (AttributeError, TypeError):
        return False


class UnfoldFobiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'unfold_fobi'

    @staticmethod
    def _patch_fobi_owner_filtering():
        """Remove owner filtering from fobi edit/delete views for staff users.

        Fobi hardcodes two layers of owner checks:
        1. ``_get_queryset`` filters by ``form_entry__user__pk == request.user.pk``
        2. Permission classes check ``obj.form_entry.user == request.user``

        Both cause 404 / PermissionDenied when an admin who is not the form's
        original creator tries to edit or delete elements/handlers.  This patch
        relaxes both checks for ``is_staff`` users.
        """
        # --- Layer 1: queryset filtering ---
        try:
            from fobi.views.class_based import (
                EditFormElementEntryView,
                EditFormHandlerEntryView,
                AbstractDeletePluginEntryView,
            )
        except ImportError:
            return

        def _make_staff_queryset(original):
            def _get_queryset(self, request):
                qs = original(self, request)
                if request.user.is_staff:
                    return qs.model._default_manager.select_related(
                        "form_entry", "form_entry__user"
                    )
                return qs
            return _get_queryset

        for view_cls in (
            EditFormElementEntryView,
            EditFormHandlerEntryView,
            AbstractDeletePluginEntryView,
        ):
            if not getattr(view_cls._get_queryset, "_unfold_patched", False):
                view_cls._get_queryset = _make_staff_queryset(
                    view_cls._get_queryset
                )
                view_cls._get_queryset._unfold_patched = True

        # --- Layer 2: permission classes ---
        try:
            from fobi.permissions.default import (
                EditFormElementEntryPermission,
                DeleteFormElementEntryPermission,
                EditFormHandlerEntryPermission,
                DeleteFormHandlerEntryPermission,
            )
        except ImportError:
            return

        def _make_staff_object_perm(original):
            def has_object_permission(self, request, view, obj):
                if request.user.is_staff:
                    return True
                return original(self, request, view, obj)
            return has_object_permission

        for perm_cls in (
            EditFormElementEntryPermission,
            DeleteFormElementEntryPermission,
            EditFormHandlerEntryPermission,
            DeleteFormHandlerEntryPermission,
        ):
            method = perm_cls.has_object_permission
            if not getattr(method, "_unfold_patched", False):
                patched = _make_staff_object_perm(method)
                patched._unfold_patched = True
                perm_cls.has_object_permission = patched

    @staticmethod
    def _patch_fobi_popup_response():
        """Return a close-and-reload popup response when ``_popup=1`` is set.

        Fobi add/edit/delete views always redirect after a successful
        operation.  When the view is opened in popup mode (``?_popup=1``),
        we intercept the redirect and return a tiny HTML page that tells
        the opening window to reload, compatible with both ``window.open``
        popups and ``django-unfold-modal`` iframe modals.
        """
        from django.template.loader import render_to_string
        from django.http import HttpResponse

        try:
            from fobi.views.class_based import (
                AddFormElementEntryView,
                EditFormElementEntryView,
                AddFormHandlerEntryView,
                EditFormHandlerEntryView,
                DeleteFormElementEntryView,
                DeleteFormHandlerEntryView,
            )
        except ImportError:
            return

        POPUP_TEMPLATE = "admin/unfold_fobi/popup_response.html"
        SESSION_KEY = "_fobi_popup_count"

        def _is_popup(request):
            """Check _popup in GET, POST, or session counter (set during GET)."""
            return (
                request.GET.get("_popup")
                or request.POST.get("_popup")
                or request.session.get(SESSION_KEY, 0) > 0
            )

        def _popup_http_response(request):
            count = request.session.get(SESSION_KEY, 0)
            if count > 1:
                request.session[SESSION_KEY] = count - 1
            else:
                request.session.pop(SESSION_KEY, None)
            html = render_to_string(POPUP_TEMPLATE)
            response = HttpResponse(html)
            response["X-Frame-Options"] = "SAMEORIGIN"
            return response

        def _is_success_redirect(response):
            """Return True only for fobi success redirects (not login/error)."""
            if response.status_code not in (301, 302):
                return False
            location = response.get("Location", "")
            # Auth redirects contain the login URL path; skip those.
            from django.conf import settings

            login_path = getattr(settings, "LOGIN_URL", "/accounts/login/")
            if login_path and login_path in location:
                return False
            return True

        def _wrap_method(original, method_name, intercept_get_redirect=False):
            """Wrap get/post to store popup counter and intercept redirects."""
            def wrapped(self, request, *args, **kwargs):
                if method_name == "get":
                    if request.GET.get("_popup"):
                        count = request.session.get(SESSION_KEY, 0)
                        request.session[SESSION_KEY] = count + 1
                    else:
                        # Non-popup GET: full reset of stale counter.
                        request.session.pop(SESSION_KEY, None)
                response = original(self, request, *args, **kwargs)
                # Intercept redirects for:
                # - POST (successful save on add/edit views)
                # - GET on add views (no-form plugins save & redirect on GET)
                # - GET on delete views (fobi deletes on GET)
                intercept = (
                    _is_popup(request)
                    and _is_success_redirect(response)
                    and (request.method == "POST" or intercept_get_redirect)
                )
                if intercept:
                    return _popup_http_response(request)
                # T10g: Allow iframe embedding for popup views.
                # Set SAMEORIGIN so the middleware won't override with DENY.
                if _is_popup(request):
                    response["X-Frame-Options"] = "SAMEORIGIN"
                return response
            return wrapped

        # Add views: intercept GET redirects too (no-form plugins save on GET)
        add_views = (
            AddFormElementEntryView,
            AddFormHandlerEntryView,
        )
        edit_views = (
            EditFormElementEntryView,
            EditFormHandlerEntryView,
        )
        delete_views = (
            DeleteFormElementEntryView,
            DeleteFormHandlerEntryView,
        )
        for view_cls in edit_views:
            for method_name in ("get", "post"):
                method = getattr(view_cls, method_name, None)
                if method and not getattr(method, "_unfold_popup_patched", False):
                    wrapped = _wrap_method(method, method_name)
                    wrapped._unfold_popup_patched = True
                    setattr(view_cls, method_name, wrapped)
        for view_cls in (*add_views, *delete_views):
            for method_name in ("get", "post"):
                method = getattr(view_cls, method_name, None)
                if method and not getattr(method, "_unfold_popup_patched", False):
                    wrapped = _wrap_method(
                        method, method_name, intercept_get_redirect=True
                    )
                    wrapped._unfold_popup_patched = True
                    setattr(view_cls, method_name, wrapped)

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

        # Register DRF integration db_store handler so PUT /api/fobi-form-entry/{slug}/ saves to SavedFormDataEntry
        try:
            import fobi.contrib.apps.drf_integration.form_handlers.db_store.fobi_integration_form_handlers  # noqa: F401
        except ImportError:
            pass

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
                patch_form_init(
                    FormElementEntryFormSet.form,
                    unfold_forms.apply_unfold_widgets_to_form
                )
            
            # Patch FormWizardFormEntryFormSet
            if hasattr(FormWizardFormEntryFormSet, 'form'):
                patch_form_init(
                    FormWizardFormEntryFormSet.form,
                    unfold_forms.apply_unfold_widgets_to_form
                )
        except (AttributeError, TypeError, ImportError):
            # Formset classes might not exist or have different structure
            pass
        
        for form_class in form_classes_to_patch:
            try:
                patch_form_init(form_class, unfold_forms.apply_unfold_widgets_to_form)
            except (AttributeError, TypeError, ImportError):
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
                    if form_class:
                        patch_form_init(form_class, unfold_forms.apply_unfold_widgets_to_form)
                    return form_class
                
                fobi_admin.FormElementEntryAdmin.get_form = patched_get_form
            
            # Patch FormHandlerEntryAdmin's get_form method
            if hasattr(fobi_admin, 'FormHandlerEntryAdmin'):
                original_get_form = fobi_admin.FormHandlerEntryAdmin.get_form
                
                def patched_get_form(self, request, obj=None, **kwargs):
                    """Patched get_form that applies Unfold widgets to form handler entry forms."""
                    form_class = original_get_form(self, request, obj=obj, **kwargs)
                    if form_class:
                        patch_form_init(form_class, unfold_forms.apply_unfold_widgets_to_form)
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
                            patch_form_init(form, unfold_forms.apply_unfold_widgets_to_form)
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

        # Ensure db_store handler is attached when a form is saved (so REST API submissions are stored)
        try:
            from django.db.models.signals import post_save
            from django.dispatch import receiver
            from fobi.models import FormEntry, FormHandlerEntry

            @receiver(post_save, sender=FormEntry)
            def ensure_db_store_handler(sender, instance, **kwargs):
                FormHandlerEntry.objects.get_or_create(
                    form_entry=instance,
                    plugin_uid="db_store",
                )
        except (ImportError, AttributeError):
            pass

        # T10b: Patch fobi edit/delete views to allow staff users to access
        # entries regardless of form ownership. Fobi hardcodes
        # `form_entry__user__pk=request.user.pk` in _get_queryset, causing
        # 404 for admin users who are not the form's original creator.
        self._patch_fobi_owner_filtering()

        # T10e: Patch fobi add/edit/delete views to return a popup response
        # instead of a redirect when opened with ?_popup=1.
        self._patch_fobi_popup_response()
