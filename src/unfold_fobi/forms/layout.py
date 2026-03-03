"""Layout helpers for Unfold crispy forms."""

from crispy_forms.layout import Column, Row


def align_visibility_fields_in_layout(form):
    """Ensure 'is_public' and 'is_cloneable' fields are adjacent in the layout and styled together."""

    helper = getattr(form, "helper", None)
    layout = getattr(helper, "layout", None) if helper else None
    if not layout:
        return

    target_fieldset = None
    for item in layout:
        if hasattr(item, "fields"):
            target_fieldset = item
            break

    if not target_fieldset:
        return

    fields = list(getattr(target_fieldset, "fields", []))
    if "is_public" not in fields or "is_cloneable" not in fields:
        return

    new_fields = []
    seen_cloneable = False
    for field in fields:
        if field == "is_public":
            new_fields.append(
                Row(
                    Column("is_public"),
                    Column("is_cloneable"),
                    css_class=(
                        "datetime flex flex-col gap-2 max-w-2xl "
                        "lg:flex-row lg:group-[.field-row]:flex-row "
                        "lg:group-[.field-row]:items-center "
                        "lg:group-[.field-tabular]:flex-row "
                        "lg:group-[.field-tabular]:items-center"
                    ),
                )
            )
            seen_cloneable = True
            continue
        if field == "is_cloneable":
            if seen_cloneable:
                continue
        new_fields.append(field)

    target_fieldset.fields = new_fields
