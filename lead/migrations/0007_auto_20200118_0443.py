# Generated by Django 2.2.9 on 2020-01-18 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0006_auto_20200118_0441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='phonenumber',
            field=models.CharField(max_length=100),
        ),
    ]
