## **Time Travel to the Stock Market!**

Proposed solution for the 'Time travel' python project (project description link in Greek: https://courses.softlab.ntua.gr/progds/2021b/python-project.pdf) which is requested as a semester assignment for the 'Programming Techniques for Data Science' course in the 'Data Science and Machine Learning' MSc in ECE NTUA.
<br>
The aim of this assignment is to start with an account with a balance of $1 on 1/1/1960 and, knowing the purchase and sale prices and the volume of each share for the period 1960-2018 (the relevant files can be found in the https://www.kaggle.com/datasets/borismarjanovic/price-volume-data-for-all-us-stocks-etfs kaggle dataset), to create a small sequence (<=1,000) and a large sequence (<=1,000,000) of buy and sell transactions that will yield a large profit (the profit check for the small sequence can be done via the link https://courses.softlab.ntua.gr/progds/2021b/time-travel/ whenever it becomes available).
<br><br>
With regard to the tactic of creating a small sequence of buy and sell transactions, based on the total return of shares for distinct periods, certain movements are detected which, in sequence, can offer a large profit if sold in subsequent periods (for more information, refer to the written report). On the other hand, to create the large sequence of buy and sell transactions, the tactic of buying and selling on the same day is followed for all shares of the same provider that offer the highest relative return.
<br>
Unfortunately, for the time being the application for producing the small transaction sequences has not been sufficiently optimized to provide solutions that deviate significantly from the following parameters 
<br><br>
```python
date_ranges = ('1962-01-01', '1980-01-01'), ('1980-01-01', '2000-01-01'), ('2000-01-01', '2018-01-01') # date ranges for stocks analyzing
min_years = (5, 10, 5) # minimum years that the stocks analyzed for each date range are present on the market
min_total_return = (2, 100, 50) # minimum total return for the stocks analyzed for each date range
```
<br><br>
Below the project structure with all revelant folders and files is provided as well as a guide for running the script applications to produce the requested sequences.
<br>
## 📂 Project Structure
```plaintext
dsml_timetravel/
│
├── int_tab/              # Interim tables for analyzing the stocks in order to choose the appropriate parameters (date ranges, return etc.)
│   ├── stock_perf_tab/   # Stocks performances tables for each target date
│   ├── filt_stock/       # Stocks filtered according to the parameters of minimum presence in the stock market and total return
│   └── buy_sell_df/      # Pandas dataframes which indicate the buying and selling transactions for each 
│
├── src_code/             # Python scripts containing the relevant classes and methods for running the applications that produce the requested transactions sequences
├── apps/                 # Application for producing the small and large transaction sequences.
├── docs/                 # Written report (at Greek) and indicative results of the applications.
```

## How to run (conda environment on windows)
```bash
# Activate your conda environment
conda activate my_env

# Change to the dir containing the downloaded project
cd C:/Users/user/working_dir

# Run the application for producing the small sequence (<=1000 transactions)
python Python_APP_1k.py

# Run the application for producing the large sequence (<=1000000 transactions)
python Python_APP_1mil.py
```

## How to run (wsl environment)
```bash
# Change to the dir containing the copied/downloaded project
cd /mnt/c/Users/user/working_dir

# Run the application for producing the small sequence (<=1000 transactions)
python3 Python_APP_1k.py

# Run the application for producing the large sequence (<=1000000 transactions)
python3 Python_APP_1mil.py
```
