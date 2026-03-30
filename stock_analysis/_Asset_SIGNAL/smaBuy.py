import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

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
        
        # print(f"  >>: CSV file '{file_path}' FOUND")
        
        # Column standardization to ensure 'Close' and 'Volume' are available
        df.columns = [col.lower() for col in df.columns] # Ensure all columns are lowercase
        
        if 'adj close' in df.columns: # After lowercase, it becomes 'adj close'
            df = df.rename(columns={'adj close': 'close'})
        
        if 'volume' not in df.columns:
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

# --- 2. Technical Indicator Calculation ---
def add_moving_averages(df, fast_period, slow_period):
    """Adds Simple Moving Averages (SMA) to the DataFrame using pandas.rolling()."""
    df['SMA_Fast'] = df['close'].rolling(window=fast_period).mean()
    df['SMA_Slow'] = df['close'].rolling(window=slow_period).mean()
    return df

# --- 3. Strategy Logic & 4. Signal Generation ---
def check_buy_signal(df):
    """
    Checks for a buy signal on the latest available data point.
    
    Returns:
        bool: True if a buy signal is found, False otherwise.
    """
    # Ensure there is at least two data points to check for a crossover
    if len(df) < 2:
        return False
        
    # Get the last two data points
    latest_data = df.iloc[-1]
    prev_data = df.iloc[-2]
    
    # Buy Signal: Price crosses SMA_Slow to the upside
    buy_signal_current = latest_data['close'] > latest_data['SMA_Slow']
    buy_signal_prev = prev_data['close'] <= prev_data['SMA_Slow']
    
    return buy_signal_current and buy_signal_prev
    
def get_last_buy_signal_date(df):
    """
    Finds the date of the most recent buy signal in the DataFrame.

    Returns:
        datetime.date: The date of the last buy signal, or None if no signal is found.
    """
    # Create a boolean series for all buy signals
    buy_signals = (df['close'] > df['SMA_Slow']) & (df['close'].shift(1) <= df['SMA_Slow'].shift(1))

    # Get the index (date) of the last True value
    last_signal_date = None
    if buy_signals.any():
        last_signal_date = buy_signals[buy_signals].index[-1].date()
        
    return last_signal_date

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Analyze Stock for SMA Buy Signal ---")

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

    # We now only need two specific MA periods to check the signal
    fast_ma_period = 21
    slow_ma_period = 7
    
    print(f">> ")
    print(f">> --------------------------------------------------------------------")
    print(f">> BEGIN Processing - {ticker_symbol} - Determining SMA Buy Signal ...")
    
    if downloaded_csv_path:
        data = load_data_from_csv(downloaded_csv_path)

        if not data.empty:
            # Add Technical Indicators
            data = add_moving_averages(data, fast_ma_period, slow_ma_period)
            data.dropna(subset=['SMA_Fast', 'SMA_Slow'], inplace=True)
            
            # Check for buy signal and print the result
            has_buy_signal = check_buy_signal(data)
            print(f">>    Ticker Symbol - {ticker_symbol} - SMA Buy => {has_buy_signal}")
            
            # Find and print the date of the last buy signal
            last_buy_date = get_last_buy_signal_date(data)
            print(f">>    Ticker Symbol - {ticker_symbol} - Last SMA Buy => {last_buy_date}")
        else:
            print(f">>    Failed to load data from {downloaded_csv_path}.")
            
    print(f">> END Processing - {ticker_symbol} - Determining SMA Buy Signal ...")
    print(f">> --------------------------------------------------------------------")
    print(f">> ")
