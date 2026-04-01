"""FormEntryProxy admin using native Unfold change view."""

import json

from django import forms
from django.contrib import admin, messages
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from fobi.forms import FormEntryForm
from fobi.utils import perform_form_entry_import, prepare_form_entry_export_data

from unfold_fobi.services import unlink_saved_entries
from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.enums import ActionVariant

from ..forms import FormEntryFormWithCloneable, ImportFormEntryJsonForm
from ..models import FormEntryProxy
from ..services import clone_form_entry
from .inlines import FormElementEntryInline, FormHandlerEntryInline
from fobi.models import FormEntry

@admin.register(FormEntryProxy)
class FormEntryProxyAdmin(ModelAdmin):
    """
    FormEntryProxy admin using a native Unfold change view.

    T10/T10a: native admin change form with element/handler inlines,
    "Add" dropdowns for available plugins, and editable element ordering.
    """

    list_display = [
        "name",
        "slug",
        "is_public",
        "active_date_from",
        "active_date_to",
        "updated",
    ]
    list_filter = ["is_public", "created", "updated"]
    search_fields = ["name", "slug"]
    readonly_fields = ["created", "updated"]

    def get_readonly_fields(self, request, obj=None):
        """Show slug as read-only on change view; hide on add (auto-generated)."""
        ro = list(super().get_readonly_fields(request, obj))
        if obj:
            ro.insert(0, "slug")
        return ro

    list_display_links = ["name"]
    compressed_fields = True
    warn_unsaved_form = True
    actions = ["export_selected_forms", "clone_selected_forms", "safe_delete_selected"]
    actions_list = ["import_form_entry_action"]
    inlines = [FormElementEntryInline, FormHandlerEntryInline]

    class Media:
        js = ("unfold_fobi/js/admin_popup_actions.js",)
        css = {"all": ("unfold_fobi/css/admin_action_dropdown_fix.css",)}

    def get_form(self, request, obj=None, **kwargs):
        """Use Fobi's FormEntryForm and inject request for validation/widgets."""
        kwargs.setdefault("form", FormEntryFormWithCloneable)
        form_class = super().get_form(request, obj, **kwargs)

        class RequestForm(form_class):
            def __init__(self, *args, **form_kwargs):
                form_kwargs.setdefault("request", request)
                super().__init__(*args, **form_kwargs)

            def clean_name(self_form):
                """Check for unique form name per user"""
                name = self_form.cleaned_data.get("name")
                if not name:
                    return name
                user = getattr(obj, "user", None) if obj else request.user
                if user is None:
                    user = request.user
                qs = FormEntry.objects.filter(user=user, name=name)
                if obj:
                    qs = qs.exclude(pk=obj.pk)
                if qs.exists():
                    raise forms.ValidationError(
                        _("A form with this name already exists.")
                    )
                return name

        return RequestForm

    def _collect_editable_fields(self):
        return [
            field
            for field in self.model._meta.fields
            if getattr(field, "editable", False)
        ]

    def get_fieldsets(self, request, obj=None):
        """Group FormEntry fields into stable admin sections and keep cloneability fields visible."""
        form_fields = set(FormEntryFormWithCloneable.base_fields)
        editable_fields = [
            field
            for field in self._collect_editable_fields()
            if field.name in form_fields
        ]
        if "is_cloneable" not in form_fields:
            for field in self._collect_editable_fields():
                if field.name == "is_cloneable":
                    editable_fields.append(field)
                    break
        remaining = [field.name for field in editable_fields]
        extra_fields = [
            name for name in FormEntryForm.base_fields if name not in remaining
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
            fieldsets.append((_("Basic information"), {"fields": basic_fields}))
        if visibility_fields:
            if "is_public" in visibility_fields and "is_cloneable" in visibility_fields:
                visibility_fields = [
                    ("is_public", "is_cloneable"),
                    *[
                        name
                        for name in visibility_fields
                        if name not in ("is_public", "is_cloneable")
                    ],
                ]
            fieldsets.append((_("Visibility"), {"fields": visibility_fields}))
        if success_fields:
            fieldsets.append((_("Success page"), {"fields": success_fields}))
        if appearance_fields:
            fieldsets.append((_("Appearance"), {"fields": appearance_fields}))
        if ownership_fields:
            fieldsets.append((_("Ownership"), {"fields": ownership_fields}))
        if date_fields:
            fieldsets.append(
                (
                    _("Active dates"),
                    {"fields": ["active_date_from", "active_date_to"]},
                )
            )
        if remaining or extra_fields:
            remaining.extend([name for name in extra_fields if name not in remaining])
            fieldsets.append((_("Advanced"), {"fields": remaining}))

        if fieldsets:
            return fieldsets
        return super().get_fieldsets(request, obj)

    def changelist_view(self, request, extra_context=None):
        """Override changelist to add custom buttons."""
        extra_context = extra_context or {}
        extra_context["title"] = _("Forms")
        return super().changelist_view(request, extra_context)

    def _get_available_form_handler_plugins(self, request, form_entry):
        """Return handler plugins available for current user and form constraints."""
        from fobi.base import form_handler_plugin_registry
        from fobi.models import FormHandlerEntry
        from fobi.utils import get_user_form_handler_plugins

        all_handlers = get_user_form_handler_plugins(request.user)
        existing_uids = set(
            FormHandlerEntry.objects.filter(form_entry=form_entry).values_list(
                "plugin_uid", flat=True
            )
        )
        available_handlers = []
        for uid, name in all_handlers:
            if uid in existing_uids:
                plugin_cls = form_handler_plugin_registry.get(uid)
                if plugin_cls and not getattr(plugin_cls, "allow_multiple", True):
                    continue
            available_handlers.append((uid, name))
        return available_handlers

    def _build_native_add_dropdown_actions(self, request, form_entry):
        """Build two native Unfold dropdown actions for adding elements/handlers."""
        from fobi.utils import get_user_form_element_plugins_grouped

        actions_detail = []

        element_items = []
        for _group, plugins in get_user_form_element_plugins_grouped(
            request.user
        ).items():
            for uid, name in plugins:
                element_items.append(
                    {
                        "title": name,
                        "path": (
                            reverse(
                                "fobi.add_form_element_entry",
                                kwargs={
                                    "form_entry_id": form_entry.pk,
                                    "form_element_plugin_uid": uid,
                                },
                            )
                            + "?_popup=1"
                        ),
                        "variant": ActionVariant.DEFAULT,
                        "attrs": {
                            "id": f"add_fobi_element_{uid}",
                            "data-popup": "yes",
                        },
                    }
                )
        if element_items:
            actions_detail.append(
                {
                    "title": _("Add element"),
                    "icon": "add",
                    "variant": ActionVariant.PRIMARY,
                    "method_name": "add_element",
                    "attrs": {
                        "x-show": "activeTab == 'formelemententry_set'",
                        "x-cloak": True,
                    },
                    "items": element_items,
                }
            )

        handler_items = []
        for uid, name in self._get_available_form_handler_plugins(request, form_entry):
            handler_items.append(
                {
                    "title": name,
                    "path": (
                        reverse(
                            "fobi.add_form_handler_entry",
                            kwargs={
                                "form_entry_id": form_entry.pk,
                                "form_handler_plugin_uid": uid,
                            },
                        )
                        + "?_popup=1"
                    ),
                    "variant": ActionVariant.DEFAULT,
                    "attrs": {
                        "id": f"add_fobi_handler_{uid}",
                        "data-popup": "yes",
                    },
                }
            )
        if handler_items:
            actions_detail.append(
                {
                    "title": _("Add handler"),
                    "icon": "add",
                    "variant": ActionVariant.DEFAULT,
                    "method_name": "add_handler",
                    "attrs": {
                        "x-show": "activeTab == 'formhandlerentry_set'",
                        "x-cloak": True,
                    },
                    "items": handler_items,
                }
            )

        return actions_detail

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """Inject native Unfold dropdown actions for add element/handler."""
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if obj:
            extra_context["form_entry"] = obj
        response = super().change_view(request, object_id, form_url, extra_context)
        if obj and hasattr(response, "context_data"):
            response.context_data["actions_detail"] = (
                self._build_native_add_dropdown_actions(request, obj)
            )
        return response

    def save_model(self, request, obj, form, change):
        """Ensure creator is set when using the native admin add view."""
        if not getattr(obj, "user_id", None):
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def export_selected_forms(self, request, queryset):
        data = [prepare_form_entry_export_data(entry) for entry in queryset]
        payload = json.dumps(data, cls=DjangoJSONEncoder)
        response = HttpResponse(payload, content_type="application/json")
        response["Content-Disposition"] = (
            'attachment; filename="form-entries-export.json"'
        )
        return response

    export_selected_forms.short_description = _("Export selected forms (JSON)")

    def _do_import(self, request, entry_data):
        """Import a single form entry. Override for post-import hooks."""
        return perform_form_entry_import(request, entry_data)

    def _do_clone(self, request, form_entry):
        """Clone a single form entry. Override for post-clone hooks."""
        return clone_form_entry(form_entry)

    @action(
        description=_("Import form (JSON)"),
        url_path="import-json",
        icon="file_upload",
        permissions=("add",),
    )
    def import_form_entry_action(self, request):
        """Changelist action: import a form entry from an uploaded JSON file."""
        from django.template.response import TemplateResponse

        cancel_url = reverse("admin:unfold_fobi_formentryproxy_changelist")
        if request.method == "POST":
            form = ImportFormEntryJsonForm(
                request.POST, request.FILES, cancel_url=cancel_url
            )
            if form.is_valid():
                entries = form.cleaned_data["entries_payload"]
                imported = []
                for entry_data in entries:
                    imported.append(self._do_import(request, entry_data))
                names = ", ".join(e.name for e in imported)
                messages.success(
                    request,
                    _("Imported {count} form(s): {names}.").format(
                        count=len(imported), names=names
                    ),
                )
                return HttpResponse(
                    status=302,
                    headers={
                        "Location": cancel_url,
                    },
                )
        else:
            form = ImportFormEntryJsonForm(cancel_url=cancel_url)
        return TemplateResponse(
            request,
            "admin/unfold_fobi/formentryproxy/import_action.html",
            {
                "title": _("Import form from JSON"),
                "content_title": _("Import form from JSON"),
                "form": form,
                "model_admin": self,
            },
        )

    @admin.action(description=_("Clone selected forms"))
    def clone_selected_forms(self, request, queryset):
        created = 0
        skipped = 0
        for form_entry in queryset:
            if not form_entry.is_cloneable:
                skipped += 1
                continue
            self._do_clone(request, form_entry)
            created += 1

        if skipped:
            messages.warning(
                request,
                _("Skipped {count} form(s) because cloning is disabled.").format(
                    count=skipped
                ),
            )
        if created > 0:
            messages.success(
                request,
                _("Cloned {count} form(s).").format(count=created),
            )

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm("fobi.delete_formentry")

    @staticmethod
    def _safe_delete_form(form_entry):
        """Unlink saved submissions, then delete the form definition."""
        unlink_saved_entries(form_entry)
        form_entry.delete()

    def delete_model(self, request, obj):
        name = obj.name
        self._safe_delete_form(obj)
        messages.info(
            request,
            _('The form "{0}" was deleted successfully.').format(name),
        )

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            name = obj.name
            self._safe_delete_form(obj)
            messages.info(
                request,
                _('The form "{0}" was deleted successfully.').format(name),
            )

    @admin.action(description=_("Delete selected forms (safe)"))
    def safe_delete_selected(self, request, queryset):
        deleted = 0
        skipped = 0
        for form_entry in queryset:
            if not self.has_delete_permission(request, form_entry):
                skipped += 1
                continue
            self._safe_delete_form(form_entry)
            deleted += 1
        if deleted:
            messages.success(
                request,
                _("Deleted {count} form(s). Submitted data was preserved.").format(
                    count=deleted
                ),
            )
        if skipped:
            messages.warning(
                request,
                _("Skipped {count} form(s) you do not have permission to delete.").format(
                    count=skipped
                ),
            )
