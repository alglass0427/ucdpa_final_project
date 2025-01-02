import csv
import os
from app import create_app, db
app = create_app()  # Assuming you have a factory function to create the app


# from app import db
from app.models import Asset  # Adjust this import based on your project structure


def import_assets_from_csv():
    csv_file_path = os.path.join('app/static', 'tickers.csv')

    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            ticker = row['ticker']
            company_name = row['company_name']
            industry = row['industry']
            
            # Create an instance of Asset model
            asset = Asset(ticker=ticker, company_name=company_name, industry=industry)
            
            # Add to session and commit
            db.session.add(asset)
        
        db.session.commit()
        print("Assets imported successfully!")


with app.app_context():
    assets  =  Asset.query.count()
    if  assets > 1: 
        print("Initial Assets Exist")
    else:
        import_assets_from_csv()
        print("Assets Added")

# if __name__ == "__main__":
#     import_assets_from_csv()

 