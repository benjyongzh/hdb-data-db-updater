# Generated by Django 5.0.7 on 2024-08-12 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TablesLastUpdated',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table', models.CharField(max_length=255)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
