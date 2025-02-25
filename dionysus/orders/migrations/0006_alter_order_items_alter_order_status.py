# Generated by Django 5.1.5 on 2025-01-27 13:20

import orders.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0005_alter_order_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="items",
            field=models.JSONField(validators=[orders.models.validate_items]),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("wait", "в ожидании"),
                    ("done", "готов"),
                    ("paid", "оплачено"),
                ],
                default="wait",
                max_length=4,
            ),
        ),
    ]
