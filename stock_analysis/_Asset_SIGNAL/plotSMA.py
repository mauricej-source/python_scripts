import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
from datetime import datetime, timedelta

# Keep clean_csv_header if you ever plan to use it for *other* CSV sources,
# but it's not needed for yfinance output.
def clean_csv_header(input_filepath, ticker, output_filepath=None):
    """
    Reads a CSV file, replaces 'Price' with 'Date' in the first line,
    and removes specific second and third lines if they match the specified format.
    (This function is generally not needed for yfinance output, which is already clean.)

    Args:
        input_filepath (str): The path to the input CSV file.
        output_filepath (str, optional): The path to save the cleaned CSV file.
                                         If None, the input file will be overwritten.
                                         Defaults to None.
    """
    if output_filepath is None:
        output_filepath = input_filepath

    lines = []
    try:
        with open(input_filepath, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: The file '{input_filepath}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return

    modified_lines = []
    
    # Process the first line
    if lines:
        first_line = lines[0].strip()
        # This modification is specific to a CSV format that YF.download does NOT produce
        if first_line.startswith('Price,'):
            modified_lines.append('date' + first_line[5:] + '\n') # Changed to lowercase 'date' here for consistency
            print(f"Modified first line: '{first_line.strip()}' -> 'date{first_line[5:].strip()}'")
        else:
            modified_lines.append(lines[0])
            print(f"First line not modified: '{first_line.strip()}'")
    else:
        print("The CSV file is empty.")
        return

    # Process subsequent lines for removal
    lines_to_skip = 0
    if len(lines) > 1:
        second_line = lines[1].strip()
        if second_line.startswith('Ticker,') and all(part == ticker for part in second_line.split(',')[1:]):
            lines_to_skip += 1
            print(f"Skipping second line: '{second_line}'")
        else:
            modified_lines.append(lines[1])
            print(f"Second line not skipped: '{second_line}'")

    if len(lines) > 2 and lines_to_skip == 1: # Only check third line if second was skipped
        third_line = lines[2].strip()
        if third_line == 'Date,,,,,': # This is specific to a non-yfinance CSV format
            lines_to_skip += 1
            print(f"Skipping third line: '{third_line}'")
        else:
            if lines_to_skip == 1:
                modified_lines.append(lines[2])
                print(f"Third line not skipped: '{third_line}'")

    # Add remaining lines
    modified_lines.extend(lines[lines_to_skip + 1:])

    try:
        with open(output_filepath, 'w') as f:
            f.writelines(modified_lines)
        print(f"CSV file cleaned successfully. Output saved to '{output_filepath}'")
    except Exception as e:
        print(f"An error occurred while writing the file: {e}")
    
def download_historical_data(ticker, start_date, end_date, output_filename):
    """
    Downloads historical stock data using yfinance and saves it to a CSV file.
    Includes robust handling for MultiIndex columns and ensures consistent column naming.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL').
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        output_filename (str): Name of the CSV file to save the data.

    Returns:
        str: The path to the saved CSV file if successful, None otherwise.
    """
    print(f"Attempting to download historical data for {ticker} from {start_date} to {end_date}...")
    try:
        # Get today's date in YYYYMMDD format
        today_date_str = datetime.now().strftime('%Y%m%d')
        
        # Define the output directory
        output_dir = 'E:/_scripts_PYTHON/_personal/_OUTPUT'
        
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Construct the new, full file path
        new_output_filename = os.path.join(output_dir, f"{today_date_str}_{output_filename}")

        # Download data
        data = yf.download(ticker, start=start_date, end=end_date)

        if data.empty:
            print(f"No data downloaded for {ticker} in the specified date range. Please check the ticker and dates.")
            return None

        # --- CRUCIAL FIX: Handle MultiIndex columns from yfinance output ---
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
            
        # Ensure all columns are lowercase and spaces replaced with underscores for consistency
        data.columns = [col.replace(' ', '_').replace('.', '').lower() for col in data.columns]
        
        if 'adj_close' in data.columns and 'close' in data.columns:
            data = data.drop(columns=['adj_close'])
        elif 'adj_close' in data.columns and 'close' not in data.columns:
            data = data.rename(columns={'adj_close': 'close'})

        required_columns_lower = ['open', 'high', 'low', 'close', 'volume']
        
        if not all(col in data.columns for col in required_columns_lower):
            missing_cols = [col for col in required_columns_lower if col not in data.columns]
            print(f"Error: Downloaded data for {ticker} is missing required columns after processing: {', '.join(missing_cols)}")
            print("Please ensure the ticker symbol is correct and has complete historical data.")
            return None

        # Save to CSV:
        data.index.name = 'date' # Set index name to 'date' (lowercase)
        data.to_csv(new_output_filename, index=True, header=True)
        print(f"Historical data for {ticker} saved to {new_output_filename}")
        
        # REMOVED: No need to call clean_csv_header for yfinance output
        # print(f"Clean Historical Data CSV Header for {ticker}")
        # clean_csv_header(output_filename, ticker)
        
        return new_output_filename

    except Exception as e:
        print(f"An error occurred during data download for {ticker}: {e}")
        return None
        
# --- 1. Data Acquisition (Using CSV as discussed) ---
def load_data_from_csv(file_path):
    """Loads historical stock data from a CSV file."""
    try:
        # Changed 'Date' to 'date' here to match the saved CSV header
        df = pd.read_csv(file_path, parse_dates=['date'], index_col='date')
        
        print(f"  >>: CSV file '{file_path}' FOUND")
        
        # Column standardization to ensure 'Close' and 'Volume' are available
        # YF.download already returns 'Close' and 'Volume' (or 'Adj Close')
        # in a consistent manner, especially after the `download_historical_data` processing.
        # This part might still be useful if you're loading CSVs from other sources.
        df.columns = [col.lower() for col in df.columns] # Ensure all columns are lowercase
        
        if 'adj close' in df.columns: # After lowercase, it becomes 'adj close'
            df = df.rename(columns={'adj close': 'close'})
        
        if 'volume' not in df.columns:
            # Check for common alternative volume names if you're not solely relying on yfinance
            if 'vol.' in df.columns:
                df = df.rename(columns={'vol.': 'volume'})
            else:
                raise ValueError("Volume column not found. Please check your CSV.")

        # Ensure numerical types and sort by date
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce', downcast='integer')
        df.dropna(subset=['close', 'volume'], inplace=True)
        df = df.sort_index(ascending=True)
        return df[['close', 'volume']] # Return lowercase column names
    except FileNotFoundError:
        print(f"Error: CSV file '{file_path}' not found.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading or processing CSV: {e}")
        return pd.DataFrame()

# --- Rest of your script (no changes needed here) ---

# --- 2. Technical Indicator Calculation ---
def add_moving_averages(df, fast_period, slow_period):
    """Adds Simple Moving Averages (SMA) to the DataFrame using pandas.rolling()."""
    df['SMA_Fast'] = df['close'].rolling(window=fast_period).mean()
    df['SMA_Slow'] = df['close'].rolling(window=slow_period).mean()
    return df

# --- 3. Strategy Logic & 4. Signal Generation ---
def generate_crossover_signals(df):
    """Generates buy/sell signals based on NEW strategy rules."""
    # Buy Signal: Price crosses SMA_45 (SMA_Slow) to the upside
    df['Buy_Signal'] = (df['close'] > df['SMA_Slow']) & \
                       (df['close'].shift(1) <= df['SMA_Slow'].shift(1))

    # Sell Signal: Price crosses SMA_15 (SMA_Fast) to the downside
    df['Sell_Signal'] = (df['close'] < df['SMA_Fast']) & \
                        (df['close'].shift(1) >= df['SMA_Fast'].shift(1))
    return df

# --- 5. Simple Backtesting (Manual/Vectorized) ---
def backtest_strategy(df, initial_capital=10000, commission_rate=0.001):
    """
    Simulates trades based on buy/sell signals and calculates portfolio performance.
    """
    df['Position'] = 0
    df['Holdings'] = 0.0
    #df['Cash'] = initial_capital
    #df['Total_Portfolio_Value'] = initial_capital
    df['Cash'] = float(initial_capital) # Explicitly cast to float
    df['Total_Portfolio_Value'] = float(initial_capital) # Explicitly cast to float
    
    for i in range(1, len(df)):
        df.loc[df.index[i], 'Cash'] = df['Cash'].iloc[i-1]
        df.loc[df.index[i], 'Holdings'] = df['Holdings'].iloc[i-1]
        df.loc[df.index[i], 'Position'] = df['Position'].iloc[i-1]

        # Ensure 'Close' is accessed correctly based on the 'load_data_from_csv' output (which is 'close')
        if df['Buy_Signal'].iloc[i] and df['Position'].iloc[i-1] == 0:
            buy_price = df['close'].iloc[i]
            if (df['Cash'].iloc[i] / (buy_price * (1 + commission_rate))) >= 1:
                shares_to_buy = (df['Cash'].iloc[i] * (1 - commission_rate)) // buy_price
                df.loc[df.index[i], 'Holdings'] = shares_to_buy
                df.loc[df.index[i], 'Cash'] -= shares_to_buy * buy_price * (1 + commission_rate)
                df.loc[df.index[i], 'Position'] = 1

        elif df['Sell_Signal'].iloc[i] and df['Position'].iloc[i-1] == 1:
            sell_price = df['close'].iloc[i]
            shares_to_sell = df['Holdings'].iloc[i]
            if shares_to_sell > 0:
                df.loc[df.index[i], 'Cash'] += shares_to_sell * sell_price * (1 - commission_rate)
                df.loc[df.index[i], 'Holdings'] = 0
                df.loc[df.index[i], 'Position'] = 0

        df.loc[df.index[i], 'Total_Portfolio_Value'] = df['Cash'].iloc[i] + (df['Holdings'].iloc[i] * df['close'].iloc[i])

    return df

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Analyze Stock with Technical Indicators ---")

    ticker_symbol = input("Enter the stock ticker symbol (e.g., JNJ, AAPL): ").upper()
    
    # --- MODIFIED DATE INPUT AND DEFAULTING LOGIC STARTS HERE ---
    start_date_input = input("Enter the start date (YYYY-MM-DD, press Enter for beginning of current year): ")
    end_date_input = input("Enter the end date (YYYY-MM-DD, press Enter for current date): ")

    # Determine start_date based on input or default
    if start_date_input:
        start_date_str = start_date_input
    else:
        # Default to the beginning of the current year
        current_year = datetime.now().year
        start_date_str = f"{current_year}-01-01"
        print(f"Start date defaulted to: {start_date_str}")

    # Determine end_date based on input or default
    if end_date_input:
        end_date_str = end_date_input
    else:
        # Default to the current date
        end_date_str = datetime.now().strftime('%Y-%m-%d')
        print(f"End date defaulted to: {end_date_str}")
    # --- MODIFIED DATE INPUT AND DEFAULTING LOGIC ENDS HERE ---

    try:
        # Convert string dates to datetime.date objects for easier comparison
        parsed_start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        parsed_end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        today_date = datetime.now().date()
        
        if parsed_start_date > today_date:
            print(f"Error: Start date ({start_date_str}) cannot be in the future.")
            exit()
            
        if parsed_start_date >= parsed_end_date:
            print(f"Error: Start date ({start_date_str}) must be strictly before end date ({end_date_str}).")
            exit()

        if parsed_end_date >= today_date:
            effective_download_end_date = today_date + timedelta(days=1)
            print(f"Warning: End date ({end_date_str}) is today or in the future. Data will be downloaded up to today's available data ({today_date.strftime('%Y-%m-%d')}).")
        else:
            effective_download_end_date = parsed_end_date + timedelta(days=1)

        download_start_date_str = parsed_start_date.strftime('%Y-%m-%d')
        download_end_date_str = effective_download_end_date.strftime('%Y-%m-%d')

    except ValueError:
        print("Error: Invalid date format. Please use YYYY-MM-DD.")
        exit()

    csv_file = f"{ticker_symbol}_historical_data.csv"

    downloaded_csv_path = download_historical_data(ticker_symbol, download_start_date_str, download_end_date_str, csv_file)

    #886.19 / Analysis
    #fast_ma_period = 15
    #slow_ma_period = 45
    
    #1,182 / Analysis
    #fast_ma_period = 22
    #slow_ma_period = 7
    
    #1,317 / Analysis
    #fast_ma_period = 20
    #slow_ma_period = 7
    
    #1,321 / Analysis
    fast_ma_period = 21
    slow_ma_period = 7
    
    #1,131 / Analysis
    #fast_ma_period = 21
    #slow_ma_period = 4
    
    # 1. Load Data
    if downloaded_csv_path: # Only proceed if data was successfully downloaded
        data = load_data_from_csv(downloaded_csv_path)

        if not data.empty:
            # 2. Add Technical Indicators
            data = add_moving_averages(data, fast_ma_period, slow_ma_period)

            data.dropna(subset=['SMA_Fast', 'SMA_Slow'], inplace=True)

            if data.empty:
                print("Not enough data after calculating moving averages. Try a larger CSV file.")
            else:
                # 3 & 4. Generate Buy/Sell Signals
                data = generate_crossover_signals(data)

                # --- Filter for the Last Year ---
                # Use datetime.now() for 'today' to make it dynamic
                today_for_filter = datetime.now() # Use actual current date for consistent last year calculation
                one_year_ago = today_for_filter - timedelta(days=365)

                data_oneyear = data.loc[one_year_ago.strftime('%Y-%m-%d'):today_for_filter.strftime('%Y-%m-%d')].copy()

                if data_oneyear.empty:
                    print(f"No data available for {ticker_symbol} in the last year ({one_year_ago.strftime('%Y-%m-%d')} to {today_for_filter.strftime('%Y-%m-%d')}).")
                else:
                    # 5. Backtest Strategy on the filtered one-year data
                    backtested_data_oneyear = backtest_strategy(data_oneyear.copy(), initial_capital=10000)

                    print("\n--- Backtesting Results (Last Year Only) ---")
                    initial_value_oneyear = 10000
                    final_value_oneyear = backtested_data_oneyear['Total_Portfolio_Value'].iloc[-1]
                    net_profit_oneyear = final_value_oneyear - initial_value_oneyear
                    roi_oneyear = (net_profit_oneyear / initial_value_oneyear) * 100 if initial_value_oneyear > 0 else 0

                    print(f"Initial Capital (for last year backtest): ${initial_value_oneyear:,.2f}")
                    print(f"Final Portfolio Value (last year): ${final_value_oneyear:,.2f}")
                    print(f"Net Profit (last year): ${net_profit_oneyear:,.2f}")
                    print(f"Return on Investment (ROI) (last year): {roi_oneyear:.2f}%")


                    # 6. Visualization for the Last Year
                    plt.figure(figsize=(14, 8))
                    #plt.plot(data_oneyear.index, data_oneyear['close'], label='Close Price', alpha=0.7)
                    #plt.plot(data_oneyear.index, data_oneyear['SMA_Fast'], label=f'SMA {fast_ma_period}', color='orange')
                    #plt.plot(data_oneyear.index, data_oneyear['SMA_Slow'], label=f'SMA {slow_ma_period}', color='purple')
                    plt.plot(data_oneyear.index, data_oneyear['close'], label='Close Price', alpha=0.7)
                    plt.plot(data_oneyear.index, data_oneyear['SMA_Fast'], label=f'SMA {fast_ma_period} (Sell Trigger)', color='orange') # Now SMA_15
                    plt.plot(data_oneyear.index, data_oneyear['SMA_Slow'], label=f'SMA {slow_ma_period} (Buy Trigger)', color='purple') # Now SMA_45
                
                    # Define an offset value
                    # This value might need to be adjusted based on the scale of your stock prices
                    # A good starting point is a small percentage of the average price, or a fixed small number
                    price_range = data_oneyear['close'].max() - data_oneyear['close'].min()
                    offset = price_range * 0.015 # 1.5% of the visible price range, adjust as needed

                    # Plot Buy Signals
                    buy_signals_oneyear = data_oneyear[data_oneyear['Buy_Signal']]
                    plt.scatter(buy_signals_oneyear.index, buy_signals_oneyear['close'] * 0.99, # Move marker down by 1%
                                marker='^', color='green', s=100, label='Buy Signal', alpha=1, zorder=5)
                    # OR using a fixed offset:
                    # plt.scatter(buy_signals_oneyear.index, buy_signals_oneyear['close'] - offset, 
                    #             marker='^', color='green', s=100, label='Buy Signal', alpha=1, zorder=5)


                    # Plot Sell Signals
                    sell_signals_oneyear = data_oneyear[data_oneyear['Sell_Signal']]
                    plt.scatter(sell_signals_oneyear.index, sell_signals_oneyear['close'] * 1.01, # Move marker up by 1%
                                marker='v', color='red', s=100, label='Sell Signal', alpha=1, zorder=5)
                    # OR using a fixed offset:
                    # plt.scatter(sell_signals_oneyear.index, sell_signals_oneyear['close'] + offset, 
                    #             marker='v', color='red', s=100, label='Sell Signal', alpha=1, zorder=5)

                    #plt.title(f'{ticker_symbol} SMA Crossover Strategy ({fast_ma_period} vs {slow_ma_period}) - Last Year ({one_year_ago.strftime("%Y-%m-%d")} to {today_for_filter.strftime("%Y-%m-%d")})')
                    plt.title(f'{ticker_symbol} Price vs SMAs ({fast_ma_period} & {slow_ma_period}) with Signals - Last Year')
                    plt.xlabel('Date')
                    plt.ylabel('Price')
                    plt.legend()
                    plt.grid(True)
                    plt.show()
        else:
            print(f"Failed to load data from {downloaded_csv_path}. Analysis aborted.")
