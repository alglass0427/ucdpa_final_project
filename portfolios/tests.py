from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Portfolio, Asset, PortfolioAsset, Cash
from users.models import Profile,Message
from users.models import Group
from django.urls import reverse
import json
import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.contenttypes.models import ContentType
import random
from decimal import Decimal
from .utils import get_latest_portfolio_prices , get_latest_price


class PortfolioViewsTest(TestCase):

    

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='password123'
        )
        self.profile, created = Profile.objects.get_or_create(user=self.user)

        self.manager_group, created = Group.objects.get_or_create(name='Manager')
        self.investor_group, created = Group.objects.get_or_create(name='Investor')
        self.profile.group = self.manager_group
        self.profile.save()
        
        self.profile = Profile.objects.get(user = self.user)
        self.portfolio, created = Portfolio.objects.get_or_create(owner=self.user.profile)

        assets_data = [
                ("AAPL", "Apple Inc.", "Consumer Electronics", False),
                ("MSFT", "Microsoft Corp.", "Software - Infrastructure", False),
                ("NVDA", "NVIDIA Corp.", "Semiconductors", False),
                ("AMZN", "Amazon.com, Inc.", "Internet Retail", False),
                ("GOOGL", "Alphabet Inc.", "Internet Content & Information", False),
                ("GOOG", "Alphabet Inc.", "Internet Content & Information", False),
                ("META", "Meta Platforms, Inc.", "Internet Content & Information", False),
                ("LLY", "Eli Lilly and Co.", "Drug Manufacturers - General", False),
                ("TSLA", "Tesla, Inc.", "Auto Manufacturers", False),
                ("AVGO", "Broadcom Inc.", "Semiconductors", False),
                ("WMT", "Walmart Inc.", "Discount Stores", False),
                ("JPM", "JPMorgan Chase & Co.", "Banks - Diversified", False),
                ("UNH", "UnitedHealth Group Inc.", "Healthcare Plans", False),
                ("V", "Visa Inc.", "Credit Services", False),
                ("XOM", "Exxon Mobil Corp.", "Oil & Gas Integrated", False),
                ("MA", "Mastercard Inc.", "Credit Services", False),
            ]


        Asset.objects.bulk_create([
            Asset(ticker=ticker, company_name=company, industry=industry, is_portfolio=is_portfolio)
            for ticker, company, industry, is_portfolio in assets_data
        ])

        Cash.objects.create(

                # user=user.profile,
                owner_content_type=ContentType.objects.get_for_model(Profile),
                portfolio=self.portfolio,
                balance=10000.0 , # Set the initial cash balance
                units = 100,
                owner_object_id = self.profile.id
            )
        all_assets = list(Asset.objects.all())  
            # Add at least 2 other assets to the portfolio
        for _ in range(10):
            random_asset = random.choice(all_assets)
            PortfolioAsset.objects.create(
                portfolio=self.portfolio,
                owner=self.user.profile,
                asset=random_asset,
                holding_value=Decimal(random.uniform(500, 5000)),
                no_of_shares=random.randint(1, 100),
                buy_price=(Decimal(random.uniform(500, 5000))/random.randint(1, 100)),
                no_of_trades=random.randint(1, 10),
                comment=f"Holding for {random_asset.company_name}."
            )

    def test_yahoo_connect(self):
        #get_latest_price ("AAPL",1,''):
        result = get_latest_price("AAPL", 1,"")
        self.assertTrue(result > 0)
    
    def test_yahoo_connect_mult(self):
        #get_latest_price ("AAPL",1,''):
        result = get_latest_portfolio_prices(self.portfolio.id)
        print (result)


        self.assertIsInstance(result, dict) 

    def test_asset_count(self):
        self.assertEqual(Asset.objects.count(), 17)

    def test_get_specific_asset(self):
        """Retrieve an asset by ticker"""
        asset = Asset.objects.get(ticker="AAPL")
        self.assertEqual(asset.company_name, "Apple Inc.")

    