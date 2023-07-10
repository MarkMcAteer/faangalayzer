from .models import Code
import io
import sys
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse
from .Classes import *

def converter(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if check_username_exists(username):
            count = 0
            entered = False  # Initialize entered variable
            error_message = ""  # Initialize error message
            messages = []  # List to store messages
            while not entered:
                if check_username_password(username, password):
                    messages.append("Welcome, " + username)
                    entered = True
                else:
                    error_message = "Incorrect Password. Try again."
                    password = ""  # Clear the password field
                    count += 1
                    if count == 3:
                        break
            if entered:
                investor = load_investor_data(username)
                messages.append("User data loaded.")
                request.session['username'] = username
                # Redirect to a new page and pass the username as a parameter
                return redirect('converter:investor-details')  # Replace 'investor_details' with your desired URL name

        else:
            investor = Investor(username, password)
            save_investor_data(investor)
            messages.append("New user created.")
            request.session['username'] = username
            # Redirect to a new page and pass the username as a parameter
            return redirect('converter:investor-details')  # Replace 'investor_details' with your desired URL name

        return render(request, 'converter.html', {'messages': messages, 'error_message': error_message})

    return render(request, 'converter.html')


def investor_details(request):
    # Retrieving username from session
    username = request.session.get('username')
    investor = load_investor_data(username)

    if not username:
        messages.error(request, 'Please log in.')
        return redirect('converter:converter')

    # Assuming you have the investor's name and balance available
    investor_name = username
    investor_balance = "$" + str(round(investor.get_balance(), 2))
    current_date = date.today()

    # Check if the stock data is already cached
    stock_data = cache.get('stock_data')

    if not stock_data:
        # Stock data is not cached, retrieve it from the Stock class
        stock_list = [
            {'symbol': 'META', 'dates': [], 'adjusted': [], 'growth': ""},
            {'symbol': 'AMZN', 'dates': [], 'adjusted': [], 'growth': ""},
            {'symbol': 'AAPL', 'dates': [], 'adjusted': [], 'growth': ""},
            {'symbol': 'NFLX', 'dates': [], 'adjusted': [], 'growth': ""},
            {'symbol': 'GOOG', 'dates': [], 'adjusted': [], 'growth': ""},
        ]

        for stock_info in stock_list:
            stock = Stock(stock_info['symbol'])
            stock.fetch_stock_data()
            stock_info['dates'] = stock.get_dates()
            stock_info['adjusted'] = stock.get_adjusted()
            if (stock.get_daily_growth() > 0 ):
                stock_info['growth'] = "+" + str(round(stock.get_daily_growth(), 2)) + "%"
            else:
                stock_info['growth'] = str(round(stock.get_daily_growth(), 2)) + "%"

        # Cache the stock data for future use
        cache.set('stock_data', stock_list, timeout=3600)  # timeout=None means cache indefinitely


    portfolio = investor.get_portfolio()
    transactions = investor.get_transactions()

    # Calculate the total value of each stock in the portfolio
    portfolio = investor.get_portfolio()
    for stock_info in stock_data:
        stock_symbol = stock_info['symbol']
        if stock_symbol in portfolio:
            num_shares = portfolio[stock_symbol]
            stock_price = stock_info['adjusted'][0]  # Get the adjusted price
            total_value = stock_price * float(num_shares)  # Calculate total value as float
            stock_info['total_value'] = round(total_value, 2)  # Add total value to stock_info
        else:
            stock_info['total_value'] = 0  # Stock not in portfolio, set total value to 0

    context = {
        'investor_name': investor_name,
        'current_date': current_date,
        'investor_balance': investor_balance,
        'stock_data': stock_data,
        'portfolio': portfolio,
        'transactions': transactions,
    }

    return render(request, 'investor-details.html', context)

def deposit_value(request):
    # Retrieving username from session
    username = request.session.get('username')
    investor = load_investor_data(username)

    if not username:
        messages.error(request, 'Please log in.')
        return redirect('converter:converter')

    if request.method == 'POST':
        value = float(request.POST.get('value'))
        # Perform any processing or store the value in a variable as needed
        investor.deposit(value)
        save_investor_data(investor)

    return redirect('converter:investor-details')

def withdraw_value(request):
    # Retrieving username from session
    username = request.session.get('username')
    investor = load_investor_data(username)

    if not username:
        messages.error(request, 'Please log in.')
        return redirect('converter:converter')

    if request.method == 'POST':
        value = float(request.POST.get('value'))
        # Perform any processing or store the value in a variable as needed
        investor.withdraw(value)
        save_investor_data(investor)

    return redirect('converter:investor-details')

def buy_stock_view(request):
    if request.method == 'POST':
        stock_name = request.POST['stock_name']
        shares = request.POST['num_shares']

        # Retrieve the investor's username from the session
        username = request.session.get('username')

        # Retrieve the investor's data from the database
        investor = load_investor_data(username)

        # Check if the stock data is already cached
        stock_data = cache.get('stock_data')

        if not stock_data:
            # Handle the case when stock data is not available
            return HttpResponse('Stock data is not available')

        selected_stock = None
        for stock_info in stock_data:
            if stock_info['symbol'] == stock_name:
                selected_stock = Stock(stock_info['symbol'])
                selected_stock.set_data(stock_info['dates'], stock_info['adjusted'])
                break

        if selected_stock:
            stock_price = selected_stock.get_current_price()

            if stock_price is None:
                return HttpResponse('Stock price is not available')

            # Calculate the total cost of the shares
            total_cost = stock_price * float(shares)

            # Check if the investor has enough balance to buy the shares
            if investor.get_balance() >= total_cost:
                # Call the buy_stock function and pass the selected stock and number of shares
                investor.buy_stock(selected_stock, shares)

                # Save the investor's updated data to the database
                save_investor_data(investor)

                messages.success(request, 'Stock added successfully.')
            else:
                messages.error(request, 'Insufficient balance to buy the shares.')

        else:
            messages.error(request, 'Invalid stock name.')

        return redirect('converter:investor-details')

    return render(request, 'add-stock.html')

def sell_stock_view(request):
    if request.method == 'POST':
        stock_name = request.POST['stock_name']
        shares = request.POST['num_shares']

        # Retrieve the investor's username from the session
        username = request.session.get('username')

        # Retrieve the investor's data from the database
        investor = load_investor_data(username)

        # Check if the stock data is already cached
        stock_data = cache.get('stock_data')

        if not stock_data:
            # Handle the case when stock data is not available
            return HttpResponse('Stock data is not available')

        selected_stock = None
        for stock_info in stock_data:
            if stock_info['symbol'] == stock_name:
                selected_stock = Stock(stock_info['symbol'])
                selected_stock.set_data(stock_info['dates'], stock_info['adjusted'])
                break

        if selected_stock:
            stock_price = selected_stock.get_current_price()

            if stock_price is None:
                return HttpResponse('Stock price is not available')

            # Check if the investor has this stock in their portfolio
            if checkKey(investor.get_portfolio(), selected_stock.stock_symbol()):
                current_shares = investor.get_portfolio()[selected_stock.stock_symbol()]

                # If the current number of shares is less than the amount you are trying to sell,
                # tell the investor they do not have enough shares to sell.
                if float(shares) > float(current_shares):
                    return HttpResponse("You don't have enough shares to sell.")

                # Call the sell_stock function and pass the selected stock and number of shares
                investor.sell_stock(selected_stock, shares)

                # Save the investor's updated data to the database
                save_investor_data(investor)

                messages.success(request, 'Stock sold successfully.')
            else:
                messages.error(request, 'Invalid stock name or you do not own this stock.')

        else:
            messages.error(request, 'Invalid stock name.')

        return redirect('converter:investor-details')

    return render(request, 'sell-stock.html')
