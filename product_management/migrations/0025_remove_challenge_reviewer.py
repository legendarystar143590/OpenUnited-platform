# Generated by Django 4.2.2 on 2024-04-26 20:53

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("product_management", "0024_bounty_data_migration"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="challenge",
            name="reviewer",
        ),
    ]
