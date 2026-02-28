from django.db import transaction
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from fobi.models import (
    FormElementEntry,
    FormEntry,
    FormFieldsetEntry,
    FormHandlerEntry,
)


def clone_form_entry(source):
    """
    Clone a FormEntry along with its fieldsets, elements, and handlers.

    Returns the newly created FormEntry.
    """
    with transaction.atomic():
        name, slug = _generate_clone_name_slug(source)
        new_form = FormEntry.objects.create(
            user=source.user,
            name=name,
            slug=slug,
            title=source.title,
            is_public=source.is_public,
            active_date_from=source.active_date_from,
            active_date_to=source.active_date_to,
            inactive_page_title=source.inactive_page_title,
            inactive_page_message=source.inactive_page_message,
            is_cloneable=source.is_cloneable,
            success_page_title=source.success_page_title,
            success_page_message=source.success_page_message,
            action=source.action,
        )

        fieldset_map = {}
        for fieldset in FormFieldsetEntry.objects.filter(form_entry=source):
            new_fieldset = FormFieldsetEntry.objects.create(
                form_entry=new_form,
                name=fieldset.name,
                is_repeatable=fieldset.is_repeatable,
            )
            fieldset_map[fieldset.pk] = new_fieldset

        elements = []
        for element in FormElementEntry.objects.filter(form_entry=source).order_by(
            "position", "pk"
        ):
            elements.append(
                FormElementEntry(
                    form_entry=new_form,
                    plugin_uid=element.plugin_uid,
                    plugin_data=element.plugin_data,
                    form_fieldset_entry=fieldset_map.get(
                        element.form_fieldset_entry_id
                    ),
                    position=element.position,
                )
            )
        if elements:
            FormElementEntry.objects.bulk_create(elements)

        handlers = []
        for handler in FormHandlerEntry.objects.filter(form_entry=source).order_by(
            "plugin_uid", "pk"
        ):
            if handler.plugin_uid == "db_store":
                continue
            handlers.append(
                FormHandlerEntry(
                    form_entry=new_form,
                    plugin_uid=handler.plugin_uid,
                    plugin_data=handler.plugin_data,
                )
            )
        if handlers:
            FormHandlerEntry.objects.bulk_create(handlers)

        # Ensure exactly one db_store handler if the source had one.
        if FormHandlerEntry.objects.filter(
            form_entry=source, plugin_uid="db_store"
        ).exists():
            FormHandlerEntry.objects.get_or_create(
                form_entry=new_form,
                plugin_uid="db_store",
            )

        return new_form


def _generate_clone_name_slug(source):
    base_name = _("Copy of {name}").format(name=source.name)
    name = base_name
    suffix = 2
    while FormEntry.objects.filter(user=source.user, name=name).exists():
        name = _("{base} ({suffix})").format(base=base_name, suffix=suffix)
        suffix += 1

    slug_base = slugify(name) or f"{source.slug}-copy"
    slug = slug_base
    suffix = 2
    while FormEntry.objects.filter(slug=slug).exists():
        slug = f"{slug_base}-{suffix}"
        suffix += 1

    return name, slug
