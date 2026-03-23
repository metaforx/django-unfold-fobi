import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("sites", "0002_alter_domain_unique"),
        ("unfold_fobi", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FobiFormSiteBinding",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "form_entry",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="site_binding",
                        to="unfold_fobi.formentryproxy",
                        verbose_name="Form",
                    ),
                ),
                (
                    "sites",
                    models.ManyToManyField(
                        blank=True,
                        related_name="fobi_form_bindings",
                        to="sites.site",
                        verbose_name="Sites",
                    ),
                ),
            ],
            options={
                "verbose_name": "Form site binding",
                "verbose_name_plural": "Form site bindings",
            },
        ),
    ]
