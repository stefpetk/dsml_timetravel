import pandas as pd
import numpy as np
import glob
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

def valuation(buy_df, sell_df, st_cap=1, n_seq=0):
    """
    This function takes as input the dataframes with the associated cost and profit from the stock transactions
    sequence and then plots the valuation diagrams.
    Args:
        buy_df: a dataframe with the stock buying transactions
        sell_df: a dataframe with the stock selling transactions
        st_cap: starting investment capital
        n_seq: the length of the transactions sequence
    """    

    # For the dataframes with the buying and selling stock transactions create two columns with the respective
    # cost and profit with regard to the close price
    buy_df['StocksCost_Close'] = buy_df['Stocks_Bought'] * buy_df['Close']
    sell_df['StocksProfit_Close'] = sell_df['Stocks_Sold'] * sell_df['Close']

    # For the 2 input dataframes, find the common columns
    CommCols_dfs = set(buy_df.columns).intersection(set(sell_df.columns)) - {'Date'}

    # Delete the common columns from the dataframes
    if n_seq <= 1000:
        buy_df = buy_df.drop(columns=list(CommCols_dfs)+['Low', 'Inv_Weight', 'Stocks_Bought'])
    else:
        buy_df = buy_df.drop(columns=list(CommCols_dfs)+['Low', 'Stocks_Bought'])

    sell_df = sell_df.drop(columns=list(CommCols_dfs)+['High', 'Stocks_Sold'])

    # Merge the buying and selling dataframes
    BuySell_df = pd.concat([buy_df, sell_df])
    BuySell_df.sort_values(by='Date', inplace=True)  # Sort the dataframe by date
    BuySell_df.fillna(0, inplace=True)  # Fill the NaN values with 0

    # Initialize a dataframe with the following columns: 
    # 1) Date of each transaction
    # 2) Balance of the capital for each transaction
    # 3) Portfolio i.e. the balance plus the price of the volume of stocks bought/sold
    valuation_df = pd.DataFrame(columns=['Date', 'Balance', 'Portfolio'])
    valuation_df['Date'] = pd.to_datetime(BuySell_df['Date'])

    # Calculate the Balance and Portfolio for the subsequent rows
    valuation_df['Balance'] = st_cap + BuySell_df['Stocks_Profit'].cumsum() - BuySell_df['Stocks_Cost'].cumsum()
    valuation_df['Portfolio'] = st_cap + BuySell_df['StocksProfit_Close'].cumsum() + BuySell_df['StocksCost_Close'].cumsum()
    
    valuation_df.reset_index(drop=True, inplace=True)

    # Plot the area chart
    plt.figure(figsize=(12, 6))
    plt.fill_between(valuation_df['Date'], valuation_df['Balance'], label='Balance', color='blue', alpha=0.8, zorder=2)
    plt.fill_between(valuation_df['Date'], valuation_df['Portfolio'], label='Portfolio', color='orange', alpha=0.8, zorder=1)

    # Customize x-axis (date scale)
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y'))
    plt.gcf().autofmt_xdate()

    # Set logarithmic scale for the y-axis
    plt.yscale('log')

    # Customize y-axis ticks
    plt.tick_params(axis='x', which='both', bottom=False, top=False)
    plt.tick_params(axis='y', which='both', left=False, right=False)
    if n_seq <=1000:
        plt.yticks([1e-2, 1e0, 1e2, 1e4, 1e6], labels=["$10^{-2}$", "$10^0$", "$10^2$", "$10^4$", "$10^6$"])
    else:
        plt.yticks([1e0, 1e3, 1e6, 1e9], labels=["$10^0$", "$10^3$", "$10^6$", "$10^9$"])

    # Customize the plot
    plt.legend()
    plt.title("Valuation")
    plt.xlabel("Date")
    plt.ylabel("Value")

    # Display the plot
    plt.show()