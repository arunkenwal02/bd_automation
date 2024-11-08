# Generated by Django 5.1.2 on 2024-11-06 09:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OtherAttributeOutput',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ghs_capacity_tonnes', models.FloatField()),
                ('electrolyser_capacity_mw', models.FloatField()),
                ('bid_capacity_mw', models.FloatField()),
                ('nh3_production_tonnes', models.FloatField()),
                ('carbon_intensity_h2', models.FloatField()),
                ('carbon_intensity_nh3', models.FloatField()),
                ('iex_sale_percentage', models.FloatField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.inputparameters')),
            ],
        ),
    ]
