from django.shortcuts import render
import json
from django.http import HttpResponse , JsonResponse
# Create your views here.
from django.db.utils import IntegrityError
from .models import  Portfolio,Asset, PortfolioAsset
from users.models import Profile
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def add_stock_db(request):

    # Parse JSON data from the request body
    data = json.loads(request.body)
    # Extract asset details
    stock_code = data.get('stock_code')
    buy_price = data.get('buy_price')
    no_of_shares = data.get('no_of_shares')
    stop_loss = data.get('stop_loss')
    cash_out = data.get('cash_out')
    comment = data.get('comment')
    portfolio_name = data.get('portfolioName')

    portfolio = Portfolio.objects.filter(owner=request.user.profile, portfolio_desc=portfolio_name).first()
    print(portfolio.owner)
    # portfolio = Portfolio.query.filter_by(portfolio_desc=portfolio_name).first()
    
    cash = Asset.objects.filter(ticker = "CASH").first()
    capital = PortfolioAsset.objects.filter(portfolio_id = portfolio.id,asset_id = cash.id).first()

    print(f"Capital : {capital.holding_value}")
    if capital.holding_value < (float(buy_price) * float(no_of_shares)):
        return JsonResponse({"message": "Not Enough Capital - (Buy Price * Volume > Capital (Cash)!", "category": "danger"},status=201)
        
    if not portfolio:
        
        return JsonResponse({"message": "No Portfolio Exists with this Description!","category": "danger"},status=201)

    # Check if the asset already exists
    asset = Asset.objects.filter(ticker=stock_code).first()

    if not asset:
        # asset = Asset(ticker=stock_code)
        # db.session.add(asset)
        # db.session.commit()
        return JsonResponse({"message": "No Asset with this Ticker - Contact Admin!","category": "danger"},status=201)

#######Reduce Cash###############

    # Retrieve the user and portfolio
    # Insert the stock details into the portfolio_assets table
    # Get the asset and portfolio IDs from your existing logic

    if portfolio and asset:
    # Fetch the holding
        holding = PortfolioAsset.objects.filter(portfolio=portfolio, asset=asset).first()
        print(f"Holding Price : {holding}")

        if holding:
            # Update the existing holding
            holding.no_of_trades += 1
            holding.buy_price = float(buy_price)
            holding.no_of_shares += float(no_of_shares)
            holding.holding_value += float(buy_price) * float(no_of_shares)

            # Update the capital
            capital.holding_value = round(
                capital.holding_value - (float(buy_price) * float(no_of_shares)), 2
            )

            try:
                with transaction.atomic():  # Use atomic transaction to ensure data integrity
                    holding.save()
                    capital.save()
                return JsonResponse({
                    "message": f"Bought Equity : {stock_code} (Buy Price : {buy_price}), Cost : {(float(buy_price) * float(no_of_shares))}",
                    "category": "success"
                }, status=201)
            except IntegrityError:
                return JsonResponse({
                    "message": "Something Went Wrong - Rolled Back Change!",
                    "category": "danger"
                }, status=400)
        else:
            # Create a new PortfolioAsset record
            portfolio_asset = PortfolioAsset(
                portfolio=portfolio,
                asset=asset,
                no_of_trades=1,
                buy_price=buy_price,
                no_of_shares=no_of_shares,
                holding_value=float(buy_price) * float(no_of_shares),
                stop_loss=stop_loss,
                cash_out=cash_out,
                comment=comment,
            )

            # Update the capital
            capital.holding_value = round(
                capital.holding_value - (float(buy_price) * float(no_of_shares)), 2
            )

            try:
                with transaction.atomic():  # Use atomic transaction to ensure data integrity
                    portfolio_asset.save()
                    capital.save()
                return JsonResponse({
                    "message": f"Bought Equity : {stock_code} (Buy Price : {buy_price}), Cost : {(float(buy_price) * float(no_of_shares))}",
                    "category": "success"
                }, status=201)
            except IntegrityError:
                return JsonResponse({
                    "message": "Something Went Wrong - Rolled Back Change!",
                    "category": "danger"
                }, status=400)
    else:
        return JsonResponse({
            "message": "Portfolio or asset not found.",
            "category": "danger"
        }, status=404)
    



from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Portfolio, PortfolioAsset, Asset
from .utils import get_latest_portfolio_prices, get_stock_price
import json

