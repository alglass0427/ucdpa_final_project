from django.urls import path
from . import views


urlpatterns = [
    
    path('get_portfolio_assets/', views.get_portfolio_assets, name="get_portfolio_assets"),
    path('add_stock_db/', views.add_stock_db, name="add_stock_db"),
    path('remove_stock/<str:stock_code>/<int:portfolio_id>/', views.remove_stock, name='remove_stock'),
    path('', views.portfolios, name="portfolios"),
    path('get_all_portfolios/', views.get_all_portfolios, name='get_all_portfolios'),
    path('add_portfolio/', views.add_portfolio, name='add_portfolio'),

    
]