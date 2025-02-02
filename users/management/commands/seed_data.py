import random
from django.contrib.auth.models import User
from users.models import Profile
from portfolios.models import Portfolio, PortfolioAsset, Asset , Cash
from django.core.management.base import BaseCommand
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = "Seed data for User, Profile, Portfolio, and Assets."

    
    def handle(self, *args, **kwargs):

        first_names = [
    "Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona", "George", "Hannah", "Ian", "Julia",
    "Kevin", "Lena", "Michael", "Nora", "Oliver", "Paula", "Quinn", "Ryan", "Sophia", "Travis",
    "Uma", "Victor", "Wendy", "Xander", "Yasmin", "Zane", "Aaron", "Beatrice", "Caleb", "Delilah",
    "Edward", "Francesca", "Gabriel", "Hazel", "Isaac", "Jasmine", "Kyle", "Laura", "Matthew", "Natalie",
    "Oscar", "Penelope", "Quentin", "Riley", "Samuel", "Tina", "Ulysses", "Vanessa", "William", "Zoey"
]
        last_names = [
    "Smith", "Johnson", "Brown", "Williams", "Jones", "Miller", "Davis", "Garcia", "Wilson", "Martinez",
    "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White", "Lopez",
    "Lee", "Gonzalez", "Harris", "Clark", "Lewis", "Walker", "Hall", "Allen", "Young", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams", "Nelson", "Baker",
    "Carter", "Mitchell", "Perez", "Roberts", "Phillips", "Campbell", "Evans", "Edwards", "Collins", "Stewart"
]


        # Fetch all existing assets
        all_assets = list(Asset.objects.all())
        if not all_assets:
            self.stdout.write(self.style.ERROR("No assets available in the database. Seed the Asset table first."))
            return

        # Get the last user id to start from the next one
        last_user = User.objects.order_by('id').last()
        next_user_id = last_user.id + 1 if last_user else 1

        # Seed 50 users with profiles
        for i in range(25):

            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            # Create a user
            user = User.objects.create_user(
                username=f"user{next_user_id + i}",
                password="password123",
                email=f"user{next_user_id + i}@example.com",
                first_name=first_name,
                last_name=last_name,
                
            )

            # Profile creation handled by signal, no need to create manually

            # Create a portfolio for each user
            portfolio = Portfolio.objects.create(
                owner=user.profile,
                portfolio_desc=f"Portfolio {next_user_id + i + 1}"
            )
            profile = Profile.objects.get(user = user)
            
            Cash.objects.create(

                # user=user.profile,
                owner_content_type=ContentType.objects.get_for_model(Profile),
                portfolio=portfolio,
                balance=10000.0 , # Set the initial cash balance
                units = 100,
                owner_object_id = profile.id
            )
            # Add at least 2 other assets to the portfolio
            for _ in range(10):
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
