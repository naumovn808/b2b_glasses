from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_company_external_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="inn",
            field=models.CharField(
                blank=True, default="", max_length=64, verbose_name="ИНН"
            ),
        ),
        migrations.AddField(
            model_name="company",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Активна"),
        ),
        migrations.AddField(
            model_name="company",
            name="partner_id_1c",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=255,
                null=True,
                verbose_name="ID партнера в 1С",
            ),
        ),
        migrations.AddField(
            model_name="company",
            name="partner_name",
            field=models.CharField(
                blank=True,
                default="",
                max_length=255,
                verbose_name="Наименование партнера",
            ),
        ),
        migrations.AddField(
            model_name="company",
            name="head_partner_id_1c",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=255,
                null=True,
                verbose_name="ID головного партнера в 1С",
            ),
        ),
        migrations.AddField(
            model_name="company",
            name="head_partner_name",
            field=models.CharField(
                blank=True,
                default="",
                max_length=255,
                verbose_name="Наименование головного партнера",
            ),
        ),
    ]

