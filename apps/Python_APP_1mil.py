from StockData import StockData
import pandas as pd
import csv
from Valuation import valuation
from StockTrader_1mil import StockTrader_1mil

# StockData class arguments
stock_data_path = "/mnt/c/Users/stef-/Desktop/Python_Assignment/Stocks_Init"
n_seq_large = 1000000

# Create the StockData class instance for 
StockData_Inst = StockData(stock_data_path, n_seq_large, date_ranges=None, return_threshold=None, min_years=None)

# Create the large stocks dataframe to be used for the stock trading sequence with a length <= 1000000
large_stock_df = StockData_Inst.concat_stock_dfs()

# Create the large transactions sequence
transactions, buy_df, sell_df, final_capital = StockTrader_1mil(large_stock_df)

# plot the valuation plot
valuation(buy_df, sell_df, n_seq=1000000)

# Store the results in a .txt file
with open('/mnt/c/Users/stef-/Desktop/Python_Assignment/large_test.txt', 'w') as file:
    file.write(f"{len(transactions)}\n")
    for _, row in transactions.iterrows():
        file.write(' '.join(str(value).strip() for value in row.values) + '\n')
print(f"Τελικό κεφάλαιο: {final_capital}")
