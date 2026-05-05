import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("unfold_fobi", "0001_initial"),
        ("unfold_fobi_cms", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fobiformpluginmodel",
            name="form_entry",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="unfold_fobi.formentryproxy",
                verbose_name="Form",
            ),
        ),
    ]
