# Generated by Django 3.2.12 on 2022-06-24 16:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_scrapyd', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spiderstats',
            name='log_hourly_error_rate',
        ),
        migrations.RemoveField(
            model_name='spiderstats',
            name='memory_use',
        ),
    ]