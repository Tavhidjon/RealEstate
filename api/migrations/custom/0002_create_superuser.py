from django.db import migrations
from django.conf import settings


def create_superuser(apps, schema_editor):
    """
    Create a default superuser for the application
    """
    # We can't import the AppUser model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    AppUser = apps.get_model('api', 'AppUser')
    
    # Create a superuser with these credentials
    # In production, you should create a superuser using the createsuperuser command
    # and remove this migration
    admin_user = AppUser(
        username='admin',
        email='admin@example.com',
        is_staff=True,
        is_superuser=True,
        is_verified=True
    )
    # set_password is not available in migrations, use a plain password for now
    # and change it after applying migrations
    admin_user.set_password('admin123')
    admin_user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),  # Make sure this matches your first migration
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
