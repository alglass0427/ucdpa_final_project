from django.shortcuts import render
import json
from django.http import HttpResponse , JsonResponse
# Create your views here.
# from django.db.utils import IntegrityError
from .models import  Portfolio,Asset, PortfolioAsset, Cash
from users.models import Message
from users.models import Group,User
from users.models import Profile
from django.db import transaction,IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required , user_passes_test
from django.db.models import Sum, Count, F, Q , Subquery, OuterRef ,Case, When, Value,FloatField
from .utils import get_latest_portfolio_prices, get_stock_price , get_latest_price , handle_cash_update_or_create , handle_cash_update_or_create_investor
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce,Cast
# from django.db import transaction, IntegrityError


def is_manager(user):
    return user.is_authenticated and str(user.profile.group) == "Manager"

@login_required(login_url='login')
def investor (request):
    # page = kwargs.get('page',None)
    # profile = request.user.profile
    

    if request.method == "POST":
        
        comment = request.POST.get('comment', None)
        portfolio_id = request.POST.get('portfolio', None)
        print("PORTFOLIO",portfolio_id)
        owner = request.POST.get('owner', None)
        if owner == 'Select Manager':
            messages.error(request,"Manager must be selected!!")
            return redirect('investor')
        
        
        if portfolio_id == 'Select Portfolio' or portfolio_id == '' or  portfolio_id == None:
            messages.error(request,"Portfolio must be selected!!")
            return redirect('investor')
        
        print("OWNER", owner)
        user = request.user.profile.id
        print(portfolio_id)
        print(owner,user)
        asset  =  Asset.objects.filter(portfolio=portfolio_id)
        portfolio_content_type = ContentType.objects.get_for_model(Profile)
        portfolio = Portfolio.objects.get(id=portfolio_id)
        # Query the Cash model
        cash = Cash.objects.filter(
            portfolio=portfolio,  # Match the specific portfolio
            owner_content_type=portfolio_content_type,  # Match the owner type
            owner_object_id=request.user.profile.id  # Match the owner object ID
            ).first()
        # print("USER CASH INVESTED:::", cash.balance)
        action = request.POST.get('action')
        if not cash and action == "Redemption" :
            messages.error(request,"No Cash Invested in this Fund")
            return redirect('investor')

        

        
        print(action)
        if action == "Subscription":
            print("Subscription")
            invest_amount = request.POST.get('invest_amount', None)
            print (invest_amount)
        elif action == "Redemption":
            print("Redemption")
            invest_amount = request.POST.get('invest_amount', None)
            invest_amount = float(invest_amount)*(-1)
            print(invest_amount)
        else:
            messages.error(request,"Invalid Request")
            return redirect('investor')

        if cash and action == "Redemption" :
            if int(cash.balance) < float(request.POST.get('invest_amount', None)):
                messages.error(request,f"Max Redemption is {cash.balance}")
                print("CANNOT REDEEM")
                return redirect('investor')
        
        print(asset)
        print("owner",owner)
        print("invest_amount",invest_amount)
        print("portfolio_id",portfolio_id)
        print("comment",comment)

        recipient = Profile.objects.get(id=owner)
        

        try:
            sender = request.user.profile
        except:
            sender = None
        
        portfolio = Portfolio.objects.get(id=portfolio_id)
        current_net_assets = (portfolio.total_holding_value() + portfolio.total_cash_balance)
        current_units = portfolio.units
        current_NAV = (current_net_assets/current_units)
        new_net_assets  = current_net_assets + float(invest_amount)
        new_total_units = new_net_assets / current_NAV
        new_units = new_total_units - current_units        
        portfolio_name = portfolio.portfolio_desc
        Message.objects.create(
            sender=sender,
            recipient=recipient,
            name = request.user.profile.name,
            email= request.user.email,
            subject= f"{invest_amount} {action} - {portfolio_name}",
            body=comment
        )
    
        messages.success(request,"Investment successful, message sent to Fund Manager!")

        if not portfolio_id :
            return JsonResponse({"error": "Portfolio ID is required."}, status=400)
        if not owner :
            return JsonResponse({"error": "Owner is required."}, status=400)
        if not portfolio_id :
            return JsonResponse({"error": "Portfolio ID is required."}, status=400)
        ## handle_cash_update_or_create_investor(portfolio, buy_price, no_of_shares, new_units,profile,buy_or_sell):
        handle_cash_update_or_create_investor(portfolio_id, invest_amount, new_units,owner,action,user)

        return redirect('investor')
    # owners = Portfolio.objects.values_list('owner__name','owner__id').distinct().order_by() 
    owners= Profile.objects.filter(group__name="Manager" ) 
    #####.order_by() with no arguments clears any default ordering applied by Django.
    print("OWNERS:::",owners)   
    
    context = {'owners':owners}
    return render(request, 'portfolios/investor.html', context)


