# Generated by Django 5.1.2 on 2024-11-12 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0014_solar_profile_wind_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wind_profile',
            name='unit_wind1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='wind_profile',
            name='unit_wind2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='wind_profile',
            name='unit_wind3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='wind_profile',
            name='unit_wind4',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='wind_profile',
            name='unit_wind5',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
