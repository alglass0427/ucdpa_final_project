# Generated by Django 5.0.6 on 2024-12-23 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0002_alter_portfolioasset_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolioasset',
            name='no_of_trades',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]