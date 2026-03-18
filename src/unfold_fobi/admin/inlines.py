"""Inline admin definitions for FormEntryProxy admin."""

import json

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from fobi.models import FormElementEntry, FormHandlerEntry
from unfold.admin import TabularInline


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
    hide_title = True

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
    hide_title = True

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
            for action_url, label, _icon in custom_actions or []:
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
