# DailyData.py
# Mark McAteer 2023

# A file that contains functions for getting stock data, processing it, and
# using that data to preform useful tasks.

import requests
import json
from matplotlib import pyplot as plt
import matplotlib.dates

api_key = 'A0VEH0LB62A3U5QJ'

# Get the stock data ------------------------------------------------------------------------------
# A function that will fill in the stock data given an empty date array,
# an empty adjusted array, and the stock symbol or name

def get_stock_data(dates_list, adjusted_list, symbol):

    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={api_key}'

    response = requests.get(url)
    data = response.json()

    if 'Time Series (Daily)' in data:
        time_series = data['Time Series (Daily)']

        # Retrieve the daily adjusted prices for the last 5 years
        for date, values in list(time_series.items())[:1825]:  # 365 days * 5 years = 1825 data points
            adjusted_price = values['5. adjusted close']
            dates_list.append(date)
            adjusted_list.append(float(adjusted_price))
    else:
        print('Error retrieving stock data.')

# Plot the stock data -----------------------------------------------------------------------------

def plot_stock(stock_dates, stock_adjusted):
    converted_dates = matplotlib.dates.datestr2num(stock_dates)

    x_axis = (converted_dates)

    y_axis = stock_adjusted
    plt.plot_date( x_axis, y_axis, '-' )

    plt.show()

# Function to determine the growth percentage from a date of purchase -----------------------------

def total_percentage_gain(date_of_purchase, stock_dates, stock_adjusted):
    counter = 0
    for i in stock_dates:
        if i == date_of_purchase:
            break
        counter += 1

    if counter < len(stock_adjusted):
        growth_percentage = ((stock_adjusted[0] - stock_adjusted[counter]) / stock_adjusted[counter]) * 100
        #print("From " + stock_dates[counter] + " to " + stock_dates[0] + " and the adjusted growth is: " + str(growth_percentage) + "%")
        return growth_percentage
    else:
        print("Invalid date of purchase, insufficient data points or API limit reached.")

# Function to determine the percentage increase from the previous days ----------------------------
# Check that the list contains enough elements
# If so, ubtract the current stock price from that of the previous day and divide
# that by the current stock price to get the percentage gain

def daily_percentage_gain(stock_dates, stock_adjusted):
    if len(stock_adjusted) >= 2:
        growth_percentage = ((stock_adjusted[0] - stock_adjusted[1]) / stock_adjusted[1]) * 100
        #print("The date is " + stock_dates[0] + " and the adjusted daily growth is: " + str(growth_percentage) + "%")
        return growth_percentage
    else:
        print("Insufficient data points to calculate daily growth or API limit reached.")


# Short function from GeeksForGeeks, credited in MAKEFILE, that checks if a
# dictionary contains a key. This will be used to deteremine if an investor already
# has the stock they're trying to purchase in their portfolio.
def checkKey(dic, key):
    if key in dic:
        return True
    else:
        return False




#
