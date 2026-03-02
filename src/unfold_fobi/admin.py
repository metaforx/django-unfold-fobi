# admin.py — T10 POC: native Unfold admin change view for FormEntryProxy
import json

from django.contrib import admin, messages
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.http import HttpResponse
from django.urls import path, reverse
from django.utils.dateparse import parse_datetime
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from fobi.forms import FormEntryForm
from fobi.models import FormElementEntry, FormHandlerEntry
from fobi.utils import perform_form_entry_import, prepare_form_entry_export_data
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action
from unfold.enums import ActionVariant

from .forms import FormEntryFormWithCloneable, ImportFormEntryJsonForm
from .models import FormEntryProxy
from .services import clone_form_entry


class FormElementEntryInline(TabularInline):
    """Inline showing form elements with sortable drag-and-drop and action links."""

    model = FormElementEntry
    fields = ("plugin_uid", "position", "plugin_data_preview", "element_actions")
    readonly_fields = ("plugin_uid", "plugin_data_preview", "element_actions")
    ordering = ("position",)
    extra = 0
    verbose_name = _("Form element")
    verbose_name_plural = _("Form elements")
    tab = True
    ordering_field = "position"
    hide_ordering_field = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description=_("Preview"))
    def plugin_data_preview(self, obj):
        if not obj.plugin_data:
            return "-"
        try:
            data = json.loads(obj.plugin_data)
            label = data.get("label") or data.get("name", "")
            return label[:80] if label else "-"
        except (json.JSONDecodeError, TypeError):
            return obj.plugin_data[:80]

    @admin.display(description=_("Actions"))
    def element_actions(self, obj):
        if not obj.pk:
            return "-"
        edit_url = (
            reverse(
                "fobi.edit_form_element_entry",
                kwargs={"form_element_entry_id": obj.pk},
            )
            + "?_popup=1"
        )
        delete_url = (
            reverse(
                "fobi.delete_form_element_entry",
                kwargs={"form_element_entry_id": obj.pk},
            )
            + "?_popup=1"
        )
        return format_html(
            '<a href="{}" id="change_fobi_element_{}" data-popup="yes"'
            ' class="related-widget-wrapper-link inline-flex items-center gap-1'
            " text-primary-600 hover:text-primary-700"
            ' dark:text-primary-500 dark:hover:text-primary-400">'
            '<span class="material-symbols-outlined text-base">edit</span>{}</a>'
            " &nbsp; "
            '<a href="{}" id="delete_fobi_element_{}" data-popup="yes"'
            ' class="related-widget-wrapper-link inline-flex items-center gap-1'
            " text-red-600 hover:text-red-700"
            ' dark:text-red-500 dark:hover:text-red-400">'
            '<span class="material-symbols-outlined text-base">delete</span>{}</a>',
            edit_url,
            obj.pk,
            _("Edit"),
            delete_url,
            obj.pk,
            _("Delete"),
        )


