from django.urls import path
from . import views

urlpatterns = [
    path('portfolio/<int:portfolio_id>/', views.portfolio_data, name='portfolio_data'),
    path('portfolio/<int:portfolio_id>/industry/', views.portfolio_industry, name='portfolio_industry'),
    path('portfolio/<int:portfolio_id>/weighting/', views.portfolio_asset_weighting, name='portfolio_asset_weighting'),
     
    ]