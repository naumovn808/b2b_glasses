from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_alter_order_options_customorder"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="id_1c",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=100,
                null=True,
                verbose_name="ID заказа в 1С",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="doc_number_1c",
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name="Номер документа в 1С",
            ),
        ),
    ]

