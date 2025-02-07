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
from rest_framework.renderers import BrowsableAPIRenderer,JSONRenderer
from django.db.models import Case, When, BooleanField

from rest_framework.decorators import api_view, renderer_classes

@api_view(['GET'])
def getRoutes(request):

    routes = [
        {'GET':'/charts/portfolio/<str:portfolio_id>/'},
        {'GET':'/charts/portfolio/<str:portfolio_id>/industry/'},
        {'GET':'/charts/portfolio/<str:portfolio_id>/weighting/'},
        {'GET':'/charts/total-users/'},
        {'GET':'/charts/top-invested-stocks/'},
        {'GET':'/charts/total-portfolio-value/'},
        {'GET':'/charts/user-growth-over-time/'},
        {'GET':'/charts/average-portfolio-size/'},
        {'GET':'/charts/top-industries/'},
        {'GET':'/charts/combined-dashboard-data/'},
        {'GET':'/charts/assets/<str:portfolio_id>/'}
    ]

    return Response(routes) 


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
    industry_totals = PortfolioAsset.objects.filter(
        portfolio=portfolio).values(
            'asset__industry').annotate(
                total_holding_value=Sum('holding_value')).order_by('asset__industry')

    data = {
        "portfolio": portfolio.portfolio_desc,
        "industry_totals": list(industry_totals),
    }
    print(f"INDUSTRY RESPONSE : {data}")

    return JsonResponse(data, safe=False)


def portfolio_asset_weighting(request, portfolio_id):
    """
    Return the weighting of each asset in the portfolio.
    """
    print("DEBUG")
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    
    # Get total holding value for the portfolio
    total_holding_value = portfolio.portfolio_assets.aggregate(total=Sum('holding_value'))['total'] or 0 
    total_holding_value +=  portfolio.total_cash_balance  ##Add Cash Balnce
    print(f"FUND VALUE: {total_holding_value}")
    # Get each asset's holding value and calculate its weighting
    assets = portfolio.portfolio_assets.select_related('asset').values(
        'asset__ticker',
        'holding_value',
    )
    
    assets_with_cash = list(assets)  # Convert QuerySet to a list for modification
    assets_with_cash.append({
        'asset__ticker': 'Cash',
        'holding_value': portfolio.total_cash_balance,
    })

    data = {
        "portfolio": portfolio.portfolio_desc,
        "total_holding_value": total_holding_value,
        "assets": [
            {
                "ticker": asset['asset__ticker'],
                "holding_value": asset['holding_value'],
                "weighting": (asset['holding_value'] / total_holding_value * 100) if total_holding_value > 0 else 0,
            }
            for asset in assets_with_cash
        ],
    }
    
    print(f"ALLOCATION RESPONSE : {data}")
    
    return JsonResponse(data, safe=False)


########INDEX PAGE

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.contrib.auth.models import User
from portfolios.models import PortfolioAsset

from charts.serializers import (
    TotalUsersSerializer,
    TopInvestedStocksSerializer,
    TotalPortfolioValueSerializer,
    UserGrowthOverTimeSerializer,
    AveragePortfolioSizeSerializer,
    TopIndustriesSerializer,
    PortfolioSerializer,
)

@api_view(['GET'])
def get_portfolios(request):

    owner_id = request.GET.get('owner_id')  # Get the owner ID from the query parameters
    if owner_id:
        portfolios = Portfolio.objects.filter(owner_id=owner_id)  # Filter portfolios by owner
        serializer = PortfolioSerializer(portfolios, many=True)  # Serialize the data
        return Response(serializer.data)  # Return JSON response
    portfolios = Portfolio.objects.all()
    serializer = PortfolioSerializer(portfolios, many=True)
    # return Response([serializer.data]) # Return all Portfolios no owner_id
    return Response([])
@api_view(['GET'])
def get_sorted_assets(request, portfolio_id):
    if request.method == "GET":
        # Get the selected portfolio
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id)
        except Portfolio.DoesNotExist:
            return JsonResponse({"error": "Portfolio not found."}, status=404)

        assets = Asset.objects.filter(
            portfolio_assets__portfolio=portfolio
        ).annotate(
            starts_with_fof=Case(
                When(ticker__startswith="FOF-", then=True),
                default=False,
                output_field=BooleanField(),
            )
        ).order_by('-starts_with_fof', 'ticker')

        asset_list = [{"id": asset.id, "ticker": asset.ticker} for asset in assets]
        return JsonResponse({"assets": asset_list}, status=200)

@api_view(['GET'])
def total_users(request):
    total = User.objects.count()
    serializer = TotalUsersSerializer({"total_users": total})
    return Response(serializer.data)


@api_view(['GET'])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def top_invested_stocks(request):
    top_stocks = PortfolioAsset.objects.values("asset__ticker").annotate(
        total_value=Sum("holding_value")
    ).order_by("-total_value")[:10]
    serializer = TopInvestedStocksSerializer(top_stocks, many=True)
    print (serializer.data)
    return Response(serializer.data)

@api_view(['GET'])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def total_portfolio_value(request):
    total_value = PortfolioAsset.objects.aggregate(total=Sum("holding_value"))["total"]
    serializer = TotalPortfolioValueSerializer({"total_value": total_value})
    return Response(serializer.data)

@api_view(['GET'])
def user_growth_over_time(request):
    growth = User.objects.annotate(day=TruncDate("date_joined")).values("day").annotate(
        total_users=Count("id")
    ).order_by("day")
    serializer = UserGrowthOverTimeSerializer(growth, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def average_portfolio_size(request):
    avg_size = PortfolioAsset.objects.aggregate(
        avg=Sum("holding_value") / Count("portfolio")
    )["avg"]
    serializer = AveragePortfolioSizeSerializer({"average_size": avg_size})
    return Response(serializer.data)

@api_view(['GET'])
def top_industries(request):
    industries = PortfolioAsset.objects.values("asset__industry").annotate(
        total_value=Sum("holding_value")
    ).order_by("-total_value")[:5]
    serializer = TopIndustriesSerializer(industries, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def combined_dashboard_data(request):
    # Calculate average portfolio size
    

    # Calculate total portfolio value
    total_value = PortfolioAsset.objects.aggregate(total=Sum("holding_value"))["total"] 
    total_value +=  Portfolio.objects.aggregate(total=Sum("total_cash_balance"))["total"] 
    # Count total users
    total_users = User.objects.count()
    avg_size=total_value/total_users
    # Create the combined response
    response_data = {
        "average_portfolio_size": avg_size,
        "total_portfolio_value": total_value,
        "total_users": total_users,
    }

    return Response(response_data)