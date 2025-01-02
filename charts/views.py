from django.shortcuts import render

# Create your views here.
# views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from portfolios.models import Portfolio, PortfolioAsset, Asset, AssetHistory
from django.db.models import Sum

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