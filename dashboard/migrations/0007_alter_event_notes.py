# Generated by Django 4.0.5 on 2022-07-26 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='notes',
            field=models.TextField(blank=True),
        ),
    ]
