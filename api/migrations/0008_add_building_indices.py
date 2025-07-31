from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_alter_buildingimage_image'),  # Make sure this is the correct previous migration
    ]

    operations = [
        migrations.AddIndex(
            model_name='building',
            index=models.Index(fields=['name'], name='building_name_idx'),
        ),
        migrations.AddIndex(
            model_name='building',
            index=models.Index(fields=['address'], name='building_address_idx'),
        ),
        migrations.AddIndex(
            model_name='building',
            index=models.Index(fields=['company'], name='building_company_idx'),
        ),
    ]
