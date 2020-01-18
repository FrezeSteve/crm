# Generated by Django 2.2.9 on 2020-01-18 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead', '0005_reminder_trash'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='Description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='phonenumber',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
