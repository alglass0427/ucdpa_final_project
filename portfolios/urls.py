from django.urls import path
from . import views


urlpatterns = [
    path('acces-denied/', views.access_denied, name='access-denied'),
    path('investor/', views.investor, name='investor'),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('get_bid_offer/', views.get_bid_offer, name= "get_bid_offer"),
    path('get_portfolio_assets/', views.get_portfolio_assets, name="get_portfolio_assets"),
    path('add_stock_db/', views.add_stock_db, name="add_stock_db"),
    path('remove_stock/<str:stock_code>/<int:portfolio_id>/', views.remove_stock, name='remove_stock'),
    path('', views.portfolios, name="portfolios"),
    path('get_all_portfolios/', views.get_all_portfolios, name='get_all_portfolios'),
    path('add_portfolio/', views.add_portfolio, name='add_portfolio'),
    path('sell_partial_db/', views.sell_partial_db, name='sell_partial_db'),
    
    
]