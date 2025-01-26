# Generated by Django 5.0.6 on 2025-01-23 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0007_portfolio_units'),
    ]

    operations = [
        migrations.AddField(
            model_name='cash',
            name='units',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='portfolio',
            name='units',
            field=models.FloatField(default=1),
        ),
    ]
