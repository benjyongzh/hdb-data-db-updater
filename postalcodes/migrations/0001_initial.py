# Generated by Django 5.0.7 on 2024-07-20 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PostalCodeAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('block', models.CharField(max_length=4)),
                ('street_name', models.CharField(max_length=100)),
                ('postal_code', models.CharField(max_length=6)),
            ],
        ),
    ]