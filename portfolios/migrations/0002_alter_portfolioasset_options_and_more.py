# Generated by Django 5.0.6 on 2024-12-23 21:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='portfolioasset',
            options={'ordering': ['portfolio']},
        ),
        migrations.RenameField(
            model_name='portfolio',
            old_name='portfolio_id',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='portfolioasset',
            old_name='portfolio_asset_seq_id',
            new_name='id',
        ),
    ]
