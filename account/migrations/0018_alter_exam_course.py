# Generated by Django 4.0.5 on 2022-08-12 10:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_room_shift'),
        ('account', '0017_alter_teacher_total_creadits'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='dashboard.course'),
        ),
    ]
