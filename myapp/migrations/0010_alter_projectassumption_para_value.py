# Generated by Django 5.1.2 on 2024-11-08 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_alter_projectassumption_parameter_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectassumption',
            name='para_value',
            field=models.FloatField(blank=True),
        ),
    ]