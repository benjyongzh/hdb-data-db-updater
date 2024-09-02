# Generated by Django 5.1 on 2024-09-02 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('postalcodes', '0004_alter_buildinggeometrypolygon_postal_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postalcodeaddress',
            name='block',
            field=models.CharField(db_index=True, max_length=4),
        ),
        migrations.AlterField(
            model_name='postalcodeaddress',
            name='street_name',
            field=models.CharField(db_index=True, max_length=100),
        ),
    ]
