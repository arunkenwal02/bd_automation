# Generated by Django 5.1.2 on 2024-11-06 09:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_otherattributeoutput'),
    ]

    operations = [
        migrations.CreateModel(
            name='SolarOutput',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('solar_value', models.FloatField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('solar_output', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.otherattributeoutput')),
            ],
        ),
        migrations.CreateModel(
            name='WindOutput',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('wind_value', models.FloatField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('wind_output', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.otherattributeoutput')),
            ],
        ),
    ]