@csrf_exempt
@login_required
def get_portfolio_assets(request):
    # Check for POST or GET request
    if request.method == 'POST':
        data = json.loads(request.body)
        portfolio_name = data.get('portfolio')
        yf_flag = data.get('yf_flag')
    else:
        portfolio_name = request.GET.get('portfolio')
        yf_flag = request.GET.get('yf_flag')

    # Get portfolio and cash asset
    portfolio_instance = Portfolio.objects.filter(
        portfolio_desc=portfolio_name,
        owner=request.user.profile
    ).first()

    cash_asset = Asset.objects.filter(ticker="CASH").first()
    cash = PortfolioAsset.objects.filter(
        asset=cash_asset,
        portfolio=portfolio_instance
    ).first() if portfolio_instance else None

    # Get all portfolio assets
    assets = portfolio_instance.portfolio_assets.all() if portfolio_instance else []

    # Update asset prices based on Yahoo Finance flag
    if yf_flag == 'on':
        for portfolio_asset in assets:
            asset = portfolio_asset.asset
            if asset.ticker != "CASH":
                yahoo_data = get_stock_price(
                    stock_code=asset.ticker,
                    asset_id=asset.id,
                    portfolio=portfolio_asset.portfolio.id,
                    yf_flag=yf_flag,
                    user_id=request.user.id,
                    buy_price=portfolio_asset.buy_price
                )
                portfolio_asset.latest_price = yahoo_data[1]
    else:
        latest_prices = get_latest_portfolio_prices(portfolio=portfolio_instance.id)
        for portfolio_asset in assets:
            asset = portfolio_asset.asset
            if asset.ticker != "CASH":
                portfolio_asset.latest_price = latest_prices.get(asset.ticker)

    # Pre-calculate percentage_diff for each asset
    stocks_data = []
    for portfolio_asset in assets:
        asset = portfolio_asset.asset
        if asset.ticker != "CASH":
            current_value = float(portfolio_asset.latest_price or 0) * float(portfolio_asset.no_of_shares or 0)
            holding_value = float(portfolio_asset.holding_value or 0)
            percentage_diff = None
            if holding_value > 0:
                percentage_diff = ((current_value - holding_value) / holding_value) * 100
            stocks_data.append({
                'portfolio_asset': portfolio_asset,
                'asset': asset,
                'percentage_diff': percentage_diff
            })

    # Pass data to template
    context = {
        'stocks': stocks_data,
        'cash': cash,
    }
    return render(request, 'users/dashboard_tbl.html', context)


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from .models import PortfolioAsset, Asset  # Update with your actual model imports
from .utils import get_latest_price 


@login_required
def remove_stock(request, stock_code, portfolio_id):
    if request.method == "POST":
        # portfolio_id = request.POST.get("portfolio_id")  # Get portfolio_id from POST data
        print(f" REQUEST : {request}")
        print(f"Removing stock: {stock_code} from portfolio with ID: {portfolio_id}")
        print(f"Portfolio to be deleted from: {portfolio_id}")

        # Fetch the cash asset
        cash = get_object_or_404(Asset, ticker="CASH")
        capital = get_object_or_404(PortfolioAsset, portfolio_id=portfolio_id, asset_id=cash.id)

        # Fetch the asset corresponding to the stock code
        asset = Asset.objects.filter(ticker=stock_code).first()
        if not asset:
            return JsonResponse({"message": f"Stock with ticker {stock_code} not found.", "category": "danger"}, status=201)

        # Fetch the specific PortfolioAsset entry
        portfolio_asset = PortfolioAsset.objects.filter(portfolio_id=portfolio_id, asset_id=asset.id).first()
        if not portfolio_asset:
            return JsonResponse({"message": f"Stock {stock_code} is not part of the portfolio.", "category": "danger"}, status=201)

        # Get the sell price, fallback to buy price if fetching fails
        try:
            sell_price = round(get_latest_price(ticker=stock_code), 2)
        except Exception:
            sell_price = round(portfolio_asset.buy_price, 2)

        # Update capital and delete the portfolio asset
        try:
            with transaction.atomic():
                capital.holding_value = round(
                    float(capital.holding_value) + (float(sell_price) * float(portfolio_asset.no_of_shares))
                )
                capital.save()
                portfolio_asset.delete()

            message = (f"Sold Equity: {stock_code} (Trade Price: {sell_price}), "
                       f"Value: {float(sell_price) * float(portfolio_asset.no_of_shares)}")
            return JsonResponse({"message": message, "category": "success"}, status=201)

        except IntegrityError:
            message = f"Could not remove {stock_code} - Please try again later!"
            return JsonResponse({"message": message, "category": "danger"}, status=201)

    return JsonResponse({"message": "Invalid request method.", "category": "danger"}, status=405)




# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from .models import Portfolio

@login_required
def portfolios(request):
    # Fetch the user's portfolio
    portfolio_list = Portfolio.objects.filter(owner=request.user.profile)
    print()
    print(portfolio_list)
    context = {'portfolios': portfolio_list}
    # Return the portfolios to the template
    return render(request, 'portfolios/portfolios.html', context)


from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Portfolio, PortfolioAsset, Asset
from django.db.models import Sum, Count, F, Q

@login_required
def get_all_portfolios(request):
    # Retrieve the data sent from JavaScript (assuming it's a POST request)
    print('DEBUG : ALAN')
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))  # Decode and parse the JSON body
        portfolio = data.get('portfolio', 'All')
        print(portfolio)
        # Query for a specific portfolio or all portfolios for the current user
        if portfolio != 'All':
            portfolios = Portfolio.objects.filter(id=portfolio, owner=request.user.profile)
        else:
            portfolios = Portfolio.objects.filter(owner=request.user.profile)

        # Prepare the data for CTEs (using Django's ORM aggregation methods)
        portfolio_details = portfolios.annotate(
            total_investments=Count('portfolio_assets'),
            max_trades=Sum('portfolio_assets__no_of_trades'),
            sum_investments=Sum('portfolio_assets__holding_value'),
            sum_cash=Sum('portfolio_assets__holding_value', filter=Q(portfolio_assets__asset__ticker='CASH'))
        ).values(
            'id', 'portfolio_desc', 'total_investments', 'max_trades', 'sum_investments', 'sum_cash'
        )

        all_details = PortfolioAsset.objects.filter(portfolio__in=portfolios).annotate(
            portfolio_reference =F('portfolio_id'),
            ticker=F('asset__ticker'),
            industry=F('asset__industry'),
            value=F('holding_value'),
            trades=F('no_of_trades')
        ).values(
            'portfolio_id', 'ticker', 'industry', 'value', 'trades'
        )
        
                # Aggregate data for the pie chart
        industry_distribution = (
            PortfolioAsset.objects.filter(portfolio__in=portfolios)
            .values('asset__industry')
            .annotate(total_value=Sum('holding_value'))
            .order_by('-total_value')
        )


        # Check if we have portfolios to return
        if portfolios.exists():
            # Render the portfolio rows template
            context = {
            'portfolios': portfolio_details,
            'all_details': all_details,
            'industry_distribution': json.dumps(list(industry_distribution)), # Pass as a list for JSON serialization
        }
            for detail in all_details:
                print(detail)

            return render(request, 'portfolios/portfolio_rows.html',context)
            # return render(request, 'portfolios/portfolio_rows.html', {'portfolios': portfolio_details})
        else:
            return JsonResponse({"error": "No portfolios found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)




from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from .models import Portfolio, Asset, PortfolioAsset

@login_required
def add_portfolio(request):
    # Fetch the 'CASH' asset
    cash = Asset.objects.filter(ticker="CASH").first()

    if request.method == 'POST':
        portfolio_desc = request.POST.get('portfolio_desc')
        seed_capital = request.POST.get('seed_capital')

        # Check if the portfolio already exists for the current user
        if not Portfolio.objects.filter(owner=request.user.id, portfolio_desc=portfolio_desc).exists():
            # Create the new portfolio
            new_portfolio = Portfolio(owner=request.user.profile, portfolio_desc=portfolio_desc)
            new_portfolio.save()

            # Create PortfolioAsset for seed capital
            capital = PortfolioAsset(
                portfolio_id=new_portfolio.id,
                asset_id=cash.id,
                no_of_trades=1,
                buy_price=seed_capital,
                no_of_shares=1,
                holding_value=seed_capital,
                stop_loss=0,
                cash_out=0,
                comment="Seed Capital"
            )
            capital.save()

            # Fetch the list of portfolios for the current user
            portfolio_list = Portfolio.objects.filter(owner=request.user.id)
            return render(request, 'portfolios/portfolios.html', {'portfolios': portfolio_list})
        else:
            messages.warning(request, f"Portfolio Name '{portfolio_desc}' already exists for user {request.user.username}.")
            return redirect('portfolios')  # Assuming 'portfolios' is the URL name for the portfolio list view

    return render(request, 'portfolios/portfolios.html')  # Assuming you have an 'add_portfolio.html' template for GET requests
