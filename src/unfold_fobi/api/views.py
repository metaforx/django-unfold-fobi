"""DRF API views for unfold_fobi."""

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.forms.fields import EmailField
from django.middleware.csrf import get_token
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from fobi.contrib.apps.drf_integration.dynamic import get_declared_fields
from fobi.models import FormEntry
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.response import Response


def normalize_field_choices(field, field_name):
    try:
        optgroups = field.widget.optgroups(field_name, field.initial)
    except Exception:
        return _fallback_choices(field.choices)

    normalized = []
    for group_label, group_choices, _index in optgroups:
        for option in group_choices:
            payload = {
                "value": option.get("value"),
                "label": option.get("label"),
            }
            if group_label not in (None, ""):
                payload["group"] = group_label
            normalized.append(payload)
    return normalized


def _fallback_choices(choices):
    normalized = []
    for choice in choices:
        value, label = _coerce_choice_pair(choice)
        if isinstance(label, (list, tuple)):
            for subchoice in label:
                subvalue, sublabel = _coerce_choice_pair(subchoice)
                normalized.append(
                    {
                        "value": subvalue,
                        "label": sublabel,
                        "group": value,
                    }
                )
        else:
            normalized.append({"value": value, "label": label})
    return normalized


def _coerce_choice_pair(choice):
    if isinstance(choice, (list, tuple)):
        if len(choice) >= 2:
            return choice[0], choice[1]
        if len(choice) == 1:
            return choice[0], choice[0]
    return choice, choice


def _build_widget_map(form_entry):
    """Map field names to their Django widget class names."""
    widget_map = {}
    for element_entry in form_entry.formelemententry_set.all().order_by("position"):
        try:
            plugin = element_entry.get_plugin(request=None)
            if not plugin:
                continue
            for item in plugin.get_form_field_instances():
                name = item[0]
                field_cls = item[1] if len(item) > 1 else None
                kwargs = item[2] if len(item) > 2 else {}
                widget = kwargs.get("widget")
                if widget is not None:
                    widget_name = widget.__class__.__name__
                elif field_cls is not None:
                    # Plugin omitted widget; instantiate field to get default.
                    safe_kwargs = {k: v for k, v in kwargs.items() if k != "widget"}
                    instance = field_cls(**safe_kwargs)
                    widget_name = instance.widget.__class__.__name__
                else:
                    continue
                # Fobi's email plugin uses TextInput(type=email) instead of
                # Django's EmailInput; resolve to the semantic widget name.
                if widget_name == "TextInput" and field_cls is not None and issubclass(field_cls, EmailField):
                    widget_name = "EmailInput"
                widget_map[name] = widget_name
        except Exception:
            continue
    return widget_map


def _can_preview(user, form_entry):
    """Check if a user can preview a non-public form."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if not user.has_perm("fobi.view_formentry"):
        return False
    if not django_apps.is_installed("unfold_fobi.contrib.sites"):
        # if sites framework is not used we can pass further checks
        return True

    # Site-scope check
    from unfold_fobi.contrib.sites.conf import get_sites_for_user_func

    try:
        form_sites = form_entry.site_binding.sites
    except (AttributeError, ObjectDoesNotExist):
        return False
    user_sites = get_sites_for_user_func()(user)
    return form_sites.filter(pk__in=user_sites).exists()


@api_view(["GET"])
@never_cache
def get_form_fields(request, slug):
    """
    Return form fields for frontend rendering with permission (preview mode).
    """
    try:
        form_entry = FormEntry.objects.get(slug=slug)
    except FormEntry.DoesNotExist:
        raise NotFound(_("Form not found"))

    is_preview = False
    if not form_entry.is_public:
        if _can_preview(request.user, form_entry):
            is_preview = True
        else:
            raise NotFound(_("Form not found"))

    fields_result = get_declared_fields(form_entry)

    if isinstance(fields_result, tuple):
        fields = fields_result[0]
    else:
        fields = fields_result

    widget_map = _build_widget_map(form_entry)

    form_structure = {
        "id": form_entry.id,
        "slug": form_entry.slug,
        "title": form_entry.name,
        "is_active": form_entry.is_active,
        "is_preview": is_preview,
        "active_date_from": form_entry.active_date_from,
        "active_date_to": form_entry.active_date_to,
        "success_page_title": form_entry.success_page_title or "",
        "success_page_message": form_entry.success_page_message or "",
        "csrf_token": get_token(request),
        "fields": [],
    }

    for field_name, field in fields.items():
        field_info = {
            "name": field_name,
            "type": field.__class__.__name__,
            "widget": widget_map.get(field_name),
            "label": getattr(field, "label", field_name),
            "required": getattr(field, "required", False),
            "help_text": getattr(field, "help_text", ""),
        }

        if hasattr(field, "choices") and field.choices:
            field_info["choices"] = normalize_field_choices(field, field_name)

        if hasattr(field, "min_value"):
            field_info["min_value"] = field.min_value
        if hasattr(field, "max_value"):
            field_info["max_value"] = field.max_value
        if hasattr(field, "min_length"):
            field_info["min_length"] = field.min_length
        if hasattr(field, "max_length"):
            field_info["max_length"] = field.max_length

        form_structure["fields"].append(field_info)

    return Response(form_structure)
