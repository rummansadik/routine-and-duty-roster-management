# Generated by Django 4.0.5 on 2022-06-30 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_alter_department_faculty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='credits',
            field=models.DecimalField(decimal_places=2, max_digits=4),
        ),
    ]
