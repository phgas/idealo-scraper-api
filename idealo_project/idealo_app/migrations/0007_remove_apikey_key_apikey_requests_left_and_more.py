# Generated by Django 4.2.4 on 2023-08-21 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('idealo_app', '0006_remove_apikey_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apikey',
            name='key',
        ),
        migrations.AddField(
            model_name='apikey',
            name='requests_left',
            field=models.IntegerField(default=1000, editable=False),
        ),
        migrations.AddField(
            model_name='apikey',
            name='timestamp',
            field=models.BigIntegerField(default=None),
        ),
    ]
