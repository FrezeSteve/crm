# Generated by Django 2.2.9 on 2020-01-17 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0002_auto_20200117_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='trashed',
            field=models.BooleanField(default=False),
        ),
    ]