def access_denied(request):
    messages.error(request, "Access denied. - Redirected To Investor from Manager UI.")
    return redirect('investor')

@login_required(login_url='login')
@user_passes_test(is_manager, login_url='access-denied')
def dashboard(request):
    print(f"REQUEST.USER: {request.user}")
    print(request.user.groups)
    print(f"User Groups: {request.user.groups.all()}")
    # managers_group = Group.objects.get(name='Manager')
    
    # Get all users who belong to the "Managers" group
    # managers_users = Profile.objects.filter(group=managers_group)
    profile = request.user.profile
    portfolios = profile.portfolio_set.all()
    if portfolios.count() == 0:
        messages.info(request, "You must create a portfolio before proceeding.")
        return redirect('portfolios')  # Redirect to the page for managing portfolios
    assets = Asset.get_assets_by_ticker()
    context = {'profile' : profile , 'portfolios': portfolios, 'assets' : assets , 'is_manager':is_manager , #'managers_users': managers_users 
               }
    return render(request, 'portfolios/dashboard.html', context)

# @csrf_exempt
def get_bid_offer(request):
    if request.method == 'POST':
        print("Request Body:", request.body)
        # data = request.get_json() # retrieve the data sent from JavaScript
        data = json.loads(request.body)
        print("Parsed Data:", data)
        print(f"Ticker : {data}")
        ticker = data['ticker']
        asset_id = data['assetID']
        portfolio_id = data['portfolioID']
        asset =  Asset.objects.filter(id = asset_id).first()
        
        if ticker  ==  "":
            return JsonResponse({'last_quote': "NA" , "message": "Please Select a ticker to refresh prices!", "category": "success"})
        
        
    else:
        # If using a GET request, retrieve portfolio from the query string
        ticker = request.args.get('ticker')
        asset_id = request.args.get('assetID')
        portfolio_id = request.args.get('portfolioID')

    print(ticker,asset_id,portfolio_id)
    
    last_quote = get_latest_price(ticker,asset_id,portfolio_id)
    # return jsonify({"message": "Asset added successfully!", "category": "success"}), 201
    return JsonResponse({'last_quote': last_quote , "message": "Asset added successfully!", "category": "success"})



