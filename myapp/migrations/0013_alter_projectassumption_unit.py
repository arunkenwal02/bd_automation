# Generated by Django 5.1.2 on 2024-11-10 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_alter_projectassumption_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectassumption',
            name='unit',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
