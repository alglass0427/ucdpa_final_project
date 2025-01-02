# Generated by Django 5.0.6 on 2024-12-16 21:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ticker', models.CharField(max_length=10, unique=True)),
                ('company_name', models.CharField(max_length=255)),
                ('industry', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssetHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('open_price', models.FloatField(blank=True, null=True)),
                ('high_price', models.FloatField(blank=True, null=True)),
                ('low_price', models.FloatField(blank=True, null=True)),
                ('close_price', models.FloatField()),
                ('volume', models.IntegerField(blank=True, null=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='portfolios.asset')),
            ],
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('portfolio_id', models.AutoField(primary_key=True, serialize=False)),
                ('portfolio_desc', models.TextField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.profile')),
            ],
            options={
                'ordering': ['portfolio_desc'],
            },
        ),
        migrations.CreateModel(
            name='PortfolioAsset',
            fields=[
                ('portfolio_asset_seq_id', models.AutoField(primary_key=True, serialize=False)),
                ('buy_price', models.FloatField(blank=True, default=0, null=True)),
                ('no_of_shares', models.IntegerField(blank=True, default=0, null=True)),
                ('holding_value', models.FloatField(blank=True, default=0, null=True)),
                ('stop_loss', models.FloatField(blank=True, default=0, null=True)),
                ('cash_out', models.FloatField(blank=True, default=0, null=True)),
                ('comment', models.TextField(null=True)),
                ('svg_content', models.TextField(null=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolio_assets', to='portfolios.asset')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='portfolio_assets', to='users.profile')),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolio_assets', to='portfolios.portfolio')),
            ],
        ),
    ]