# @csrf_exempt
@login_required(login_url="login")
def add_stock_db(request):
    user = request.user
    print("USER GROUP::::", user.profile.group)
    print ("USER:::::::",user)
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
    asset_id = data.get('asset_id')
    portfolio_id = data.get('portfolio_id')
    managed_portfolio = Portfolio.objects.filter(owner=request.user.profile, portfolio_desc=portfolio_name).first()
    # print("OWNER::" , portfolio.owner)
    total_amount =   (float(buy_price) * float(no_of_shares))
    # portfolio = Portfolio.objects.filter(id=portfolio_id).first()

    group = user.profile.group.name
    if group.strip() == 'Manager':
        print("IN IF ACCESS:::::", user.profile.group)
        capital = managed_portfolio.total_cash_balance
    else:
        capital = user.profile.balance
        print("CAPITAL USER BALANCE::::", user.profile.group)
        print("IN ELSE ACCESS:::::", user.profile.group)
        

        if capital < total_amount:
            return JsonResponse({"message": "Not Enough Capital - (Buy Price * Volume > Capital (Cash)!", "category": "danger"},status=201)

        asset_portfolio = Portfolio.objects.filter(id=portfolio_id).first()
        if not asset_portfolio:
            return JsonResponse({"message": "No Portfolio Exists with this Description!","category": "danger"},status=201)

        current_net_assets = (asset_portfolio.total_holding_value() + asset_portfolio.total_cash_balance)
        current_units = asset_portfolio.units
        current_NAV = (current_net_assets/current_units)
        new_net_assets  = current_net_assets + total_amount
        new_total_units = new_net_assets / current_NAV
        new_units = new_total_units - current_units
        
        try:
            with transaction.atomic():

                profile = user.profile
                current_balance =  asset_portfolio.total_cash_balance
                # current_units =  portfolio.units
                asset_portfolio.units	+= new_units
                print("NEW UNITS",new_units)
                asset_portfolio.save()

                ##update existing investor or create
                # signal updates the Cash in Portfolio
                cash, created = Cash.objects.update_or_create(
                        portfolio=asset_portfolio,
                        # user=profile,
                        owner_content_type=ContentType.objects.get_for_model(Portfolio),
                        owner_object_id=managed_portfolio.id,
                        balance=total_amount,  # amount invested
                        units = new_units,
                        currency="USD"
                    )
                print("CASH::::",cash)

                if not created:
                         # Update the balance if the instance already exists
                    cash.balance += total_amount
                    cash.units += new_units
                    cash.save()
                else:
                    print(f"Created new Cash entry for portfolio {portfolio_id} with balance {total_amount}.")
                            
                #subtract from user balance
                profile.balance -= total_amount
                profile.save()
                
                
                
            return JsonResponse({
                    "message": f"Bought Fund Units : {asset_portfolio.portfolio_desc} (Buy Price : {buy_price}), Cost : {(float(buy_price) * float(no_of_shares))}",
                    "category": "success"
                    }, status=201)
        except IntegrityError:
            return JsonResponse({
                "message": "Something Went Wrong - Rolled Back Change!",
                "category": "danger"
            }, status=400)
    
    print(f"Capital : {capital}")
    if capital < (float(buy_price) * float(no_of_shares)):
        return JsonResponse({"message": "Not Enough Capital - (Buy Price * Volume > Capital (Cash)!", "category": "danger"},status=201)
        
    if not managed_portfolio:
        
        return JsonResponse({"message": "No Portfolio Exists with this Description!","category": "danger"},status=201)

    # Check if the asset already exists
    asset = Asset.objects.filter(ticker=stock_code).first()

    if not asset:
        
        return JsonResponse({"message": "No Asset with this Ticker - Contact Admin!","category": "danger"},status=201)

