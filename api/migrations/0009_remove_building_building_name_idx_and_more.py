# Generated by Django 5.2.3 on 2025-07-31 17:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_add_building_indices'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='building',
            name='building_name_idx',
        ),
        migrations.RemoveIndex(
            model_name='building',
            name='building_address_idx',
        ),
        migrations.RemoveIndex(
            model_name='building',
            name='building_company_idx',
        ),
    ]
