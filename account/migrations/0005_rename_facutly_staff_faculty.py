# Generated by Django 4.0.5 on 2022-06-27 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_routine_facutly'),
    ]

    operations = [
        migrations.RenameField(
            model_name='staff',
            old_name='facutly',
            new_name='faculty',
        ),
    ]
