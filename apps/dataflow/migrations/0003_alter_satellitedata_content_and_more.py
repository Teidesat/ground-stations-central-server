# Generated by Django 5.1.7 on 2025-03-31 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataflow', '0002_satellitedata_raw_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='satellitedata',
            name='content',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='satellitedata',
            name='timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