#######Reduce Cash###############


    if managed_portfolio and asset:

        if asset.is_portfolio:
            print(f"Asset Portfolio: {asset.portfolio}")
            current_net_assets = (asset.portfolio.total_holding_value() + asset.portfolio.total_cash_balance)
            print(f"Current Assets in FOF: {current_net_assets}")
            current_units = asset.portfolio.units
            print(f"Current UNITS in FOF: {current_units}")
            current_NAV = (current_net_assets/current_units)
            new_net_assets  = current_net_assets + total_amount
            new_total_units = round(new_net_assets / current_NAV,2)
            new_units = round(new_total_units - current_units,2)
            print("NEW UNITS",new_units)
            asset_portfolio = Portfolio.objects.filter(id=portfolio_id).first()
            if not asset_portfolio:
                return JsonResponse({"message": "No Portfolio Exists with this Description!","category": "danger"},status=201)
            
            test = handle_cash_update_or_create(asset, buy_price, no_of_shares, new_units, managed_portfolio,"BUY")


            Message.objects.create(
            sender=request.user.profile,
            recipient=asset.portfolio.owner,
            name = request.user.profile.name,
            email= request.user.email,
            subject= f"{total_amount} SUB- {portfolio_name}",
            body=comment
        )
           
    # Fetch the holding
        holding = PortfolioAsset.objects.filter(portfolio=managed_portfolio, asset=asset).first()
        print(f"Holding Price : {holding}")

        if holding:
            # Update the existing holding
            holding.no_of_trades += 1
            holding.buy_price = float(buy_price)
            holding.no_of_shares += float(no_of_shares)
            holding.holding_value += float(buy_price) * float(no_of_shares)

            # Update the capital
            managed_portfolio.total_cash_balance = round(
                managed_portfolio.total_cash_balance - (float(buy_price) * float(no_of_shares)), 2
            )

            try:
                with transaction.atomic():  # Use atomic transaction to ensure data integrity
                    holding.save()
                    managed_portfolio.save()
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
                portfolio=managed_portfolio,
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
            managed_portfolio.total_cash_balance = round(
            managed_portfolio.total_cash_balance - (float(buy_price) * float(no_of_shares)), 2
            )

            try:
                with transaction.atomic():  # Use atomic transaction to ensure data integrity
                    portfolio_asset.save()
                    managed_portfolio.save()
                    
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
    

@csrf_exempt
@login_required(login_url="login")
def get_portfolio_assets(request):
    # Check for POST or GET request
    if request.method == 'POST':
        data = json.loads(request.body)
        portfolio_name = data.get('portfolio')
        yf_flag = data.get('yf_flag')
    else:
        portfolio_name = request.GET.get('portfolio')

        yf_flag = request.GET.get('yf_flag')

    print("Portfolio Name:::::::::::::::::::::", portfolio_name)

    # Get portfolio and cash asset
    portfolio_instance = Portfolio.objects.filter(
        portfolio_desc=portfolio_name,
        owner=request.user.profile
    ).first()
    profile = request.user.profile
    is_manager = profile.group.name == 'Manager' if profile.group else False

    cash = Cash.objects.filter(portfolio_id=portfolio_instance.id).aggregate(total_balance=Sum('balance'))['total_balance'] or 0
    portfolio = Portfolio.objects.filter(owner=request.user.profile, portfolio_desc=portfolio_name).first()
    assets = portfolio_instance.portfolio_assets.all() if portfolio_instance else []

    # Update asset prices based on Yahoo Finance flag
    if yf_flag == 'on':
        for portfolio_asset in assets:
            asset = portfolio_asset.asset
            
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
        print ("LATEST_PRICES", latest_prices)
        for portfolio_asset in assets:
            asset = portfolio_asset.asset
            # if asset.ticker != True:
            portfolio_asset.latest_price = latest_prices.get(asset.ticker)
            
                

    # Pre-calculate percentage_diff for each asset
    stocks_data = []
    for portfolio_asset in assets:
        asset = portfolio_asset.asset
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
    print('Manager: ', is_manager)
    # Pass data to template
    context = {
        'stocks': stocks_data,
        'cash': portfolio.total_cash_balance,
        'is_manager': is_manager,
    }
    return render(request, 'portfolios/dashboard_tbl.html', context)



