"""Create FobiFormSiteBinding rows for all existing forms.

When the optional Sites app is enabled on a project that already has
forms, this migration ensures every FormEntry gets a binding row.
If a default site (id=1) exists, it is assigned to each new binding
so forms are not invisible to non-superusers.
"""

from django.db import migrations


def seed_form_site_bindings(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    FormEntry = apps.get_model("fobi", "FormEntry")
    FobiFormSiteBinding = apps.get_model("unfold_fobi_sites", "FobiFormSiteBinding")

    default_site = Site.objects.filter(id=1).first()

    for form_entry_id in FormEntry.objects.values_list("id", flat=True).iterator():
        binding, created = FobiFormSiteBinding.objects.get_or_create(
            form_entry_id=form_entry_id
        )
        if created and default_site and not binding.sites.exists():
            binding.sites.add(default_site)


class Migration(migrations.Migration):
    dependencies = [
        ("unfold_fobi_sites", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            seed_form_site_bindings,
            migrations.RunPython.noop,
        ),
    ]
