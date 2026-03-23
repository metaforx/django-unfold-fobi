"""Reusable admin mixins for site-aware Fobi integration.

These mixins are designed to be composed with ``FormEntryProxyAdmin``
and ``SavedFormDataEntryAdmin`` in consuming projects.

Usage::

    from unfold_fobi.admin import FormEntryProxyAdmin as BaseAdmin
    from unfold_fobi.contrib.sites.admin import (
        RelationSiteScopeAdminMixin,
        SiteAwareFormEntryMixin,
    )

    class FormEntryProxyAdmin(
        SiteAwareFormEntryMixin,
        RelationSiteScopeAdminMixin,
        BaseAdmin,
    ):
        site_relation_lookup = "site_binding__sites"
"""

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _

from .conf import get_sites_for_user_func
from .models import FobiFormSiteBinding
from .services import copy_site_bindings, ensure_binding


class RelationSiteScopeAdminMixin:
    """Site filtering and permission checks through a relation path.

    Set ``site_relation_lookup`` to the ORM lookup path from the model
    to its sites (e.g. ``"site_binding__sites"``).
    """

    site_relation_lookup = ""
    site_list_filter = ""

    def _site_relation_lookup(self):
        if not self.site_relation_lookup:
            raise ValueError("site_relation_lookup must be set on the admin class")
        return self.site_relation_lookup

    def _site_list_filter(self):
        return self.site_list_filter or self._site_relation_lookup()

    def get_sites_for_user(self, user):
        """Return the sites queryset for the given user.

        Override this method or set ``UNFOLD_FOBI_SITES_FOR_USER`` in settings.
        """
        return get_sites_for_user_func()(user)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        user_sites = self.get_sites_for_user(request.user)
        return qs.filter(
            **{f"{self._site_relation_lookup()}__in": user_sites}
        ).distinct()

    def get_list_filter(self, request):
        list_filter = list(super().get_list_filter(request) or ())
        site_filter = self._site_list_filter()
        if site_filter not in list_filter:
            list_filter.insert(0, site_filter)
        return list_filter

    def _has_site_scoped_permission(self, request, action, obj=None):
        """Check model-level permission + object-level site membership."""
        if request.user.is_superuser:
            return True

        if action not in ("view", "change", "delete", "add"):
            return False
        perm_codename = f"{self.opts.app_label}.{action}_{self.opts.model_name}"
        if not request.user.has_perm(perm_codename):
            return False

        if obj is None or action == "add":
            return True

        user_sites = self.get_sites_for_user(request.user)
        return self.model._default_manager.filter(
            pk=obj.pk,
            **{f"{self._site_relation_lookup()}__in": user_sites},
        ).exists()


class SiteAwareFormEntryMixin:
    """Admin mixin that adds a synthetic ``sites`` field to the form entry admin.

    Must be combined with ``RelationSiteScopeAdminMixin`` and placed
    before ``FormEntryProxyAdmin`` in the MRO.
    """

    site_fieldset_label = _("Publication sites")
    site_fieldset_classes = ("tab",)

    def get_allowed_sites(self, request):
        """Return the sites the current user is allowed to assign."""
        if request.user.is_superuser:
            return Site.objects.all()
        return self.get_sites_for_user(request.user)

    def _get_selected_site_ids(self, obj):
        """Return the currently selected site IDs for the given object."""
        if not obj or not obj.pk:
            return []
        binding = FobiFormSiteBinding.objects.filter(form_entry=obj).first()
        if binding:
            return list(binding.sites.values_list("id", flat=True))
        return []

    def get_form(self, request, obj=None, **kwargs):
        from unfold_fobi.forms import FormEntryFormWithCloneable

        allowed_sites = self.get_allowed_sites(request)
        allowed_site_ids = set(allowed_sites.values_list("id", flat=True))
        selected_site_ids = self._get_selected_site_ids(obj)

        class SiteAwareForm(FormEntryFormWithCloneable):
            sites = forms.ModelMultipleChoiceField(
                label=_("Sites"),
                queryset=Site.objects.none(),
                required=False,
                widget=FilteredSelectMultiple(_("Sites"), is_stacked=False),
            )

            def __init__(self, *args, **form_kwargs):
                form_kwargs.setdefault("request", request)
                super().__init__(*args, **form_kwargs)
                self.fields["sites"].queryset = allowed_sites
                if selected_site_ids:
                    self.fields["sites"].initial = [
                        sid for sid in selected_site_ids if sid in allowed_site_ids
                    ]

        # Set form before calling super so FormEntryProxyAdmin.get_form
        # respects it (via kwargs.setdefault).
        kwargs["form"] = SiteAwareForm
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        if any("sites" in fs[1].get("fields", ()) for fs in fieldsets):
            return fieldsets
        fieldsets.append(
            (
                self.site_fieldset_label,
                {
                    "classes": self.site_fieldset_classes,
                    "fields": ("sites",),
                },
            )
        )
        return fieldsets

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        binding, _ = ensure_binding(obj)
        selected_sites = form.cleaned_data.get("sites")
        if selected_sites:
            binding.sites.set(selected_sites)
            return
        binding.sites.clear()
        self.assign_default_sites(request, binding)

    def assign_default_sites(self, request, binding):
        """Hook for projects to implement default site assignment.

        Called when no sites are selected in the form.
        Override this to implement fallback logic (e.g. assign user's group sites).
        By default does nothing — the binding will have no sites assigned.
        """
        pass

    def _do_import(self, request, entry_data):
        """Import a form entry and create a site binding."""
        imported_entry = super()._do_import(request, entry_data)
        binding, _ = ensure_binding(imported_entry)
        self.assign_default_sites(request, binding)
        return imported_entry

    def _do_clone(self, request, form_entry):
        """Clone a form entry and propagate site bindings from the source."""
        clone = super()._do_clone(request, form_entry)
        target_binding = copy_site_bindings(form_entry, clone)
        if not target_binding.sites.exists():
            self.assign_default_sites(request, target_binding)
        return clone
