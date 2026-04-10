import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("cms", "0001_initial"),
        ("fobi", "0015_auto_20180130_0013"),
    ]

    operations = [
        migrations.CreateModel(
            name="FobiFormPluginModel",
            fields=[
                (
                    "cmsplugin_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="cms.cmsplugin",
                    ),
                ),
                (
                    "form_entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="fobi.formentry",
                        verbose_name="Form",
                    ),
                ),
            ],
            options={
                "verbose_name": "Fobi form plugin",
                "verbose_name_plural": "Fobi form plugins",
            },
            bases=("cms.cmsplugin",),
        ),
    ]