@login_required(login_url="login")
def remove_stock(request, stock_code, portfolio_id):
    if request.method == "POST":
        # portfolio_id = request.POST.get("portfolio_id")  # Get portfolio_id from POST data
        print(f" REQUEST : {request}")
        print(f"Removing stock: {stock_code} from portfolio with ID: {portfolio_id}")
        print(f"Portfolio to be deleted from: {portfolio_id}")

        # Fetch the cash asset
        portfolio = Portfolio.objects.get(id=portfolio_id)
        print(portfolio)
        capital = portfolio.total_cash_balance

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

        if asset.is_portfolio:
            try:
                portfolio_content_type = ContentType.objects.get_for_model(Portfolio)

                # Query the Cash model
                cash = Cash.objects.filter(
                    portfolio=asset.portfolio,  # Match the specific portfolio
                    owner_content_type=portfolio_content_type,  # Match the owner type
                    owner_object_id=portfolio.id  # Match the owner object ID
                    )
                print(f"REMOVE ASSET CASH: {cash}")
                total_amount =   (float(sell_price) * float(portfolio_asset.no_of_shares))
                print(f"Asset Portfolio: {asset.portfolio}")
                current_net_assets = (asset.portfolio.total_holding_value() + asset.portfolio.total_cash_balance)
                print(f"Current Assets in FOF: {current_net_assets}")
                current_units = asset.portfolio.units
                print(f"Current UNITS in FOF: {current_units}")
                current_NAV = (current_net_assets/current_units)
                new_net_assets  = current_net_assets - total_amount
                new_total_units = round(new_net_assets / current_NAV,2)
                new_units = round(new_total_units - current_units,2)
                print("NEW UNITS",new_units)
                print("SELL PRICE",sell_price)
                asset_portfolio = Portfolio.objects.filter(id=portfolio_id).first()
                if not asset_portfolio:
                    return JsonResponse({"message": "No Portfolio Exists with this Description!","category": "danger"},status=201)
                
                test = handle_cash_update_or_create(asset, sell_price, portfolio_asset.no_of_shares, new_units, portfolio,"SELL")
                portfolio_asset.delete()

                message = (f"Sold Equity: {stock_code} (Trade Price: {sell_price}), "
                       f"Value: {float(sell_price) * float(portfolio_asset.no_of_shares)}")
                return JsonResponse({"message": message, "category": "success"}, status=201)
            except IntegrityError:
                message = f"Could not remove {stock_code} - Please try again later!"
            return JsonResponse({"message": message, "category": "danger"}, status=201)

        try:
            with transaction.atomic():
                portfolio.total_cash_balance = round(
                    float(portfolio.total_cash_balance) + (float(sell_price) * float(portfolio_asset.no_of_shares))
                )
                portfolio.save()
                portfolio_asset.delete()

            message = (f"Sold Equity: {stock_code} (Trade Price: {sell_price}), "
                       f"Value: {float(sell_price) * float(portfolio_asset.no_of_shares)}")
            return JsonResponse({"message": message, "category": "success"}, status=201)

        except IntegrityError:
            message = f"Could not remove {stock_code} - Please try again later!"
            return JsonResponse({"message": message, "category": "danger"}, status=201)

    return JsonResponse({"message": "Invalid request method.", "category": "danger"}, status=405)



@login_required(login_url="login")
@user_passes_test(is_manager, login_url='access-denied')
def portfolios(request):
    # Fetch the user's portfolio
    
    portfolio_list = Portfolio.objects.filter(owner=request.user.profile)
    print()
    print(portfolio_list)
    context = {'portfolios': portfolio_list}
    # Return the portfolios to the template
    return render(request, 'portfolios/portfolios.html', context)




