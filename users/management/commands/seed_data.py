import random
from django.contrib.auth.models import User
from users.models import Profile
from portfolios.models import Portfolio, PortfolioAsset, Asset , Cash
from django.core.management.base import BaseCommand
from decimal import Decimal


class Command(BaseCommand):
    help = "Seed data for User, Profile, Portfolio, and Assets."

    def handle(self, *args, **kwargs):
        # Fetch all existing assets
        all_assets = list(Asset.objects.all())
        if not all_assets:
            self.stdout.write(self.style.ERROR("No assets available in the database. Seed the Asset table first."))
            return

        # Get the last user id to start from the next one
        last_user = User.objects.order_by('id').last()
        next_user_id = last_user.id + 1 if last_user else 1

        # Seed 50 users with profiles
        for i in range(10):
            # Create a user
            user = User.objects.create_user(
                username=f"user{next_user_id + i}",
                password="password123",
                email=f"user{next_user_id + i}@example.com"
            )

            # Profile creation handled by signal, no need to create manually

            # Create a portfolio for each user
            portfolio = Portfolio.objects.create(
                owner=user.profile,
                portfolio_desc=f"Portfolio {next_user_id + i + 1}"
            )

            # Add a "CASH" asset if it doesn't already exist in the portfolio
            # cash_asset = Asset.objects.filter(ticker="CASH").first()
            # if not cash_asset:
            #     cash_asset = Asset.objects.create(
            #         ticker="CASH",
            #         company_name="Cash Asset",
            #         industry="Cash"
            #     )



            # PortfolioAsset.objects.create(
            #     portfolio=portfolio,
            #     owner=user.profile,
            #     asset=cash_asset,
            #     holding_value=Decimal('10000'),
            #     no_of_shares=1,
            #     no_of_trades=1,
            #     comment="Initial cash balance."
            # )
            Cash.objects.create(
                user=user.profile,
                portfolio=portfolio,
                balance=10000.0  # Set the initial cash balance
            )
            # Add at least 2 other assets to the portfolio
            for _ in range(2):
                random_asset = random.choice(all_assets)
                PortfolioAsset.objects.create(
                    portfolio=portfolio,
                    owner=user.profile,
                    asset=random_asset,
                    holding_value=Decimal(random.uniform(500, 5000)),
                    no_of_shares=random.randint(1, 100),
                    buy_price=(Decimal(random.uniform(500, 5000))/random.randint(1, 100)),
                    no_of_trades=random.randint(1, 10),
                    comment=f"Holding for {random_asset.company_name}."
                )

            self.stdout.write(self.style.SUCCESS(f"Created user: {user.username} with portfolio and assets."))

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
