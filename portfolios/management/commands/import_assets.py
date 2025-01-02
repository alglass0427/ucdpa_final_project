import csv
import os
from django.core.management.base import BaseCommand
from portfolios.models import Asset  # Replace 'myapp' with your app name
from django.apps import apps

class Command(BaseCommand):
    help = 'Import assets from a CSV file'

    def handle(self, *args, **kwargs):
        app_path = apps.get_app_config('portfolios').path 
        csv_file_path = os.path.join(app_path, 'tickers.csv')   # Adjust the path as needed
        print(f"csv_file_path :  {csv_file_path}")
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f"File '{csv_file_path}' does not exist."))
            return

        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)

            assets_added = 0
            for row in reader:
                ticker = row['ticker']
                company_name = row['company_name']
                industry = row['industry']

                # Check if the asset already exists
                if not Asset.objects.filter(ticker=ticker).exists():
                    asset = Asset(ticker=ticker, company_name=company_name, industry=industry)
                    asset.save()
                    assets_added += 1

            if assets_added > 0:
                self.stdout.write(self.style.SUCCESS(f"{assets_added} assets imported successfully!"))
            else:
                self.stdout.write(self.style.WARNING("No new assets were imported."))
