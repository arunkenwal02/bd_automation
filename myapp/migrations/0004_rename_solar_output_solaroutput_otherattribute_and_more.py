# Generated by Django 5.1.2 on 2024-11-06 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_solaroutput_windoutput'),
    ]

    operations = [
        migrations.RenameField(
            model_name='solaroutput',
            old_name='solar_output',
            new_name='otherattribute',
        ),
        migrations.RenameField(
            model_name='windoutput',
            old_name='wind_output',
            new_name='otherattribute',
        ),
    ]