@login_required(login_url="login")
def get_all_portfolios(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))  # Decode and parse the JSON body
        portfolio = data.get('portfolio', 'All')

        # Query for a specific portfolio or all portfolios for the current user
        if portfolio != 'All':
            portfolios = Portfolio.objects.filter(id=portfolio)
        else:
            portfolios = Portfolio.objects.filter(owner=request.user.profile)

        # Prepare the data for portfolio details
        portfolio_details = portfolios.annotate(
            total_investments=Count('portfolio_assets'),
            max_trades=Sum('portfolio_assets__no_of_trades'),
            sum_investments=Sum('portfolio_assets__holding_value', filter=~Q(portfolio_assets__asset__ticker='CASH')),
            total_value=Sum('portfolio_assets__holding_value')
        ).values(
            'id', 'portfolio_desc', 'total_investments', 'max_trades', 'sum_investments', 'total_cash_balance'
        )


        portfolio_total_value = Portfolio.objects.filter(
                id=OuterRef('portfolio_reference')  # Match the Portfolio ID consistently
            ).annotate(
                # total_value=Sum('portfolio_assets__holding_value') + F('total_cash_balance')
                # total_value = Coalesce(Sum('portfolio_assets__holding_value'), Value(0)) + F('total_cash_balance')
                total_value = Coalesce(Sum('portfolio_assets__holding_value'), Value(0), output_field=FloatField()) + Cast(F('total_cash_balance'), FloatField())

            ).values('total_value')

        
        # Cash entries
        portfolio_ids = portfolios.values_list('id', flat=True)
        cash_entries = Portfolio.objects.filter(pk__in=portfolio_ids).annotate(
            portfolio_reference=F('id'),
            ticker=Value('Cash'),
            industry=Value('Cash Balance'),
            value=F('total_cash_balance'),
            trades=Value(0),
            weight=(F('total_cash_balance') / (Subquery(portfolio_total_value))) * 100
        ).values(
            'portfolio_reference', 'ticker', 'industry', 'value', 'trades', 'weight'
        )
        print(f"CASH ENTRIES:::::: {cash_entries}")

        # Portfolio asset details
        all_details = PortfolioAsset.objects.filter(portfolio__in=portfolios).annotate(
            portfolio_reference=F('portfolio_id'),
            ticker=F('asset__ticker'),
            industry=F('asset__industry'),
            value=F('holding_value'),
            trades=F('no_of_trades'),
            weight=(F('holding_value') / Subquery(portfolio_total_value)) * 100
        ).values(
            'portfolio_reference', 'ticker', 'industry', 'value', 'trades', 'weight'
        )

        # Combine cash entries with portfolio assets
        all_details = list(all_details) + list(cash_entries)
        print(f"ALL DETAILS :  {all_details}")
        # Check if portfolios exist
        if portfolios.exists():
            context = {
                'portfolios': portfolio_details,
                'all_details': all_details,
            }
            html_content = render(request, 'portfolios/portfolio_rows.html', context).content.decode('utf-8')
            return JsonResponse({
                'message': None,
                'html': html_content,
            })
        else:
            return JsonResponse({
                "error": "No portfolios found",
                "message": "No Portfolios Found!",
                "category": "danger"
            }, status=404)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)




from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from .models import Portfolio, Asset, PortfolioAsset

@login_required(login_url="login")
def add_portfolio(request):
    # Fetch the 'CASH' asset
    # cash = Asset.objects.filter(ticker="CASH").first()

    if request.method == 'POST':
        portfolio_desc = request.POST.get('portfolio_desc')
        seed_capital = request.POST.get('seed_capital')
        units = request.POST.get('units')
        seed_capital = float(seed_capital)
        units = int(units)

        try:
            with transaction.atomic():
                # Check if the profile has enough balance
                profile = request.user.profile
                if profile.balance < seed_capital:
                    messages.error(request, "Insufficient balance in the profile to create a portfolio.")
                    return redirect('portfolios')

                # Check if the portfolio already exists for the current user
                if not Portfolio.objects.filter(owner=request.user.id, portfolio_desc=portfolio_desc).exists():
                    # Create the new portfolio
                    new_portfolio, created = Portfolio.objects.update_or_create(
                    owner=request.user.profile,
                    portfolio_desc=portfolio_desc,
                    defaults={
                        "total_cash_balance": seed_capital,
                        "units": units}
                )   
                    if created:
                        Cash.objects.update_or_create(
                            portfolio=new_portfolio,
                            # user=profile,
                            owner_content_type=ContentType.objects.get_for_model(Profile),
                            owner_object_id=profile.id,
                            balance=seed_capital,  # Seed capital as the initial balance
                            units = units,
                            currency="USD"
                        )
                        # Add seed capital to the portfolio balance
                        new_portfolio.total_cash_balance = seed_capital
                        new_asset, created = Asset.objects.update_or_create(
                        ticker=f"(FOF){new_portfolio.id}",  # Generate a unique ticker for portfolios
                        defaults={
                            "company_name": new_portfolio.portfolio_desc,
                            "is_portfolio": True,
                            "industry": "Internal Fund",
                            "portfolio": new_portfolio
                        }
                        
                    )

                        amount =  profile.balance
                        print("AMOUNT:", amount)
                        
                        new_portfolio.save()
                        profile.balance -= seed_capital
                        profile.save()
                        # Fetch the list of portfolios for the current user
                        # portfolio_list = Portfolio.objects.filter(owner=request.user.id)
                        messages.success(request, f"Portfolio '{portfolio_desc}' created successfully.")
                    else:
                        messages.warning(request, f"Portfolio Name '{portfolio_desc}' already exists for user {request.user.username}.")
                        return redirect('portfolios')  # Assuming 'portfolios' is the URL name for the portfolio list view
                else:
                    messages.warning(request, f"Portfolio Name '{portfolio_desc}' already exists for user {request.user.username}.")

        except IntegrityError:
            messages.warning(request, f"Something went wrong!! -  rolled back Change.")    

        return redirect('portfolios')
    
    portfolio_list = Portfolio.objects.filter(owner=request.user.id)
    return render(request, 'portfolios/portfolios.html', {'portfolios': portfolio_list})  # Assuming you have an 'add_portfolio.html' template for GET requests






