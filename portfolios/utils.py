from django.shortcuts import render,redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from django.http import HttpResponse ,  HttpRequest , JsonResponse
from django.contrib.auth.models import User
from users.forms import CustomUserCreationForm , ProfileForm
from .models import Profile
from portfolios.models import Asset ,AssetHistory , PortfolioAsset  ,Portfolio
import os
import io
import yfinance as yf
from datetime import datetime, timedelta, date
from django.db import transaction
from django.db.models import F,Max
from django.contrib.contenttypes.models import ContentType
from .models import Cash

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend
import pandas as pd
# from yahooquery import Ticker
# from concurrent.futures import ThreadPoolExecutor
CURRENT_DIR =  os.getcwd()


# def is_manager(user):
#     profile = user.profile
#     return profile.group.name == 'Manager' if profile.group else False

###################################################################################
####GET SINGLE LATEST PRICE
###################################################################################
def get_latest_price (ticker,asset,portfolio):

    if portfolio != '':
        print('THIS IS A PORTFOLIO' , portfolio , "ASSET", asset)
        portfolio = Portfolio.objects.get(id=portfolio)
        asset_value = portfolio.total_holding_value()
        cash_value = portfolio.total_cash_balance
        total_value = asset_value + cash_value
        price  = total_value/portfolio.units

        print(total_value , asset_value ,cash_value , price , portfolio.units )
        return price
    else:
        print('THIS IS NOT A PORTFOLIO' , portfolio , "ASSET", asset)
    print("TICKER",ticker)
    stock = yf.Ticker(ticker)
    stock_info = stock.history(period="1d", actions=False,rounding=True)
    print(stock_info)
    last_quote = stock_info['Close'].iloc[-1]
    print (f" Last Quote : {last_quote}")
    return last_quote

###################################################################################
####GET LATEST PRICES FROM A LIST OF ASSETS IN THE PORTFOLIO
###################################################################################

def get_latest_portfolio_prices(portfolio):
    print(portfolio)
    
    portfolio_assets = PortfolioAsset.objects.filter(portfolio_id=portfolio).select_related('asset')

    print(portfolio_assets)
    # Extract tickers from the portfolio assets
    tickers = [asset.asset.ticker for asset in portfolio_assets if asset.asset.is_portfolio != True]

    if not tickers:
        # If no tickers are provided, return an empty dictionary or handle accordingly
        print("No stocks available in the portfolio.")
        return {}
    print(tickers)
    # Fetch the latest stock prices from Yahoo Finance
    ticker_data = yf.download(tickers, period="1d", interval="1d" ,actions=False,rounding=True)
    closing_prices = ticker_data['Close'].iloc[-1]  # Get the last available row (latest data)

        # Check if the result contains multiple tickers or just one
    if len(tickers) == 1:
        # If there's only one ticker, yfinance returns a scalar DataFrame
        closing_prices = ticker_data['Close']
        return {tickers[0]: closing_prices.iloc[-1]}  # Single ticker case
    else:
        # If multiple tickers, fetch the closing prices as a Series
        closing_prices = ticker_data['Close'].iloc[-1]  # Last available row
        return {ticker: closing_prices[ticker] for ticker in tickers}

###################################################################################
####GET MAX DATE FOR ASSET IN TO REDUCE REQUEST DATE RANGE
###################################################################################

def get_max_date_for_asset(asset_id):
    max_date = AssetHistory.objects.filter(asset_id=asset_id).aggregate(Max('date'))['date__max']
    return max_date

