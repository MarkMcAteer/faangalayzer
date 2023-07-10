from converter.Data import *
from django.core.cache import cache
from .Data import *
from datetime import date
import pickle
import os

# Stock class -------------------------------------------------------------------------------------

# This class will provide the information of a stock that will supply
# information to the website. This will be seperate from a users stock.
# A users stock can be built as a subclass which will have a date_of_purchase
# and amount invested.

class Stock:
    def __init__(self, symbol):
        self.symbol = symbol
        self.dates = []
        self.adjusted = []
        self.fetch_stock_data()

    def stock_symbol(self):
        return self.symbol

    def get_dates(self):
        return self.dates

    def get_adjusted(self):
        return self.adjusted

    def plot_data(self):
        plot_stock(self.dates, self.adjusted)

    def get_daily_growth(self):
        return daily_percentage_gain(self.dates, self.adjusted)

    def get_current_price(self):
        if len(self.adjusted) > 0:
            return self.adjusted[0]
        else:
            return None

    def fetch_stock_data(self):
        stock_data = cache.get(f'stock_data:{self.symbol}')

        if stock_data is None:
            # Retrieve stock data using API or any other method
            get_stock_data(self.dates, self.adjusted, self.symbol)

            stock_info = {
                'symbol': self.symbol,
                'dates': self.dates,
                'adjusted': self.adjusted
            }

            cache.set(f'stock_data:{self.symbol}', stock_info, timeout=3600)  # Cache indefinitely
        else:
            self.symbol = stock_data['symbol']
            self.dates = stock_data['dates']
            self.adjusted = stock_data['adjusted']

    def set_data(self, dates, adjusted):
        self.dates = dates
        self.adjusted = adjusted



# Investor class ----------------------------------------------------------------------------------

class Investor:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.balance = 0.0
        # Portfolio Dictonary containing the name of the stock and the number of
        # shares that the investor holds of that stock
        self.portfolio = {}
        # List of past transactions
        self.transactions = []

    def get_username(self):
        return self.username

    def get_balance(self):
        return float(str(self.balance))

    def get_portfolio(self):
        return self.portfolio

    def get_transactions(self):
        return self.transactions

#    def print_portfolio(self):
#        print(self.portfolio)

#    def print_transactions(self):
#        for i in self.transactions:
#            print(i)

    def deposit(self, value):
        self.balance += value

    def withdraw(self, value):
        self.balance -= value

    def buy_stock(self, stock, num_shares):
        price = stock.get_current_price() * float(num_shares)
        if self.balance > price:
            self.balance -= price
            if checkKey(self.portfolio, stock.stock_symbol()):
                current_shares = self.portfolio[stock.stock_symbol()]
                self.portfolio.update({stock.stock_symbol(): (float(num_shares) + float(current_shares))})
            else:
                self.portfolio.update({stock.stock_symbol(): num_shares})
            self.transactions.append(stock.stock_symbol() + ": " + str(date.today()) + ": " + str(num_shares) + " share(s) purchased")
        else:
        # print("Insufficient funds.")
            pass

    def sell_stock(self, stock, num_shares):
        value = stock.get_current_price() * float(num_shares)
        # First check if the investor has this stock in their portfolio.
        if checkKey(self.portfolio, stock.stock_symbol()):
            current_shares = self.portfolio[stock.stock_symbol()]
            # If the current number of shares is less than the amount you are trying to sell,
            # tell the investor they do not have enough of these shares to sell.
            if float(num_shares) > float(current_shares) :
                #print("You don't have " + str(num_shares) + " share(s) to sell, you have " + str(current_shares) + " share(s) in your account.")
                pass
            else:
                self.portfolio.update({stock.stock_symbol(): (float(current_shares) - float(num_shares))})
                self.transactions.append(stock.stock_symbol() + ": " + str(date.today()) +  ": " + str(num_shares) + " share(s) sold")
                self.balance += value
                # If the investor has no more of these shares left in their portfolio, remove the stock.
                if float(current_shares) - float(num_shares) == 0.0:
                    del self.portfolio[stock.stock_symbol()]
        else:
            #print("You don't have this stock in your portfolio.")
            pass


# Save Investor data to a file
def save_investor_data(investor):
    filename = f"{investor.username}.pkl"
    with open(filename, "wb") as file:
        pickle.dump(investor, file)

# Load Investor data from a file
def load_investor_data(username):
    filename = f"{username}.pkl"
    with open(filename, "rb") as file:
        investor = pickle.load(file)
    return investor

def check_username_exists(username):
    filename = f"{username}.pkl"
    return os.path.exists(filename)

def check_username_password(username, password):
    filename = f"{username}.pkl"

    if os.path.exists(filename):
        with open(filename, "rb") as file:
            investor = pickle.load(file)
        return investor.password == password

    return False
