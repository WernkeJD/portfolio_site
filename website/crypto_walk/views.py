from django.shortcuts import render
from crypto_walk.models import Tickers, DailySelections, Selections, Portfolio
from django.http import HttpRequest, HttpResponse, JsonResponse
import json
import requests
import os
from dotenv import load_dotenv
import random
import yfinance as yf
import pandas as pd
import datetime
from django.views.decorators.csrf import csrf_exempt
import time

load_dotenv()

coin_key = os.getenv("COINGECKO_API_KEY")

# Create your views here.

#helpers
def get_coin_price(coins: list):
    ids = ",".join(coins)
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ids, "vs_currencies": "usd"}
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    return data

def get_stock_price(tickers: list):

    today = datetime.date.today()
    # yfinance expects string dates
    start = today.strftime('%Y-%m-%d')
    end = (today + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    ticker_data = yf.download(tickers, start=start, end=end, interval="1d")

    opening_prices = {}
    if not ticker_data.empty:
        # If multiple tickers, columns are multi-index
        if isinstance(ticker_data.columns, pd.MultiIndex):
            for ticker in tickers:
                try:
                    opening_price = ticker_data["Open"][ticker].iloc[0]
                    opening_prices[ticker] = opening_price
                except Exception as e:
                    opening_prices[ticker] = None
        else:
            # Single ticker
            opening_prices[tickers[0]] = ticker_data["Open"].iloc[0]
    else:
        for ticker in tickers:
            opening_prices[ticker] = None

    return opening_prices



#main function on page load
def pick_crypto(request: HttpRequest):
    if request.method == 'GET':
        crypto1 = None
        crypto2 = None
        stock1 = None
        stock2 = None

        check = DailySelections.objects.filter(date=datetime.date.today())

        if not check:

            response = requests.get("https://api.coingecko.com/api/v3/coins/list", headers={'accept': 'application/json', 'x-cg-pro-api-key': coin_key})

            if response.status_code == 200:
                print("response: ", response.text)

                try:
                    json_data = response.json()
                    print("json: ", json_data)

                    crypto1 = json_data[random.randint(0, len(json_data))]["id"]
                    crypto2 = json_data[random.randint(0, len(json_data))]["id"]
                    # stock1 = Tickers.objects.get(id=(random.randint(42178, 45177))).ticker
                    # stock2 = Tickers.objects.get(id=(random.randint(42178, 45177))).ticker
                    stock1 = Tickers.objects.get(id=(random.randint(1, 3000))).ticker
                    stock2 = Tickers.objects.get(id=(random.randint(1, 3000))).ticker

                    
                    coin_prices = get_coin_price([crypto1, crypto2])
                    crypto_1_value = coin_prices[crypto1]["usd"]
                    crypto_2_value = coin_prices[crypto2]["usd"]

                    stock_prices = get_stock_price([stock1, stock2])
                    print("stock prices: ", stock_prices)

                    stock_1_value = stock_prices[stock1]
                    stock_2_value = stock_prices[stock2]

                    DailySelections.objects.create(date=datetime.date.today(), crypto_1=crypto1, crypto_2=crypto2, stock_1=stock1, stock_2=stock2, crypto_1_price=crypto_1_value, crypto_2_price=crypto_2_value, stock_1_price=stock_1_value, stock_2_price=stock_2_value)

                except json.decoder.JSONDecodeError:
                    print("response is not valid json")
            else:
                print(f"Request failed with status code: {response.status_code}")
                print("Error message:", response.text)  
        else:
            data = DailySelections.objects.get(date=datetime.date.today())
            crypto1 = data.crypto_1
            crypto2 = data.crypto_2
            stock1 = data.stock_1
            stock2 = data.stock_2
            
        return render(request, 'pick_crypto.html', {"crypto1": crypto1, "crypto2": crypto2, "stock1": stock1, "stock2": stock2})
    
        
@csrf_exempt
def update_clicks(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        selection = data.get("selection")

        try:
            daily = DailySelections.objects.get(date=datetime.date.today())
        except DailySelections.DoesNotExist:
            return JsonResponse({"error": "No daily selection found"}, status=404)

        if selection == "crypto1":
            daily.crypto_1_selections += 1
        elif selection == "crypto2":
            daily.crypto_2_selections += 1
        elif selection == "stock1":
            daily.stock_1_selections += 1
        elif selection == "stock2":
            daily.stock_2_selections += 1
        else:
            return JsonResponse({"error": "Invalid selection"}, status=400)

        daily.save()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
@csrf_exempt
def update_selections(request: HttpRequest) -> HttpResponse:

    investment_amount = 100 #dollars

    try:
        daily_selections = DailySelections.objects.get(date=datetime.date.today() - datetime.timedelta(days=1))
    except DailySelections.DoesNotExist:
        return HttpResponse("No daily selections found for yesterday", status=404)

    if daily_selections.crypto_1_selections > daily_selections.crypto_2_selections:
        crypto_selection = daily_selections.crypto_1
        crypto_price = daily_selections.crypto_1_price
        crypto_shares = investment_amount / crypto_price
    else:
        crypto_selection = daily_selections.crypto_2
        crypto_price = daily_selections.crypto_2_price
        crypto_shares = investment_amount / crypto_price


    if daily_selections.stock_1_selections > daily_selections.stock_2_selections:
        stock_selection = daily_selections.stock_1
        stock_price = daily_selections.stock_1_price
        stock_shares = investment_amount / stock_price
    else:
        stock_selection = daily_selections.stock_2
        stock_price = daily_selections.stock_2_price
        stock_shares = investment_amount / stock_price

    try:
        Selections.objects.create(date=datetime.date.today() - datetime.timedelta(days=1), crypto_selection=crypto_selection, crypto_price=crypto_price, number_of_coins_purchased=crypto_shares, stock_selection=stock_selection, stock_price=stock_price, number_of_stock_purchased=stock_shares)
        return HttpResponse("Selection updated successfully")
    except Exception as e:
        print("Error creating selection: ", e)
        return HttpResponse("Error creating selection", status=500)

    
@csrf_exempt
def generate_portfolio_value(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        # Get all selections up to yesterday
        all_selections = Selections.objects.filter(date__lte=yesterday).order_by('date')

        # Get yesterday's selections
        recent_selections = Selections.objects.filter(date=yesterday)

        # Get all unique crypto and stock selections except the most recent two
        older_selections = all_selections.exclude(id__in=recent_selections.values_list('id', flat=True))
        crypto_ids = [s.crypto_selection for s in older_selections]
        stock_ids = [s.stock_selection for s in older_selections]

        # Get latest prices for older holdings
        crypto_prices = get_coin_price(crypto_ids) if crypto_ids else {}
        stock_prices = get_stock_price(stock_ids) if stock_ids else {}

        # Calculate value for older holdings
        crypto_portfolio_value = 0
        stock_portfolio_value = 0
        for s in older_selections:
            crypto_price_latest = crypto_prices.get(s.crypto_selection, {}).get("usd", 0)
            stock_price_latest = stock_prices.get(s.stock_selection, 0)
            crypto_portfolio_value += s.number_of_coins_purchased * crypto_price_latest
            stock_portfolio_value += s.number_of_stock_purchased * stock_price_latest

        # Add value for recent purchases using stored prices
        for s in recent_selections:
            crypto_portfolio_value += s.number_of_coins_purchased * s.crypto_price
            stock_portfolio_value += s.number_of_stock_purchased * s.stock_price

        # Calculate cash for each portfolio
        # Get previous day's cash, or start with 10k if first day
        prev_portfolio = Portfolio.objects.order_by('-date').first()
        if prev_portfolio:
            crypto_cash = prev_portfolio.crypto_cash
            stock_cash = prev_portfolio.stock_cash
        else:
            crypto_cash = 10000
            stock_cash = 10000

        # Subtract yesterday's investments from cash
        crypto_invested = sum([s.crypto_price * s.number_of_coins_purchased for s in recent_selections])
        stock_invested = sum([s.stock_price * s.number_of_stock_purchased for s in recent_selections])
        crypto_cash -= crypto_invested
        stock_cash -= stock_invested

        try:
            Portfolio.objects.create(
                date=today,
                crypto_portfolio_value=crypto_portfolio_value + crypto_cash,
                stock_portfolio_value=stock_portfolio_value + stock_cash,
                crypto_cash=crypto_cash,
                stock_cash=stock_cash
            )
            return HttpResponse("Portfolio value updated successfully")
        except Exception as e:
            print("Error creating portfolio value: ", e)
            return HttpResponse("Error creating portfolio value", status=500)

def portfolio_comparison(request: HttpRequest):
    # Get all portfolio entries ordered by date
    portfolios = Portfolio.objects.order_by('date')
    dates = [p.date.strftime('%Y-%m-%d') for p in portfolios]
    crypto_values = [p.crypto_portfolio_value for p in portfolios]
    stock_values = [p.stock_portfolio_value for p in portfolios]
    return render(request, 'portfolio_comparison.html', {
        'dates': json.dumps(dates),
        'crypto_values': json.dumps(crypto_values),
        'stock_values': json.dumps(stock_values)
    })


def clear_data(request: HttpRequest):
    selections = Selections.objects.all()
    portfolios = Portfolio.objects.all()

    portfolios.delete()
    selections.delete()

    selections_check = Selections.objects.all()
    portfolios_check = Portfolio.objects.all()

    if not selections_check and not portfolios_check:
        return HttpResponse("data cleared", status=200)
    else:
        return HttpResponse("data not deleted", status=500)





