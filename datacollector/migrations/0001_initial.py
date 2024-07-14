# Generated by Django 5.0.7 on 2024-07-14 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ResaleTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.CharField(max_length=7)),
                ('town', models.CharField(max_length=100)),
                ('flat_type', models.CharField(max_length=50)),
                ('block', models.CharField(max_length=4)),
                ('street_name', models.CharField(max_length=100)),
                ('storey_range', models.CharField(max_length=10)),
                ('floor_area_sqm', models.PositiveSmallIntegerField()),
                ('flat_model', models.CharField(max_length=50)),
                ('lease_commence_date', models.CharField(max_length=4)),
                ('remaining_lease', models.CharField(max_length=100)),
                ('resale_price', models.IntegerField()),
            ],
        ),
    ]