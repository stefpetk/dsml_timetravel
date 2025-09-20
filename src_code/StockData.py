import glob
import os
import pandas as pd

class StockData:
    """Class to read stock data from the specified path, analyze according to the total return and filter out the stocks
    so that only stocks with certain characteristics are kept. 
    """
    def __init__(self, stock_path, n_seq, date_ranges, return_threshold, min_years, n_splits=3):
        """
        Args:
                stock_path (str): Path to the stock data without the .txt extension
                n_seq (int): Length of the sequence of transactions which will be used to determine the total return threshold
                date_ranges (tuple): Tuple with the start and end date for which the performance of each stock will be analyzed in the YYYY-MM-DD format
                (if not specified stock performance will be evaluated for all the years it's present in the market)
                n_splits (int): Number of splits to be used for the evaluation of the stock performance and subsequent data filtering
                return_threshold (tuple): Threshold for the total return of the stock to be kept for each split
                min_years (tuple): Minimum number of years the stock has to be present in the market to be kept for each split
        """
        self.stock_path = stock_path
        self.n_seq = n_seq
        self.n_splits = n_splits
        self.date_ranges = date_ranges
        self.return_threshold = return_threshold
        self.min_years = min_years

    def read_analyze_stocks(self):
        """
        Read all stock data from the specified paths, compute the total return for the specified date ranges
        for each stock and store it in a dataframe.

        Returns:
            stock_performance (pd.DataFrame): Dataframe with the total return for each stock for the number of years specified
            stock_datalist (list): List of dataframes with the stock data for each stock
        """

        # List all files in the directory using their path
        files = glob.glob(os.path.join(self.stock_path, "*.txt"))

        # Filter out empty files
        files = [file for file in files if os.path.getsize(file) > 0]

        # Create a list with the initial individal stock data read as dataframes
        stock_datalist = [pd.read_csv(file) for file in files]

        # Create a list with the stock names, rename the 'OpenInt' column to 'Stock_Name'
        # and append to the column the stock id
        st_names = [file.split('\\')[-1].split('.')[0].upper() for file in files]
        stock_datalist = [stock_df.rename(columns={'OpenInt': 'Stock_Name'}) for stock_df in stock_datalist]
        for i, stock_df in enumerate(stock_datalist):
            stock_df['Stock_Name'] = st_names[i] 

        # Initialize a list to store stock performance
        performances_data = []
        
        if self.date_ranges != None:
            for i, date_range in enumerate(self.date_ranges):
                performances_data.append([])
                start_date, end_date = date_range

                for j, stock_df in enumerate(stock_datalist):
                    stock_name = st_names[j]

                    # Convert 'Date' column to datetime for filtering
                    stock_df['Date'] = pd.to_datetime(stock_df['Date'])

                    # Apply date range filter
                    filtered_df = stock_df
                    if start_date:
                        filtered_df = filtered_df[filtered_df['Date'] >= pd.to_datetime(start_date)]
                    if end_date:
                        filtered_df = filtered_df[filtered_df['Date'] <= pd.to_datetime(end_date)]

                    # Skip if there's insufficient data after filtering
                    if filtered_df.empty or len(filtered_df) < 2:
                        continue

                    # Calculate metrics
                    start_date_filt = filtered_df['Date'].iloc[0]
                    end_date_filt = filtered_df['Date'].iloc[-1]

                    start_low = filtered_df['Low'].iloc[0]
                    end_high = filtered_df['High'].iloc[-1]

                    # Total return: (End High - Start Low) / Start Low
                    total_return = (end_high - start_low) / start_low
                    total_years = (end_date_filt - start_date_filt).days / 365.25

                    # Append results
                    performances_data[i].append({
                        "Stock": stock_name,
                        "Total_Return": total_return,
                        "Total_Years": total_years,
                        "Start_Date": start_date_filt,
                        "End_Date": end_date_filt
                    })

            # Create dataframe from performance data for each date range
            stocks_performances = [pd.DataFrame(performance_data) for performance_data in performances_data]

            # Filter and sort performance data
            stocks_performances = [stock_performance[(stock_performance['Total_Return'] > 0) & (stock_performance['Total_Return'] != float('inf'))]
                                   for stock_performance in stocks_performances]
            stocks_performances = [stock_performance.sort_values(by='Total_Return', ascending=False)
                                   for stock_performance in stocks_performances]

            return stocks_performances, stock_datalist
        else:
            return stock_datalist

    def filter_stocks(self):
        """
        Filter out the list with the stocks dataframes based on the following criteria if the length of the sequence is below 1000:
        1) For the first period (e.g. 1962-1980) period the stock has a total return above 2 dollars and is at least 5 years in the stock market
        2) For the second period (e.g. 1980-2000) period the stock has a total return above 100 dollars and is at least 5 years in the stock market
        3) For the third period (e.g. 2000-2018) period the stock has a total return above 50 dollars and is at least 10 years in the stock market

        Returns:
            filt_stock_datalist (list): List of dataframes with the stock data for the filtered stocks if the sequence length is below 1000
        """
        
        # Read the stock data and analyze it
        stock_performances, stock_datalists = self.read_analyze_stocks()

        # Filter out the stocks based on the criteria and find the Id's of the stocks in question based on the length of the input sequence
        if self.n_seq <= 1000:
            filtered_stocks = [stock_performance[(stock_performance['Total_Years'] >= self.min_years[i]) & 
                                                 (stock_performance['Total_Return'] >= self.return_threshold[i])] 
                                                 for i, stock_performance in zip(range(self.n_splits), stock_performances)]
            
            # find the ID for the stocks that will be kept according to the specified criteria and
            # flatten the list of filtered stock ID's
            filt_stocks_ids = [filtered_stock['Stock'].values for filtered_stock in filtered_stocks]

            # Use the filtered stocks ID's to filter out the stock dataframes
            filt_stock_datalists = []
            for i, filt_stocks_id in enumerate(filt_stocks_ids):
                start_date, end_date = self.date_ranges[i]
                filtered_dfs = []
                for stock_df in stock_datalists:
                    if stock_df['Stock_Name'].iloc[0] in filt_stocks_id:
                        filtered_df = stock_df[(stock_df['Date'] >= pd.to_datetime(start_date)) & 
                                               (stock_df['Date'] <= pd.to_datetime(end_date))]
                        filtered_dfs.append(filtered_df)
                filt_stock_datalists.append(filtered_dfs)
            
            return filt_stock_datalists

    def concat_stock_dfs(self):
        """Concatenate all the stock dataframes into a single one with chronological order where only the stocks between the
           specified date ranges are kept.

            Returns:
                large_df (pd.DataFrame): Dataframe with the stock data for all the stocks"""

        if self.n_seq <= 1000:
            stock_datalists = self.filter_stocks()

            # retain only the stocks for the start and end dates
            for i in range(len(stock_datalists)):
                for j, stock_df in enumerate(stock_datalists[i]):
                    stock_df['Date'] = pd.to_datetime(stock_df['Date'])
                    stock_datalists[i][j] = stock_df.iloc[[0, -1]]

            large_dfs = [pd.concat(stock_datalist, ignore_index=True) 
                         for stock_datalist in stock_datalists]
            
            for large_df in large_dfs:
                large_df['Date'] = pd.to_datetime(large_df['Date'])
                large_df = large_df.sort_values(by='Date')

            return large_dfs

        else:
            stock_datalists = self.read_analyze_stocks()
            large_df = pd.concat(stock_datalists, ignore_index=True)
            large_df['Date'] = pd.to_datetime(large_df['Date'])
            large_df = large_df.sort_values(by='Date')

            return large_df



