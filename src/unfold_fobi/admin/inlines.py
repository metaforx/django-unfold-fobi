"""Inline admin definitions for FormEntryProxy admin."""

import json

from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from fobi.models import FormElementEntry, FormHandlerEntry
from unfold.admin import TabularInline

INLINE_ACTION_BUTTON_CLASS = (
    "related-widget-wrapper-link px-2.5 py-1.5 text-sm gap-1 shadow-none"
)
INLINE_ACTION_DANGER_CLASS = (
    "related-widget-wrapper-link px-2.5 py-1.5 text-sm gap-1 shadow-none "
    "border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700 dark:border-red-900/60 dark:text-red-500 "
    "dark:hover:bg-red-950/30 dark:hover:text-red-400"
)


def _build_action(
    url, label, icon_name=None, attrs=None, variant="default", button_class=""
):
    """Build context for a compact inline action button."""
    return {
        "url": url,
        "label": label,
        "icon_name": icon_name,
        "attrs": attrs or {},
        "variant": variant,
        "button_class": button_class,
    }


def _render_action_buttons(actions):
    """Render inline actions via the Unfold button component."""
    return render_to_string(
        "unfold_fobi/admin/inline_action_buttons.html",
        {
            "actions": actions,
        },
    )


class FormElementEntryInline(TabularInline):
    """Inline showing form elements with sortable drag-and-drop and action links."""

    model = FormElementEntry
    template = "admin/unfold_fobi/edit_inline/form_elements_tabular.html"
    fields = (
        "plugin_data_preview",
        "plugin_name",
        "required_field",
        "position",
        "element_actions",
    )
    readonly_fields = (
        "plugin_data_preview",
        "plugin_name",
        "required_field",
        "element_actions",
    )
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

    @admin.display(description=_("Label"))
    def plugin_data_preview(self, obj):
        if not obj.plugin_data:
            return "-"
        try:
            data = json.loads(obj.plugin_data)
            label = data.get("label") or data.get("name", "")
            return label[:80] if label else "-"
        except (json.JSONDecodeError, TypeError):
            return obj.plugin_data[:80]

    @admin.display(description=_("Form element"))
    def plugin_name(self, obj):
        plugin = obj.get_plugin()
        if plugin and getattr(plugin, "name", None):
            return force_str(plugin.name)
        return obj.plugin_uid or "-"

    @admin.display(description=_("Required field"), boolean=True)
    def required_field(self, obj):
        if not obj.plugin_data:
            return False
        try:
            data = json.loads(obj.plugin_data)
            return bool(data.get("required"))
        except (json.JSONDecodeError, TypeError):
            return False

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
            "{}",
            _render_action_buttons(
                [
                    _build_action(
                        edit_url,
                        _("Edit"),
                        icon_name="edit",
                        attrs={
                            "id": f"change_fobi_element_{obj.pk}",
                            "data-popup": "yes",
                        },
                        button_class=INLINE_ACTION_BUTTON_CLASS,
                    ),
                    _build_action(
                        delete_url,
                        _("Delete"),
                        icon_name="delete",
                        attrs={
                            "id": f"delete_fobi_element_{obj.pk}",
                            "data-popup": "yes",
                        },
                        button_class=INLINE_ACTION_DANGER_CLASS,
                    ),
                ]
            ),
        )


class FormHandlerEntryInline(TabularInline):
    """Read-only inline showing form handlers with links to fobi edit views."""

    model = FormHandlerEntry
    template = "admin/unfold_fobi/edit_inline/form_handlers_tabular.html"
    fields = ("handler_name", "handler_data_preview", "handler_actions")
    readonly_fields = ("handler_name", "handler_data_preview", "handler_actions")
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

    @admin.display(description=_("Form handler"))
    def handler_name(self, obj):
        request = getattr(self, "_request", None)
        plugin = obj.get_plugin(request=request)
        if plugin and getattr(plugin, "name", None):
            return force_str(plugin.name)
        return obj.plugin_uid or "-"

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
        actions = []
        delete_action = None
        if obj.plugin_data:
            edit_url = (
                reverse(
                    "fobi.edit_form_handler_entry",
                    kwargs={"form_handler_entry_id": obj.pk},
                )
                + "?_popup=1"
            )
            actions.append(
                _build_action(
                    edit_url,
                    _("Edit"),
                    icon_name="edit",
                    attrs={
                        "id": f"change_fobi_handler_{obj.pk}",
                        "data-popup": "yes",
                    },
                    button_class=INLINE_ACTION_BUTTON_CLASS,
                )
            )
        delete_url = (
            reverse(
                "fobi.delete_form_handler_entry",
                kwargs={"form_handler_entry_id": obj.pk},
            )
            + "?_popup=1"
        )
        delete_action = _build_action(
            delete_url,
            _("Delete"),
            icon_name="delete",
            attrs={
                "id": f"delete_fobi_handler_{obj.pk}",
                "data-popup": "yes",
            },
            button_class=INLINE_ACTION_DANGER_CLASS,
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
                icon_name = None
                # T07: redirect "View entries" to admin filtered changelist
                if str(label) == str(_("View entries")):
                    action_url = (
                        reverse(
                            "admin:fobi_contrib_plugins_form_handlers_db_store_savedformdataentry_changelist"
                        )
                        + f"?form_entry__id__exact={obj.form_entry_id}"
                    )
                    icon_name = "visibility"
                elif str(label) == str(_("Export entries")):
                    icon_name = "download"
                actions.append(
                    _build_action(
                        action_url,
                        label,
                        icon_name=icon_name,
                        button_class=INLINE_ACTION_BUTTON_CLASS,
                    )
                )
        if delete_action:
            actions.append(delete_action)
        return format_html("{}", _render_action_buttons(actions))
