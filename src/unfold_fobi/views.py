"""
Unfold custom views wrapping fobi class-based views.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from unfold.views import UnfoldModelAdminViewMixin

from fobi.forms import FormElementEntryFormSet
from fobi.models import FormEntry, FormHandlerEntry
from fobi.views.class_based import (
    CreateFormEntryView as FobiCreateFormEntryView,
    EditFormEntryView as FobiEditFormEntryView,
)
from .forms import FormEntryFormWithCloneable
from .forms import FormEntryFormWithCloneable


class FormEntryCreateView(UnfoldModelAdminViewMixin, FobiCreateFormEntryView):
    title = _("Create form")
    permission_required = ("fobi.add_formentry",)
    form_class = FormEntryFormWithCloneable

    def get_form_class(self):
        return self.form_class
    form_class = FormEntryFormWithCloneable


class FormEntryEditView(UnfoldModelAdminViewMixin, FobiEditFormEntryView):
    title = _("Edit form")
    permission_required = ("fobi.change_formentry",)
    form_class = FormEntryFormWithCloneable

    def get_form_class(self):
        return self.form_class
    form_class = FormEntryFormWithCloneable

    class _FormHandlerChangeListAdmin(admin.ModelAdmin):
        list_display = ("handler_name", "handler_actions")
        list_display_links = None
        actions = None
        list_select_related = ("form_entry",)

        def __init__(self, model, admin_site, form_entry=None):
            super().__init__(model, admin_site)
            self.form_entry = form_entry
            self._request = None

        def get_queryset(self, request):
            qs = super().get_queryset(request)
            if self.form_entry:
                qs = qs.filter(form_entry=self.form_entry)
            return qs

        @admin.display(description=_("Handler"))
        def handler_name(self, obj):
            request = self._request
            plugin = obj.get_plugin(request=request)
            name = obj.plugin_name
            if callable(name):
                name = name()
            if obj.plugin_data and plugin:
                return format_html(
                    "{} <a class=\"ml-2 inline-flex items-center justify-center h-6 w-6 rounded-full border border-base-200 text-xs text-font-subtle-light dark:border-base-700 dark:text-font-subtle-dark\" href=\"javascript:;\" data-toggle=\"popover\" data-content=\"{}\" role=\"button\" title=\"{}\">?</a>",
                    name,
                    format_html("{}", plugin.plugin_data_repr or ""),
                    _("Info"),
                )
            return name

        @admin.display(description=_("Actions"))
        def handler_actions(self, obj):
            request = self._request
            plugin = obj.get_plugin(request=request)
            actions = []
            if obj.plugin_data:
                actions.append(
                    (
                        reverse_lazy(
                            "fobi.edit_form_handler_entry",
                            kwargs={"form_handler_entry_id": obj.pk},
                        ),
                        format_html(
                            "<span class=\"material-symbols-outlined text-base\">edit</span>"
                        ),
                        _("Edit"),
                        "border-base-200 bg-white text-font-default-light hover:border-base-300 hover:text-primary-600 dark:border-base-700 dark:bg-base-900 dark:text-font-default-dark dark:hover:text-primary-500",
                    )
                )
            actions.append(
                (
                    reverse_lazy(
                        "fobi.delete_form_handler_entry",
                        kwargs={"form_handler_entry_id": obj.pk},
                    ),
                    format_html(
                        "<span class=\"material-symbols-outlined text-base\">delete</span>"
                    ),
                    _("Delete"),
                    "border-red-200 bg-red-50 text-red-700 hover:border-red-300 hover:text-red-800 dark:border-red-600/40 dark:bg-red-500/10 dark:text-red-400",
                )
            )

            if plugin:
                for url, label, icon in plugin.get_custom_actions(
                    obj.form_entry, request
                ):
                    # T07: redirect "View entries" to admin filtered
                    # changelist instead of the frontend /fobi/<id>/ view.
                    if str(label) == str(_("View entries")):
                        url = (
                            reverse_lazy(
                                "admin:fobi_contrib_plugins_form_handlers_db_store_savedformdataentry_changelist"
                            )
                            + f"?form_entry__id__exact={obj.form_entry_id}"
                        )
                    actions.append(
                        (
                            url,
                            format_html("<span class=\"{}\"></span>", icon),
                            label,
                            "border-base-200 bg-white text-font-default-light hover:border-base-300 hover:text-primary-600 dark:border-base-700 dark:bg-base-900 dark:text-font-default-dark dark:hover:text-primary-500",
                        )
                    )

            return format_html(
                "<div class=\"flex flex-wrap gap-2\">{}</div>",
                format_html_join(
                    "",
                    "<a href=\"{}\" class=\"inline-flex items-center gap-2 rounded-default border px-3 py-1.5 text-sm font-medium shadow-xs transition {}\">{}{}</a>",
                    (
                        (url, class_name, mark_safe(icon_html), label)
                        for url, icon_html, label, class_name in actions
                    ),
                ),
            )

    def _build_handler_changelist(self, request):
        if not getattr(self, "object", None):
            return None
        handler_admin = self._FormHandlerChangeListAdmin(
            FormHandlerEntry, admin.site, form_entry=self.object
        )
        handler_admin._request = request
        changelist = ChangeList(
            request,
            FormHandlerEntry,
            handler_admin.list_display,
            handler_admin.list_display_links,
            handler_admin.list_filter,
            handler_admin.date_hierarchy,
            handler_admin.search_fields,
            handler_admin.list_select_related,
            handler_admin.list_per_page,
            handler_admin.list_max_show_all,
            handler_admin.list_editable,
            handler_admin,
            handler_admin.sortable_by,
            handler_admin.search_help_text,
        )
        changelist.formset = None
        return changelist

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        handler_changelist = self._build_handler_changelist(self.request)
        context["handler_changelist"] = handler_changelist
        # Use proxy model opts so Unfold breadcrumbs render as:
        # Unfold_Fobi → Forms (builder) → <form name>
        from .models import FormEntryProxy

        context["opts"] = FormEntryProxy._meta
        if getattr(self, "object", None):
            self.object.__class__ = FormEntryProxy
            context["original"] = self.object
        return context

    @staticmethod
    def _positions_are_valid(post_data):
        positions = []
        for key, value in post_data.items():
            if not key.endswith("-position"):
                continue
            try:
                positions.append(int(value))
            except (TypeError, ValueError):
                return False
        if not positions:
            return False
        total = len(positions)
        return sorted(positions) == list(range(1, total + 1))

    def post(self, request, *args, **kwargs):
        """
        Handle ordering posts with a custom success message.
        """
        if "ordering" not in request.POST:
            return super().post(request, *args, **kwargs)

        if not self._positions_are_valid(request.POST):
            messages.error(
                request,
                _(
                    "Errors occurred while trying to change the "
                    "elements ordering!"
                ),
            )
            return redirect(
                reverse_lazy(
                    "fobi.edit_form_entry",
                    kwargs={"form_entry_id": self.kwargs.get(self.pk_url_kwarg)},
                )
            )

        self.object = self.get_object(queryset=self._get_queryset(request))
        form_element_entry_formset = FormElementEntryFormSet(
            request.POST,
            request.FILES,
            queryset=self.object.formelemententry_set.all(),
        )
        try:
            if form_element_entry_formset.is_valid():
                form_element_entry_formset.save()
                return redirect(
                    reverse_lazy(
                        "fobi.edit_form_entry",
                        kwargs={"form_entry_id": self.object.pk},
                    )
                )
            messages.error(
                request,
                _(
                    "Errors occurred while trying to change the "
                    "elements ordering!"
                ),
            )
            return redirect(
                reverse_lazy(
                    "fobi.edit_form_entry",
                    kwargs={"form_entry_id": self.object.pk},
                )
            )
        except MultiValueDictKeyError:
            messages.error(
                request,
                _(
                    "Errors occurred while trying to change the "
                    "elements ordering!"
                ),
            )
            return redirect(
                reverse_lazy(
                    "fobi.edit_form_entry",
                    kwargs={"form_entry_id": self.object.pk},
                )
            )

        return super().post(request, *args, **kwargs)


class FormWizardsDashboardView(UnfoldModelAdminViewMixin, RedirectView):
    title = _("Wizards")
    permission_required = ("fobi.view_formwizardentry",)
    pattern_name = "fobi.form_wizards_dashboard"


class FormEntryImportView(UnfoldModelAdminViewMixin, RedirectView):
    title = _("Import form")
    permission_required = ("fobi.add_formentry",)
    pattern_name = "fobi.import_form_entry"


def normalize_field_choices(field, field_name):
    try:
        optgroups = field.widget.optgroups(field_name, field.initial)
    except Exception:
        return _fallback_choices(field.choices)

    normalized = []
    for group_label, group_choices, _index in optgroups:
        for option in group_choices:
            payload = {
                'value': option.get('value'),
                'label': option.get('label'),
            }
            if group_label not in (None, ''):
                payload['group'] = group_label
            normalized.append(payload)
    return normalized


def _fallback_choices(choices):
    normalized = []
    for choice in choices:
        value, label = _coerce_choice_pair(choice)
        if isinstance(label, (list, tuple)):
            for subchoice in label:
                subvalue, sublabel = _coerce_choice_pair(subchoice)
                normalized.append({
                    'value': subvalue,
                    'label': sublabel,
                    'group': value,
                })
        else:
            normalized.append({'value': value, 'label': label})
    return normalized


def _coerce_choice_pair(choice):
    if isinstance(choice, (list, tuple)):
        if len(choice) >= 2:
            return choice[0], choice[1]
        if len(choice) == 1:
            return choice[0], choice[0]
    return choice, choice


@api_view(['GET'])
def get_form_fields(request, slug):
    """
    Custom API endpoint to get form fields structure for frontend rendering.

    This is an alternative to using OPTIONS /api/fobi-form-entry/{slug}/
    which should also return form metadata in the 'actions' -> 'PUT' section.

    Usage:
    - GET /api/fobi-form-fields/{slug}/ - Returns form fields structure
    - OPTIONS /api/fobi-form-entry/{slug}/ - Returns form metadata including PUT schema
    """
    try:
        form_entry = FormEntry.objects.get(slug=slug, is_public=True)

        # Import lazily to avoid DRF compatibility errors at startup.
        from fobi.contrib.apps.drf_integration.dynamic import get_declared_fields

        # Get the dynamic form fields from fobi DRF integration.
        # get_declared_fields returns a tuple: (fields_dict, metadata_dict)
        fields_result = get_declared_fields(form_entry)

        # Handle both tuple and dict return types
        if isinstance(fields_result, tuple):
            fields = fields_result[0]  # First element is the fields dictionary
        else:
            fields = fields_result

        # Convert fields to a more frontend-friendly format
        form_structure = {
            'id': form_entry.id,
            'slug': form_entry.slug,
            'title': form_entry.name,
            'fields': []
        }

        # Extract field information
        for field_name, field in fields.items():
            field_info = {
                'name': field_name,
                'type': field.__class__.__name__,
                'label': getattr(field, 'label', field_name),
                'required': getattr(field, 'required', False),
                'help_text': getattr(field, 'help_text', ''),
            }

            # Add field-specific attributes
            if hasattr(field, 'choices') and field.choices:
                field_info['choices'] = normalize_field_choices(field, field_name)

            if hasattr(field, 'min_value'):
                field_info['min_value'] = field.min_value
            if hasattr(field, 'max_value'):
                field_info['max_value'] = field.max_value
            if hasattr(field, 'min_length'):
                field_info['min_length'] = field.min_length
            if hasattr(field, 'max_length'):
                field_info['max_length'] = field.max_length

            form_structure['fields'].append(field_info)

        return Response(form_structure)
    except FormEntry.DoesNotExist:
        return Response({'error': _('Form not found')}, status=404)