@login_required(login_url="login")
def sell_partial_db(request):
    try:
        # Parse JSON data from the request body
        data = json.loads(request.body)

        # Extract asset details from the request
        stock_code = data.get('stock_code')
        sell_price = data.get('buy_price')  # This is the price at which the stock is being sold
        no_of_shares = data.get('no_of_shares')
        portfolio_name = data.get('portfolioName')

        # Get the portfolio related to the current user
        portfolio = Portfolio.objects.filter(owner=request.user.profile, portfolio_desc=portfolio_name).first()

        if not portfolio:
            return JsonResponse({"message": "No Portfolio Exists with this Description!", "category": "danger"}, status=201)

        # Check if the asset exists
        asset = Asset.objects.filter(ticker=stock_code).first()

        if not asset:
            return JsonResponse({"message": "No Asset with this Ticker - Contact Admin!", "category": "danger"}, status=201)

        # Retrieve the portfolio asset (the holding) for the specified asset in the portfolio
        holding = PortfolioAsset.objects.filter(portfolio=portfolio, asset=asset).first()

        if not holding:
            return JsonResponse({"message": "This Portfolio does not contain this Asset", "category": "danger"}, status=201)

        # Ensure the user is selling fewer shares than they hold
        if int(holding.no_of_shares) < int(no_of_shares):
            return JsonResponse({"message": "Not Enough Shares to Sell - Change Volume!", "category": "danger"}, status=201)

        # Ensure the user is not selling all shares, else handle it separately
        if int(holding.no_of_shares) == int(no_of_shares):
            return JsonResponse({"message": "Volume = Remaining Shares - Use Sell button on Asset", "category": "danger"}, status=201)

        # Update the holding: reduce the number of shares and holding value
        holding.no_of_shares -= float(no_of_shares)
        holding.holding_value -= float(sell_price) * float(no_of_shares)

        # Update the portfolio's total cash balance
        portfolio.total_cash_balance += round(float(sell_price) * float(no_of_shares), 2)

        # Commit the changes using a transaction to ensure data integrity
        with transaction.atomic():
            holding.save()  # Save the updated holding
            portfolio.save()  # Save the updated portfolio

        return JsonResponse({
            "message": f"Sold Equity: {stock_code} (Sell Price: {sell_price}), Value: {(float(sell_price) * float(no_of_shares))}",
            "category": "success"
        }, status=201)

    except Exception as e:
        # Handle any exceptions that may occur
        return JsonResponse({"error": str(e)}, status=400)