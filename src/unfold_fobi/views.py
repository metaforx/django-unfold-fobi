"""
Unfold custom views — T10 POC simplification.

Only redirect views and the DRF API endpoint remain.
The custom builder edit/create views are replaced by native admin change/add.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from unfold.views import UnfoldModelAdminViewMixin

from fobi.models import FormEntry


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
    """
    try:
        form_entry = FormEntry.objects.get(slug=slug, is_public=True)

        from fobi.contrib.apps.drf_integration.dynamic import get_declared_fields

        fields_result = get_declared_fields(form_entry)

        if isinstance(fields_result, tuple):
            fields = fields_result[0]
        else:
            fields = fields_result

        form_structure = {
            'id': form_entry.id,
            'slug': form_entry.slug,
            'title': form_entry.name,
            'fields': []
        }

        for field_name, field in fields.items():
            field_info = {
                'name': field_name,
                'type': field.__class__.__name__,
                'label': getattr(field, 'label', field_name),
                'required': getattr(field, 'required', False),
                'help_text': getattr(field, 'help_text', ''),
            }

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
