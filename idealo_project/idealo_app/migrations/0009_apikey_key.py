# Generated by Django 4.2.4 on 2023-08-21 23:01

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('idealo_app', '0008_rename_timestamp_apikey_expiry'),
    ]

    operations = [
        migrations.AddField(
            model_name='apikey',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
