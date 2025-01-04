from django.shortcuts import render

# Create your views here.
# views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from portfolios.models import Portfolio, PortfolioAsset, Asset, AssetHistory
from users.models import Profile
from django.db.models import Sum,Count
from django.db.models.functions import TruncMonth,TruncDate
from datetime import datetime, timedelta


def portfolio_data(request, portfolio_id):
    """Return data for a specific portfolio, including its assets."""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    assets = portfolio.portfolio_assets.select_related('asset').all()

    data = {
        "portfolio": portfolio.portfolio_desc,
        "assets": [
            {
                "asset": asset.asset.ticker,
                "buy_price": asset.buy_price,
                "no_of_shares": asset.no_of_shares,
                "holding_value": asset.holding_value,
                "cash_out": asset.cash_out,
                "stop_loss": asset.stop_loss,
            }
            for asset in assets
        ],
    }
    print(f" Portfolio Details End Point :  {data}")
    return JsonResponse(data, safe=False)


def portfolio_industry(request, portfolio_id):
    """Return total assets grouped by industry for a specific portfolio."""
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)

    # Aggregate totals by industry for the given portfolio
    industry_totals = PortfolioAsset.objects.filter(portfolio=portfolio).values('asset__industry').annotate(total_holding_value=Sum('holding_value')).order_by('asset__industry')

    data = {
        "portfolio": portfolio.portfolio_desc,
        "industry_totals": list(industry_totals),
    }

    return JsonResponse(data, safe=False)


def portfolio_asset_weighting(request, portfolio_id):
    """
    Return the weighting of each asset in the portfolio.
    """
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    
    # Get total holding value for the portfolio
    total_holding_value = portfolio.portfolio_assets.aggregate(total=Sum('holding_value'))['total'] or 0

    # Get each asset's holding value and calculate its weighting
    assets = portfolio.portfolio_assets.select_related('asset').values(
        'asset__ticker',
        'holding_value',
    )
    
    data = {
        "portfolio": portfolio.portfolio_desc,
        "total_holding_value": total_holding_value,
        "assets": [
            {
                "ticker": asset['asset__ticker'],
                "holding_value": asset['holding_value'],
                "weighting": (asset['holding_value'] / total_holding_value * 100) if total_holding_value > 0 else 0,
            }
            for asset in assets
        ],
    }

    return JsonResponse(data, safe=False)


########INDEX PAGE

# Total Users
def total_users(request):
    total = User.objects.count()
    return JsonResponse({"labels": ["Total Users"], "data": [total]})

# Top 5 Invested Stocks
def top_invested_stocks(request):
    top_stocks = (
        PortfolioAsset.objects.values("asset__ticker")
        .annotate(total_value=Sum("holding_value"))
        .order_by("-total_value")[:5]
    )
    labels = [stock["asset__ticker"] for stock in top_stocks]
    data = [stock["total_value"] for stock in top_stocks]
    return JsonResponse({"labels": labels, "data": data})

# Total Portfolio Value
def total_portfolio_value(request):
    total_value = PortfolioAsset.objects.aggregate(total=Sum("holding_value"))["total"]
    return JsonResponse({"labels": ["Total Value"], "data": [total_value]})

# User Growth Over Time
def user_growth_over_time(request):
    growth = (
        User.objects.annotate(day=TruncDate("date_joined"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )
    labels = [entry["day"].strftime("%Y-%m-%d") for entry in growth if entry["day"]]
    data = [entry["total"] for entry in growth if entry["day"]]
    return JsonResponse({"labels": labels, "data": data})

# Average Portfolio Size
def average_portfolio_size(request):
    avg_size = PortfolioAsset.objects.aggregate(avg=Sum("holding_value") / Count("portfolio"))["avg"]
    return JsonResponse({"labels": ["Average Size"], "data": [avg_size]})

# Top Industries by Value
def top_industries(request):
    industries = (
        PortfolioAsset.objects.values("asset__industry")
        .annotate(total_value=Sum("holding_value"))
        .order_by("-total_value")[:5]
    )
    labels = [industry["asset__industry"] for industry in industries]
    data = [industry["total_value"] for industry in industries]
    return JsonResponse({"labels": labels, "data": data})