class FormHandlerEntryInline(TabularInline):
    """Read-only inline showing form handlers with links to fobi edit views."""

    model = FormHandlerEntry
    fields = ("plugin_uid", "handler_data_preview", "handler_actions")
    readonly_fields = ("plugin_uid", "handler_data_preview", "handler_actions")
    extra = 0
    verbose_name = _("Form handler")
    verbose_name_plural = _("Form handlers")
    tab = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_formset(self, request, obj=None, **kwargs):
        """Cache the request so handler_actions can forward it to get_custom_actions."""
        self._request = request
        return super().get_formset(request, obj, **kwargs)

    @admin.display(description=_("Preview"))
    def handler_data_preview(self, obj):
        if not obj.plugin_data:
            return "-"
        try:
            data = json.loads(obj.plugin_data)
            return str(data)[:80]
        except (json.JSONDecodeError, TypeError):
            return obj.plugin_data[:80]

    @admin.display(description=_("Actions"))
    def handler_actions(self, obj):
        if not obj.pk:
            return "-"
        parts = []
        if obj.plugin_data:
            edit_url = (
                reverse(
                    "fobi.edit_form_handler_entry",
                    kwargs={"form_handler_entry_id": obj.pk},
                )
                + "?_popup=1"
            )
            parts.append(
                format_html(
                    '<a href="{}" id="change_fobi_handler_{}" data-popup="yes"'
                    ' class="related-widget-wrapper-link inline-flex items-center gap-1'
                    " text-primary-600 hover:text-primary-700"
                    ' dark:text-primary-500 dark:hover:text-primary-400">'
                    '<span class="material-symbols-outlined text-base">edit</span>{}</a>',
                    edit_url,
                    obj.pk,
                    _("Edit"),
                )
            )
        delete_url = (
            reverse(
                "fobi.delete_form_handler_entry",
                kwargs={"form_handler_entry_id": obj.pk},
            )
            + "?_popup=1"
        )
        parts.append(
            format_html(
                '<a href="{}" id="delete_fobi_handler_{}" data-popup="yes"'
                ' class="related-widget-wrapper-link inline-flex items-center gap-1'
                " text-red-600 hover:text-red-700"
                ' dark:text-red-500 dark:hover:text-red-400">'
                '<span class="material-symbols-outlined text-base">delete</span>{}</a>',
                delete_url,
                obj.pk,
                _("Delete"),
            )
        )
        # Plugin custom actions (e.g. "View entries" for db_store)
        request = getattr(self, "_request", None)
        plugin = obj.get_plugin(request=request)
        if plugin:
            get_custom_actions = getattr(plugin, "get_custom_actions", None)
            custom_actions = (
                get_custom_actions(obj.form_entry, request)
                if callable(get_custom_actions)
                else []
            )
            for action_url, label, _icon in (custom_actions or []):
                # T07: redirect "View entries" to admin filtered changelist
                if str(label) == str(_("View entries")):
                    action_url = (
                        reverse(
                            "admin:fobi_contrib_plugins_form_handlers_db_store_savedformdataentry_changelist"
                        )
                        + f"?form_entry__id__exact={obj.form_entry_id}"
                    )
                parts.append(
                    format_html(
                        '<a href="{}" class="inline-flex items-center gap-1 text-primary-600 '
                        'hover:text-primary-700 dark:text-primary-500 dark:hover:text-primary-400">'
                        "{}</a>",
                        action_url,
                        label,
                    )
                )
        return mark_safe(" &nbsp; ".join(parts))


@admin.register(FormEntryProxy)
class FormEntryProxyAdmin(ModelAdmin):
    """
    FormEntryProxy admin using native Unfold change view.

    T10/T10a: native admin change form with element/handler inlines,
    "Add" dropdowns for available plugins, and editable element ordering.
    """

    list_display = ["name", "slug", "is_public", "created", "updated"]
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
    actions = ["export_selected_forms", "clone_selected_forms"]
    actions_list = ["import_form_entry_action"]
    inlines = [FormElementEntryInline, FormHandlerEntryInline]

    class Media:
        js = ("unfold_fobi/js/admin_popup_actions.js",)
        css = {"all": ("unfold_fobi/css/admin_action_dropdown_fix.css",)}

    def get_form(self, request, obj=None, **kwargs):
        """Use Fobi's FormEntryForm and inject request for validation/widgets."""
        kwargs["form"] = FormEntryFormWithCloneable
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

    def _collect_editable_fields(self):
        return [
            field
            for field in self.model._meta.fields
            if getattr(field, "editable", False)
        ]

    def get_fieldsets(self, request, obj=None):
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

    def get_urls(self):
        """Add custom URLs for import/wizards views (kept for compatibility)."""
        from .views import FormEntryImportView, FormWizardsDashboardView

        urls = super().get_urls()
        custom_urls = [
            path(
                "import/",
                self.admin_site.admin_view(
                    FormEntryImportView.as_view(model_admin=self)
                ),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_import",
            ),
            path(
                "wizards/",
                self.admin_site.admin_view(
                    FormWizardsDashboardView.as_view(model_admin=self)
                ),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_wizards",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        """Override changelist to add custom buttons."""
        extra_context = extra_context or {}
        extra_context["title"] = _("Forms")
        return super().changelist_view(request, extra_context)

    def _get_available_form_handler_plugins(self, request, form_entry):
        """Return handler plugins available for current user and form constraints."""
        from fobi.base import form_handler_plugin_registry
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
        if not obj.user_id:
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

    @action(
        description=_("Import form (JSON)"),
        url_path="import-json",
        icon="file_upload",
        permissions=("fobi.add_formentry",),
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
                    imported.append(perform_form_entry_import(request, entry_data))
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
                        "Location": cancel_url
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
            clone_form_entry(form_entry)
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

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()
            messages.info(
                request,
                _('The form "{0}" was deleted successfully.').format(obj.name),
            )
