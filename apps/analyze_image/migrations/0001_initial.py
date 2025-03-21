# Generated by Django 5.1.7 on 2025-03-20 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Imagen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('format', models.CharField(max_length=10, null=True)),
                ('header', models.TextField(blank=True, null=True)),
                ('exif', models.TextField(null=True)),
                ('fecha', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('content', models.ImageField(upload_to='media')),
            ],
        ),
    ]
