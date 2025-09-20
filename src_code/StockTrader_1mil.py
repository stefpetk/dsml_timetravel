import pandas as pd
import numpy as np

def StockTrader_1mil(data, initial_capital=1, max_volume_percentage=0.1, n_seq=1_000_000):
    """
    Function that generates a large stock trading sequence utilizing the intra-day trading
    technique
    
    Args:
        data (pd.DataFrame): Stock data with the following columns: 
                             ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Stock_Name'].
        initial_capital (float): Initial starting capital (default=1).
        max_volume_percentage (float): max percentage of the volume that can bought/sold
        for a given stock and date set at 10%.
        n_seq (int): Max number of transactions.
    
    Returns:
        A dataframe with all the transactions.
        pd.DataFrame: A dataframe with the stocks purchases.
        pd.DataFrame: A Dataframe with stocks sells.
        capital: Final available capital.
    """
    
    # Sort dataframe values by date
    data['Date'] = pd.to_datetime(data['Date'])
    data = data.sort_values(by=['Date', 'Stock_Name']).reset_index(drop=True)
    
    # Initialize capital, transactions and the buying/selling sequence
    capital = initial_capital
    transactions = []
    buy_logs = []
    sell_logs = []
    
    # Loop for each day and stock
    for _, row in data.iterrows():
        if len(transactions) >= n_seq:
            break  # break the loop if the length of the sequence exceeds the number specified

        # Calculation of lowest buying price and highest selling price per day
        buy_price = min(row['Open'], row['Low'])
        sell_price = max(row['High'], row['Close'])

        # Calculation of max number of stocks that can be bought per day
        max_stocks_by_volume = np.floor(max_volume_percentage * row['Volume'])
        max_stocks_by_capital = np.floor(capital / buy_price)
        stocks_to_trade = int(min(max_stocks_by_volume, max_stocks_by_capital))
        
        # Omit if stocks haven't been bought yet
        if stocks_to_trade < 1:
            # Log the transactions
            buy_logs.append({
                'Date': row['Date'], 'Open': row['Open'], 'Low': row['Low'], 'Close': row['Close'],
                'Volume': row['Volume'], 'Stock_Name': row['Stock_Name'], 
                'Stocks_Bought': 0, 'Stocks_Cost': 0.0
            })
            sell_logs.append({
                'Stock_Name': row['Stock_Name'], 'Date': row['Date'], 'Open': row['Open'], 
                'High': row['High'], 'Close': row['Close'], 'Volume': row['Volume'], 
                'Stocks_Sold': 0, 'Stocks_Profit': 0.0
            })
            continue
        
        # Update the capital with the cost and register the purchases
        cost = stocks_to_trade * buy_price
        capital -= cost
        transactions.append(f"{row['Date'].date()} buy-low {row['Stock_Name']} {stocks_to_trade}")
        buy_logs.append({
            'Date': row['Date'], 'Open': row['Open'], 'Low': row['Low'], 'Close': row['Close'],
            'Volume': row['Volume'], 'Stock_Name': row['Stock_Name'], 
            'Stocks_Bought': stocks_to_trade, 'Stocks_Cost': cost
        })

        # Update the capital with the profit and register the sellings
        profit = stocks_to_trade * sell_price
        capital += profit
        transactions.append(f"{row['Date'].date()} sell-high {row['Stock_Name']} {stocks_to_trade}")
        sell_logs.append({
            'Stock_Name': row['Stock_Name'], 'Date': row['Date'], 'Open': row['Open'], 
            'High': row['High'], 'Close': row['Close'], 'Volume': row['Volume'], 
            'Stocks_Sold': stocks_to_trade, 'Stocks_Profit': profit
        })
    
    # Create the dataframes for the purchases and sellings
    buy_df = pd.DataFrame(buy_logs)
    sell_df = pd.DataFrame(sell_logs)
    
    return pd.DataFrame({'Transaction': transactions}), buy_df, sell_df, capital