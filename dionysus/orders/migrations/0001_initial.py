# Generated by Django 5.1.5 on 2025-01-25 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Orders",
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
                ("table_numder", models.SmallIntegerField()),
                ("items", models.JSONField()),
                ("total_price", models.IntegerField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("wait", "order pending"),
                            ("done", "order ready"),
                            ("paid", "order paid"),
                        ],
                        max_length=4,
                    ),
                ),
            ],
        ),
    ]
