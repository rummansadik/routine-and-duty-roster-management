# Generated by Django 4.0.5 on 2022-11-19 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0028_alter_student_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='routine',
            name='session',
            field=models.IntegerField(default=2020),
            preserve_default=False,
        ),
    ]
