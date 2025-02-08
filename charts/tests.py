from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class APIViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        
    def test_api_view(self):
        response = self.client.get(reverse('top_invested_stocks'))
        self.assertEqual(response.status_code, 200)
        
    def test_portfolio_view(self):
        response = self.client.get(reverse('total_portfolio_value'))
        self.assertEqual(response.status_code, 200)
        
    def test_growth_view(self):
        response = self.client.get(reverse('user_growth_over_time'))
        self.assertEqual(response.status_code, 200)
        
    