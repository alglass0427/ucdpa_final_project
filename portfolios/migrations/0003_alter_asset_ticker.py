# Generated by Django 5.0.6 on 2025-02-02 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='ticker',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
