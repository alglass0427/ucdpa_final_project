from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,   ###GENERATE TOKEN
    TokenRefreshView,      ###GIVE A TOKEN TO GENERATE A NEW TOKEN -  longer expiration
)


urlpatterns = [
    path('portfolio/<int:portfolio_id>/', views.portfolio_data, name='portfolio_data'),
    path('portfolio/<int:portfolio_id>/industry/', views.portfolio_industry, name='portfolio_industry'),
    path('portfolio/<int:portfolio_id>/weighting/', views.portfolio_asset_weighting, name='portfolio_asset_weighting'),
    path("total-users/", views.total_users, name="total_users"),
    path("get-portfolios/", views.get_portfolios, name="get_portfolios"),
    path("top-invested-stocks/", views.top_invested_stocks, name="top_invested_stocks"),
    path("total-portfolio-value/", views.total_portfolio_value, name="total_portfolio_value"),
    path("user-growth-over-time/", views.user_growth_over_time, name="user_growth_over_time"),
    path("average-portfolio-size/", views.average_portfolio_size, name="average_portfolio_size"),
    path("top-industries/", views.top_industries, name="top_industries"),
    path("combined-dashboard-data/", views.combined_dashboard_data, name="combined_dashboard_data"),
    path('assets/<int:portfolio_id>/', views.get_sorted_assets, name='get_sorted_assets'),
     
    ]

urlpatterns += [
    path('users/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),    
]