import pandas as pd
from datetime import timedelta
import numpy as np

def stocks_weight(StockPerf_df):
  """
  Function that assigns a weight for buying and selling stocks with a high profit based on the total return of the stock.

  Args:
    StockPerf_df: a dataframe with the stocks performance

  Returns:
    ModStockPerf_df: a dataframe with the stocks performance and the assigned
    investment weights
  """
  # Calculate the sum of the total return
  return_sum = StockPerf_df['Total_Return'].sum()

  # Calculate the investment weight (ratio of total return to the sum of total return minus 2%)
  StockPerf_df['Inv_Weight'] = StockPerf_df['Total_Return'] / return_sum - 0.02

  # Ensure that Inc_Weight > 0 for all circumstances
  StockPerf_df['Inv_Weight'] = StockPerf_df['Inv_Weight'].clip(lower=0)

  return StockPerf_df


def Stock_Trader_1000(transactions, performances, st_cap=1, trans_fee=0.01):
  """
  Function that generates a stock trading sequence for a given period and computes the capital at the end of the time period.

  Args:
    transactions: a dataframe with the filtered stock transactions
    performances: a dataframe with the stock performances
    st_cap: the initial budget for the stock trading sequence at 1/1/1960 equal to 1 dollar
  Returns:
    transaction_df: a dataframe with the stock transactions
    remaining_capital: the capital at the end of the time period
  """
  transactions.reset_index(drop=True, inplace=True)  # Reset the index of the transactions dataframe
  transactions['Date'] = pd.to_datetime(transactions['Date'])  # Convert 'Date' column to datetime objects
  date_diffs = transactions['Date'].diff()  # Calculate differences between consecutive dates

  # Find the index where the consecutive date difference is greater than 6 years
  split_index = date_diffs[date_diffs > timedelta(days=365 * 6)].index

  # Split the dataframe at the identified index
  split_dataframes = [transactions.iloc[:np.int64(split_index[0])],
                      transactions.iloc[np.int64(split_index[0]):]]

  # Set one dataframe for buying and one for selling stocks
  buy_df = split_dataframes[0].reset_index(drop=True)
  sell_df = split_dataframes[1].reset_index(drop=True)

  # Merge the performances dataframe with the buying dataframe and then align with the selling dataframe
  buy_df = pd.merge(buy_df, performances[['Stock', 'Inv_Weight']],
                    left_on='Stock_Name', right_on='Stock', how='left')
  sell_df = sell_df.set_index('Stock_Name').reindex(buy_df['Stock_Name']).reset_index()

  # Drop unnecessary columns
  buy_df.drop(columns=['Stock', 'High'], inplace=True)
  sell_df.drop(columns=['Low'], inplace=True)

  # Initialize the columns for buying and selling stocks dataframes
  buy_df['Stocks_Bought'] = 0
  buy_df['Stocks_Cost'] = 0

  sell_df['Stocks_Sold'] = 0
  sell_df['Stocks_Profit'] = 0

  # Starting capital
  remaining_capital = st_cap

  # Minimum capital (10% of the starting capital) to be maintained in the account
  min_capital = st_cap * 0.1

  # Initialize a dataframe to record transactions
  transaction_log = []

  # Buy stocks while the remaining capital is greater or equal to the minimum capital
  while remaining_capital >= min_capital:
    for index, row in buy_df.iterrows():

      # Calculate the market price based on the buying condition at the 
      # lowest available price for a given date
      if row['Close'] <= row['Low'] and row['Close'] <= row['Open']:
          stock_price = row['Close'] + trans_fee * row['Close']
          price_type = 'close'
      elif row['Low'] <= row['Close'] and row['Low'] <= row['Open']:
          stock_price = row['Low'] + trans_fee * row['Low']
          price_type = 'low'
      elif row['Open'] <= row['Close'] and row['Open'] <= row['Low']:
          stock_price = row['Open'] + trans_fee * row['Open']
          price_type = 'open'
      else:
          continue
      
      # Calculate the maximum number of stocks that can be bought based 
      # on 10% of the total volume
      max_allowed_stocks = np.floor(0.1 * row['Volume'])

      # Calculate the maximum number of stocks based on the investable capital
      investable_capital = row['Inv_Weight'] * remaining_capital
      max_stocks = np.floor(investable_capital / stock_price)

      # Calculate the cost of buying the maximum number of stocks
      cost = max_stocks * stock_price

      # If the cost is zero or the maximum number of stocks exceeds the allowed number, 
      # continue to the next row
      if cost == 0:
          continue
      elif max_stocks > max_allowed_stocks:
          continue

      # Update the buying dataframe columns
      buy_df.at[index, 'Stocks_Bought'] += max_stocks
      buy_df.at[index, 'Stocks_Cost'] += cost

      # Reduce the remaining capital
      remaining_capital -= cost

      # Log the transaction
      transaction_log.append({
          "Date": row['Date'],
          "Transaction": f"buy-{price_type}",
          "Stock": row['Stock_Name'],
          "Volume": max_stocks
      })

      # Break the loop if the remaining capital is less than the minimum capital
      if remaining_capital < min_capital:
          break

  # Loop for selling the stock
  for (ib, rowb), (ise, rowse) in zip(buy_df.iterrows(), sell_df.iterrows()):

    # Calculate the market price based on the selling condition at the highest possible price 
    # for a given date
    if rowse['Close'] >= rowse['High'] and rowse['Close'] >= rowse['Open']:
        stock_price = rowse['Close'] - trans_fee * rowse['Close']
        price_type = 'close'
    elif rowse['High'] >= rowse['Close'] and rowse['High'] >= rowse['Open']:
        stock_price = rowse['High'] - trans_fee * rowse['High']
        price_type = 'high'
    elif rowse['Open'] >= rowse['Close'] and rowse['Open'] >= rowse['High']:
        stock_price = rowse['Open'] - trans_fee * rowse['Open']
        price_type = 'open'
    else:
        continue

    # Update the selling dataframe columns (sell all the stocks we bought)
    sell_df.at[ise, 'Stocks_Sold'] = buy_df.at[ib, 'Stocks_Bought']
    sell_df.at[ise, 'Stocks_Profit'] = sell_df.at[ise, 'Stocks_Sold'] * stock_price

    # Log the transaction
    transaction_log.append({
        "Date": rowse['Date'],
        "Transaction": f"sell-{price_type}",
        "Stock": rowb['Stock_Name'],
        "Volume": buy_df.at[ib, 'Stocks_Bought']
    })

  # Increase the available capital based on the profit from selling the stocks
  remaining_capital = remaining_capital + sell_df['Stocks_Profit'].sum()

  # Create a dataframe for the transactions
  transaction_df = pd.DataFrame(transaction_log)
  transaction_df['Date'] = pd.to_datetime(transaction_df['Date'])
  transaction_df = transaction_df.sort_values(by='Date')

  # Final grouping for merging transactions of the same day/stock
  transaction_df = (
    transaction_df.groupby(['Date', 'Transaction', 'Stock'], as_index=False)
    .agg({'Volume': 'sum'}))

  # Filter out transactions with zero volume
  transaction_df = transaction_df[transaction_df['Volume'] > 0]

  if remaining_capital > st_cap and len(transaction_df) < 1000:
    return transaction_df, remaining_capital, [buy_df, sell_df]
  else:
    raise Exception("The investment for the given period was not profitable") # Raise an exception if the investment was not profitable