# Generated by Django 5.1.3 on 2024-12-10 12:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mrtstations', '0003_line_rail_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mrtstation',
            name='rail_type',
        ),
    ]
