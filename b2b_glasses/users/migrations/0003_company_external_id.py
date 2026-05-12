# Generated manually for adding external_id to Company

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_telegramlinktoken_options_alter_user_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="external_id",
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                unique=True,
                verbose_name="Внешний ID",
            ),
        ),
    ]
