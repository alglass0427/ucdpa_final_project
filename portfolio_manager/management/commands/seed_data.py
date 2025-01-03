import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Profile
from portfolios.models import Portfolio, PortfolioAsset, Asset
from django.db import transaction

# Define some sample data for assets
ASSET_DATA = [
    {"ticker": "AAPL", "industry": "Technology"},
    {"ticker": "GOOGL", "industry": "Technology"},
    {"ticker": "TSLA", "industry": "Automotive"},
    {"ticker": "MSFT", "industry": "Technology"},
    {"ticker": "AMZN", "industry": "E-commerce"},
    {"ticker": "JPM", "industry": "Finance"},
    {"ticker": "DIS", "industry": "Entertainment"},
    {"ticker": "NFLX", "industry": "Streaming"},
    {"ticker": "XOM", "industry": "Energy"},
    {"ticker": "PFE", "industry": "Pharmaceuticals"},
]

class Command(BaseCommand):
    help = "Seed the database with users, portfolios, and assets."

    def create_assets(self):
        """Create assets if they don't already exist."""
        for asset_data in ASSET_DATA:
            Asset.objects.get_or_create(
                ticker=asset_data["ticker"],
                defaults={"industry": asset_data["industry"]},
            )

    def create_users_with_portfolios(self):
        """Create 50 users with portfolios and assets."""
        self.create_assets()  # Ensure assets exist
        assets = list(Asset.objects.all())

        with transaction.atomic():
            for i in range(1, 51):
                # Create user
                username = f"user{i}"
                email = f"user{i}@example.com"
                user = User.objects.create_user(username=username, email=email, password="password123")
                
                # Create user profile
                profile = Profile.objects.create(user=user)

                # Create at least 1 portfolio for each user
                for j in range(1, random.randint(2, 4)):  # 1 to 3 portfolios
                    portfolio = Portfolio.objects.create(
                        owner=profile,
                        portfolio_desc=f"Portfolio {j} for {username}",
                    )

                    # Add at least 2 assets to each portfolio
                    for _ in range(random.randint(2, 5)):  # 2 to 4 assets
                        asset = random.choice(assets)
                        PortfolioAsset.objects.create(
                            portfolio=portfolio,
                            asset=asset,
                            no_of_trades=random.randint(1, 10),
                            buy_price=round(random.uniform(50, 500), 2),
                            holding_value=round(random.uniform(1000, 5000), 2),
                        )

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating users, portfolios, and assets...")
        self.create_users_with_portfolios()
        self.stdout.write(self.style.SUCCESS("Seeding completed!"))