###################################################################################
####REQUEST PRICES FOR MAX 30 DAYS FROM YAHOO
################################################################################### 
# Function to get stock price using Yahoo Finance API
def get_stock_price(stock_code,asset_id,portfolio,yf_flag,user_id,buy_price):
    # print(yf_flag)
    print(f"Stock Code {stock_code}")
    print(f"Asset ID {asset_id}")
    print(f"Portfolio ID {portfolio}")
    print(f"yf_flag {yf_flag}")
    print(f"user_id {user_id}")
    print(f"buy_price {buy_price}")
    chk_ast = Asset.objects.get(id=asset_id)
    print("CHECK::::::::::",chk_ast.is_portfolio)
    if chk_ast.is_portfolio == True:
        print('THIS IS A PORTFOLIO' , chk_ast.portfolio)
        portfolio = Portfolio.objects.get(id=chk_ast.portfolio.id)
        asset_value = portfolio.total_holding_value()
        cash_value = portfolio.total_cash_balance
        total_value = asset_value + cash_value
        price  = total_value/portfolio.units

        print(total_value , asset_value ,cash_value , price , portfolio.units )
        return ((stock_code,price,""))
    
    if yf_flag == 'on'  and chk_ast.is_portfolio != True:
        
        try:
            max_date = get_max_date_for_asset(asset_id)
            if max_date is None:
                print(f"Max Date NONE : {max_date}")
                start_date = datetime.today() - timedelta(days=30)  # Default to 1 month ago if no data
            else:
                print(f"Max Date : {max_date}")
                start_date = max_date  # Next day after max date
            
            end_date = datetime.today()
            ##create an object of the yahoo ticker
            stock = yf.Ticker(stock_code)
            ##get the history from 30 days max  - max date to today or 30 days to create the graph
            yahoo_stock_info = stock.history(start=start_date, end=end_date, actions=False, rounding=True)
       
            yahoo_stock_info.dropna(inplace=True)
            # Fetch historical data using yfinance

            # Insert or update the historical data into the database
            #REASON - - -- - IF YAHOO FLAG IS OFF THE SVG CAN STILL BE CREATED
            for date, row in yahoo_stock_info.iterrows():
                date_only = date.date()  # Get only the date part (without time)
                
                # Check if the record already exists
                existing_entry = AssetHistory.objects.filter(asset_id=asset_id, date=date_only).first()
                
                if existing_entry:
                    # Update the existing record
                    existing_entry.open_price = row['Open']
                    existing_entry.high_price = row['High']
                    existing_entry.low_price = row['Low']
                    existing_entry.close_price = row['Close']
                    existing_entry.volume = row['Volume']
                else:
                    # Create a new record
                    AssetHistory.objects.create(
                        asset_id=asset_id,
                        date=date_only,
                        open_price=row['Open'],
                        high_price=row['High'],
                        low_price=row['Low'],
                        close_price=row['Close'],
                        volume=row['Volume']
                    )
                
            print(f"Historical data for {stock_code} saved/updated successfully.")

            ################exit yahoo try
        except Exception as e:
            print(f"Error processing yahoo DATA {stock_code}: {e}")
            return "Error: " + str(e)
        
        ######END IF yf_flag is Y - - -  add Condition to based on MAX Date 

        # Input buy price (manually specified)
        # buy_price = buy_price  # Example: bought the stock at $150
    print(f"THIS IS THE BUY PRICE IN STOCK FUNCTION  ::::::  {buy_price}")
    
    today = datetime.today()
    ##############DATABASE PRICES INSTEAD OF YFINANCE DIRECT  ####################################  
    
    # Query the AssetHistory table for the asset's historical data  -  USE THE ASSET HISTORY RELATIONSHIP TO THE PORTFOLIO ASSET
    # PRICES ARE AGNOSTIC OF PORTFOLIO THAT HOLDS THE ASSET
    historical_data = AssetHistory.objects.filter(
        asset_id=asset_id, 
        date__gte=today - timedelta(days=30)  # Get data for the last 30 days
    ).order_by('date')  # Order by the 'date' field

    print(historical_data)
    # Prepare lists for plotting
    dates = [entry.date for entry in historical_data]
    closing_prices = [entry.close_price for entry in historical_data]

    ####USE PANDAS To creeate the data frams
    stock_info = pd.DataFrame({
                                'Date': dates,
                                'Close': closing_prices
                            })
    stock_info.set_index('Date', inplace=True)
    if len(closing_prices) >= 7:
        
        moving_averages = [
        sum(closing_prices[i-7:i]) / 7 if i >= 7 else None for i in range(len(closing_prices))
        ]
        stock_info['SMA'] = stock_info['Close'].rolling(window=7).mean().dropna()  ##mean
        stock_info['STD'] = stock_info['Close'].rolling(window=7).std().dropna()   ##standard deviation
        print(stock_info.head())
        print(stock_info.dtypes)
        # Calculate the Upper and Lower Bollinger Bands
        stock_info['Upper Band'] = stock_info['SMA'] + (stock_info['STD'] * 1.96)
        stock_info['Lower Band'] = stock_info['SMA'] - (stock_info['STD'] * 1.96)
    
    
    else:
        moving_averages = [None] * len(closing_prices)  # Not enough data for MA
    print(f"Moving Averages : {moving_averages}")


    ########SVG FROM DATABASE #########
    # Prepare to capture SVG output
    svg_buffer = io.StringIO()

    # Create a plot
    plt.figure(figsize=(10, 5))

    # Plot the closing price
    plt.plot(dates, closing_prices, label='Closing Price', color='blue')

    # Plot Upper
    plt.plot(stock_info.index, stock_info['Upper Band'], label='Upper Band', color='green')

    # Plot the 7-day moving average
    plt.plot(dates, moving_averages, label='7 Day MA', color='orange')
    
    plt.plot(stock_info.index, stock_info['Lower Band'], label='Lower Band', color='red')

    plt.fill_between(stock_info.index, stock_info['Lower Band'], stock_info['Upper Band'], color='gray', alpha=0.3)
        
    # Plot the buy price as a horizontal benchmark line
    plt.axhline(y=buy_price, color='green', linestyle='--', label=f'Buy Price (${buy_price})')
    

    # Add labels and title
    plt.title(f'{stock_code} Stock Performance - Last 1 Month - As of {today.date()}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

    # Save the plot to the SVG buffer
    plt.savefig(svg_buffer, format='svg')
    plt.close()  # Close the plot to free up memory

    # Get the SVG content as a string
    svg_content = svg_buffer.getvalue()
    svg_buffer.close()  # Close the buffer

    # Fetch the portfolio based on user_id
    # portfolio = Portfolio.query.filter_by(user_id=user_id).first()

    # Check if the portfolio exists
    if portfolio:
        print(f"Portfolio ID: {portfolio}")

        # Fetch the PortfolioAsset instance
        # portfolio_asset = PortfolioAsset.query.filter_by(portfolio_id=portfolio.id, asset_id=asset.id).first()
        portfolio_asset = PortfolioAsset.objects.filter(portfolio_id=portfolio, asset_id=asset_id).first()
        print(f"DEBUG  -  - - -  - - - Portfolio ID: {portfolio}")
         # Check if the portfolio exists
    if portfolio:
        print(f"Portfolio ID: {portfolio}")

        # Fetch the PortfolioAsset instance
        try:
            portfolio_asset = PortfolioAsset.objects.filter(portfolio_id=portfolio, asset_id=asset_id).first()

            if portfolio_asset:
                print(f"Found Portfolio Asset: {portfolio_asset}")

                # Update the `svg_content`
                portfolio_asset.svg_content = svg_content
                portfolio_asset.save()  # Save changes to the database
                print(f"Updated Portfolio Asset: {portfolio_asset}")
                print("SVG content updated successfully.")
            else:
                print(f"No Portfolio Asset found for Portfolio ID: {portfolio.id} and Asset ID: {asset_id}")
        except Exception as e:
            print(f"Error querying or updating PortfolioAsset: {e}")
    else:
        print("Portfolio not provided or does not exist.")
    

    if not stock_info.empty:
        print(f"Returned to dashboard : {stock_code},{round(stock_info['Close'].iloc[-1], 2)},{stock.isin}")
        return (stock_code,round(stock_info['Close'].iloc[-1], 2),stock.isin)  # Get the last closing price
    else:
        return (("Invalid Ticker","",""))
    


def handle_cash_update_or_create(asset, buy_price, no_of_shares, new_units, managed_portfolio,buy_or_sell):
    # Use transaction.atomic to ensure all changes are committed atomically
    print(new_units," :  NEW UNITS IN HANDLE")
    with transaction.atomic():
        # Attempt to update or create the Cash entry
        cash, created = Cash.objects.update_or_create(
            portfolio=asset.portfolio,
            owner_content_type=ContentType.objects.get_for_model(Portfolio),
            owner_object_id=managed_portfolio.id,
            defaults={
                "currency": "USD",  # Default value for currency, not balance or units
            }
        )

        # If it's created, initialize balance and units
        if created:
            previous_balance = 0
            previous_units = 0
            cash.balance = float(buy_price) * float(no_of_shares)
            cash.units = new_units
            cash.save()
            print(f"Created new Cash entry for portfolio {asset.portfolio.id} with balance {cash.balance} and Owner {managed_portfolio.id}.")
            
        else:
            # Retrieve previous values before saving the updated instance
            previous_balance = cash.balance
            previous_units = cash.units

            # Increment balance and units for the existing instance
            if buy_or_sell == 'BUY':
                cash.balance += float(buy_price) * float(no_of_shares)
                cash.units += new_units
            else:
                cash.balance -= float(buy_price) * float(no_of_shares)
                cash.units += new_units
            cash.save()

            # Calculate the difference in balance and units
            balance_diff = cash.balance - previous_balance
            print("CASH DIFF",balance_diff)
            units_diff = cash.units - previous_units
            print(f"Updated Cash entry for portfolio {asset.portfolio.id} with balance diff {balance_diff} and units diff {units_diff}.")

        # Perform Portfolio update with the diff values (regardless of create or update)
        balance_diff = cash.balance - previous_balance
        print(f"BALANCE: DIFF : {balance_diff}")
        units_diff = cash.units - previous_units
        Portfolio.objects.filter(id=asset.portfolio.id).update(
            total_cash_balance=F('total_cash_balance') + balance_diff,
            units=F('units') + units_diff
        )

        Portfolio.objects.filter(id=managed_portfolio.id).update(
            total_cash_balance=F('total_cash_balance') - balance_diff,
            units=F('units') + units_diff
        )

    return cash




def handle_cash_update_or_create_investor(portfolio, buy_price, new_units,owner,buy_or_sell,user):
    # Use transaction.atomic to ensure all changes are committed atomically
    print(new_units," :  NEW UNITS IN HANDLE")
    with transaction.atomic():
        portfolio_obj = Portfolio.objects.get(id=portfolio)
        # Attempt to update or create the Cash entry
        cash, created = Cash.objects.update_or_create(
            portfolio=portfolio_obj,
            owner_content_type=ContentType.objects.get_for_model(Profile),
            owner_object_id=user,
            defaults={
                "currency": "USD",  # Default value for currency, not balance or units
            }
        )

        # If it's created, initialize balance and units
        if created:
            previous_balance = 0
            previous_units = 0
            cash.balance = float(buy_price) ##* float(no_of_shares)
            cash.units = new_units
            cash.save()
            print(f"Created new Cash entry for portfolio {portfolio} with balance {cash.balance} and Owner {user}.")
            
        else:
            # Retrieve previous values before saving the updated instance
            previous_balance = cash.balance
            previous_units = cash.units
            cash.balance += float(buy_price) ##* float(no_of_shares)
            cash.units += new_units
            cash.save()


            # Calculate the difference in balance and units
            balance_diff = cash.balance - previous_balance
            print("CASH DIFF",balance_diff)
            units_diff = cash.units - previous_units
            print(f"Updated Cash entry for portfolio {portfolio} with balance diff {balance_diff} and units diff {units_diff}.")

        # Perform Portfolio update with the diff values (regardless of create or update)
        balance_diff = cash.balance - previous_balance
        print(f"BALANCE: DIFF : {balance_diff}")
        units_diff = cash.units - previous_units
        Portfolio.objects.filter(id=portfolio).update(
            total_cash_balance=F('total_cash_balance') + balance_diff,
            units=F('units') + units_diff
        )

        Profile.objects.filter(id=user).update(
            balance=F('balance') - balance_diff,
        )

    return cash
