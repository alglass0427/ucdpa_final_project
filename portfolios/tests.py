from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Portfolio, Asset, PortfolioAsset
from users.models import Profile,Message
from users.models import Group
from django.urls import reverse
import json
import pytest
from django.urls import reverse
from django.test import Client
# from app.models import Asset, Portfolio, PortfolioAsset  # Adjust import based on your app structure

# class PortfolioViewsTestCase(TestCase):
    
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='testpassword')
                
#         self.profile, created = Profile.objects.get_or_create(user=self.user)
#         self.manager_group, created = Group.objects.get_or_create(name='Manager')
#         self.investor_group, created = Group.objects.get_or_create(name='Investor')
#         self.client.login(username='testuser', password='testpassword')
#         self.portfolio = Portfolio.objects.create(portfolio_desc='Test Portfolio', owner=self.profile)
#         self.asset = Asset.objects.create(ticker='AAPL', is_portfolio=False)
        


#     @pytest.mark.django_db     
#     def test_add_stock_db_view(client):
#         # Arrange: Create test asset and portfolio
#         asset = Asset.objects.create(id=1, ticker="AAPL")
#         portfolio = Portfolio.objects.create(id=1, portfolio_desc="Tech Portfolio")

#         # Get CSRF token
#         client = Client()
#         client.get(reverse('add_stock'))  # Ensure session & CSRF token
#         csrf_token = client.cookies['csrftoken'].value

#         # Prepare data
#         asset_data = {
#             "asset_id": asset.id,
#             "portfolio_id": portfolio.id,
#             "ticker": "AAPL",
#             "buy_price": 150.25,
#             "no_of_shares": 10,
#             "stop_loss": 140.00,
#             "cash_out": 200.00,
#             "comment": "Long-term investment",
#             "portfolioName": portfolio.portfolio_desc
#         }

#         # Act: Send request
#         response = client.post(
#             reverse('add_stock'),  # Django URL resolver
#             data=json.dumps(asset_data),
#             content_type='application/json',
#             HTTP_X_CSRFTOKEN=csrf_token  # Include CSRF token
#         )

#         # Assert: Check response and database update
#         assert response.status_code == 200
#         response_json = response.json()
#         assert response_json["status"] == "success"

#         # Verify the stock was added
#         new_entry = PortfolioAsset.objects.filter(asset_id=asset.id, portfolio_id=portfolio.id).first()
#         assert new_entry is not None
#         assert new_entry.buy_price == 150.25
#         assert new_entry.no_of_shares == 10
    
#     def test_get_portfolio_assets_view(self):
#         PortfolioAsset.objects.create(portfolio=self.portfolio, asset=self.asset)
#         url = reverse('get_portfolio_assets')
#         response = self.client.get(url, {'portfolio_id': self.portfolio.id})
        
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('AAPL', response.json())
