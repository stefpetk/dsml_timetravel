from StockData import StockData
import pandas as pd
from StockTrader_1k import stocks_weight, Stock_Trader_1000
from Valuation import valuation
import sys

# StockData class arguments
stock_data_path = "/mnt/c/Users/working_dir/Stocks_Init" # the 'Stocks_Init' dir contains the stocks prices+volume from the kaggle dataset
n_seq_small = 1000

# These parameters can be minimally tweaked (e.g. change the minimum years by 1-2)
date_ranges = ('1962-01-01', '1980-01-01'), ('1980-01-01', '2000-01-01'), ('2000-01-01', '2018-01-01')
min_years = (5, 10, 5)
min_total_return = (2, 100, 50)

# For the date ranges 1962-1980, 1980-2000 and 2000-2018 create sorted tables with the the total return of the stocks
StockData_Inst = StockData(stock_data_path, n_seq_small, date_ranges, min_total_return, min_years)
StocksPerfs, StockDataList = StockData_Inst.read_analyze_stocks()

# Create the final filtered stocks dataframe to be used for the stock trading sequence with a length <= 1000
filt_stock_datalists = StockData_Inst.concat_stock_dfs()

# Create a list with the filtered stocks dataframes for the date ranges specified and sort them by date
filtered_stocks = [filtered_stock for filtered_stock in filt_stock_datalists]
filtered_stocks = [filtered_stock.sort_values(by=["Date"]) for filtered_stock in filtered_stocks]

# Create a list with the stock performances dataframes for the date ranges specified, sort them by total return,
# filter the stocks that are not in the filtered stocks dataframes and calculate the stocks weights
stocks_perf = [StockPerf for StockPerf in StocksPerfs]
stocks_perf = [stock_perf.sort_values(by=["Total_Return"], ascending=False) for stock_perf in stocks_perf]
stocks_perf = [stock_perf[stock_perf["Stock"].isin(filtered_stock['Stock_Name'].values)] for stock_perf, filtered_stock in
               zip(stocks_perf, filtered_stocks)]
stocks_perf = [stocks_weight(stock_perf) for stock_perf in stocks_perf]

# Create the stock trading sequence for the 1962-1980 time period
Stock_Trader_1980 = Stock_Trader_1000(filtered_stocks[0], stocks_perf[0])

# Create the stock trading sequence for the 1980-2000 time period
Stock_Trader_2000 = Stock_Trader_1000(filtered_stocks[1], stocks_perf[1],
                                      st_cap=Stock_Trader_1980[1])

# Create the stock trading sequence for the 2000-2010 time period
Stock_Trader_2018 = Stock_Trader_1000(filtered_stocks[2], stocks_perf[2],
                                      st_cap=Stock_Trader_2000[1])

# Concatenate the stock trading sequences and write them to a file
small_txt = pd.concat([Stock_Trader_1980[0], Stock_Trader_2000[0],
                       Stock_Trader_2018[0]])

# Define the dataframes with buying and selling transactions
BuySell_dfs = [Stock_Trader_1980[2], Stock_Trader_2000[2], Stock_Trader_2018[2]]

# split the into 2 the buying and selling dataframe
buy_df = pd.concat([BuySell_df[0] for BuySell_df in BuySell_dfs])
sell_df = pd.concat([BuySell_df[1] for BuySell_df in BuySell_dfs])

# plot the valuation plot
valuation(buy_df, sell_df)

# write the final transcations sequence .txt file to the specified path
with open('/mnt/c/Users/user/working_dir/small.txt', 'w', newline='') as file:
  file.write(f"{len(small_txt)}\n")
  small_txt.to_csv(
        file,
        sep=' ',
        index=False,
        header=False
    )

