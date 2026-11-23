from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0009_colorgroup_alter_color_hex_value_color_group"),
    ]

    operations = [
        migrations.AddField(
            model_name="lens",
            name="name",
            field=models.CharField(
                blank=True, default="", max_length=500, verbose_name="Наименование"
            ),
        ),
        migrations.AddField(
            model_name="lens",
            name="sku",
            field=models.CharField(
                blank=True,
                db_index=True,
                default="",
                max_length=255,
                verbose_name="Артикул",
            ),
        ),
        migrations.AddField(
            model_name="lens",
            name="barcode",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="Штрихкод"
            ),
        ),
        migrations.AlterField(
            model_name="lens",
            name="dia",
            field=models.IntegerField(
                blank=True, db_index=True, null=True, verbose_name="Диаметр (DIA)"
            ),
        ),
    ]

