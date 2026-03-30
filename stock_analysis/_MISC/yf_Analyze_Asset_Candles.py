import os
import pandas as pd
import pandas_ta as ta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
import mplfinance as mpf # <--- ADDED IMPORT for mplfinance
from datetime import datetime, timedelta

def clean_csv_header(input_filepath, ticker, output_filepath=None):
    """
    Reads a CSV file, replaces 'Price' with 'Date' in the first line,
    and removes specific second and third lines if they match the specified format.

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
        if first_line.startswith('Price,'):
            modified_lines.append('date' + first_line[5:] + '\n')
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
        # Check for the exact format "Ticker,JNJ,JNJ,JNJ,JNJ,JNJ"
        if second_line.startswith('Ticker,') and all(part == ticker for part in second_line.split(',')[1:]):
            lines_to_skip += 1
            print(f"Skipping second line: '{second_line}'")
        else:
            modified_lines.append(lines[1])
            print(f"Second line not skipped: '{second_line}'")

    if len(lines) > 2 and lines_to_skip == 1: # Only check third line if second was skipped
        third_line = lines[2].strip()
        # Check for the exact format "Date,,,,"
        if third_line == 'Date,,,,,':
            lines_to_skip += 1
            print(f"Skipping third line: '{third_line}'")
        else:
            # If the second line was skipped but the third wasn't, add the third line back.
            # This handles cases where only the second line matches for skipping.
            if lines_to_skip == 1: # This means the second line was skipped, but third was not.
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
        # Download data
        data = yf.download(ticker, start=start_date, end=end_date)

        if data.empty:
            print(f"No data downloaded for {ticker} in the specified date range. Please check the ticker and dates.")
            return None

        # --- CRUCIAL FIX: Handle MultiIndex columns from yfinance output ---
        # If the columns are a MultiIndex (e.g., [('Close', 'JNJ')]), flatten them.
        if isinstance(data.columns, pd.MultiIndex):
            # For a single ticker, the second level of the MultiIndex is often the ticker symbol itself.
            # Dropping this level simplifies the column names to 'Open', 'High', 'Low', etc.
            data.columns = data.columns.droplevel(1)
            
        # Ensure all columns are lowercase and spaces replaced with underscores for consistency
        # Also handle potential dots in column names (e.g., 'Adj. Close' -> 'adj_close')
        data.columns = [col.replace(' ', '_').replace('.', '').lower() for col in data.columns]
        
        # Drop 'adj_close' if it exists and 'close' is also available,
        # or rename 'adj_close' to 'close' if 'close' isn't present.
        # yfinance with auto_adjust=True often makes 'Close' the adjusted price directly.
        if 'adj_close' in data.columns and 'close' in data.columns:
            # If both exist, and 'close' is already adjusted, you might want to drop 'adj_close'
            data = data.drop(columns=['adj_close'])
        elif 'adj_close' in data.columns and 'close' not in data.columns:
            # If only 'adj_close' exists, rename it to 'close'
            data = data.rename(columns={'adj_close': 'close'})

        # Define expected required columns in lowercase based on standard yfinance output
        # 'price' is not a default yfinance column, it's usually derived or a user-defined term.
        # Standard are 'open', 'high', 'low', 'close', 'volume'.
        required_columns_lower = ['open', 'high', 'low', 'close', 'volume']
        
        # Check if required columns are present after standardization
        if not all(col in data.columns for col in required_columns_lower):
            missing_cols = [col for col in required_columns_lower if col not in data.columns]
            print(f"Error: Downloaded data for {ticker} is missing required columns after processing: {', '.join(missing_cols)}")
            print("Please ensure the ticker symbol is correct and has complete historical data.")
            return None

        # Save to CSV:
        data.index.name = 'date' # Set index name before saving
        data.to_csv(output_filename, index=True, header=True) # index_label='date' is not needed if index.name is set
        print(f"Historical data for {ticker} saved to {output_filename}")
        
        print(f"Clean Historical Data CSV Header for {ticker}")
        # Call your header cleaning function after saving the initial CSV
        clean_csv_header(output_filename, ticker) 
        
        return output_filename

    except Exception as e:
        print(f"An error occurred during data download for {ticker}: {e}")
        return None

def calculate_indicators_from_csv(csv_filepath, volume_span_short_param, volume_span_long_param):
    """
    Loads stock data from a CSV, sets 'date' as index, handles duplicates,
    and calculates indicators.
    """
    print(f"Reading historical data from: {csv_filepath}...")
    try:
        # Load the CSV file
        # The 'date' column should be parsed as dates and set as the index
        df = pd.read_csv(csv_filepath, index_col='date', parse_dates=True)

        # --- FIX: Handle duplicate index labels ---
        # Check for duplicates in the index (the 'date' column)
        if not df.index.is_unique:
            print(f"Warning: Duplicate dates found in {csv_filepath}. Removing duplicate date entries.")
            # Option 1: Keep the first occurrence of each duplicate date
            df = df[~df.index.duplicated(keep='first')]
            
            # After removing duplicates, ensure the index is sorted
            df = df.sort_index()

        print(f"Data loaded from CSV. Shape: {df.shape}")

        # Ensure column names are consistent (lowercase, no spaces/dots)
        df.columns = [col.replace(' ', '_').replace('.', '').lower() for col in df.columns]

        # Check for required columns after loading and standardization
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            print(f"Error: Missing required columns for indicator calculation: {', '.join(missing)}")
            return None

        # --- Use the passed-in parameters directly for volume spans ---
        volume_span_short = volume_span_short_param
        volume_span_long = volume_span_long_param
        
        # Calculate EVWMA (Exponential Volume Weighted Moving Average)
        avg_volume = df['volume'].mean()
        if avg_volume == 0:
            print("Error: Average volume is zero. Cannot calculate EVWMA based on volume spans.")
            return None

        # Ensure lengths are positive; if volume is extremely low, length calculation could be problematic
        length_short = max(1, round(volume_span_short / avg_volume))
        length_long = max(1, round(volume_span_long / avg_volume))

        # Check if 'close' and 'volume' are numeric
        if not pd.api.types.is_numeric_dtype(df['close']) or not pd.api.types.is_numeric_dtype(df['volume']):
            print("Error: 'close' or 'volume' columns are not numeric. Cannot calculate EVWMA.")
            return None

        # Calculate weighted average for EVWMA base
        df['close_vol'] = df['close'] * df['volume']

        df['evwma_short'] = df['close_vol'].ewm(span=length_short, adjust=False).mean() / df['volume'].ewm(span=length_short, adjust=False).mean()
        df['evwma_long'] = df['close_vol'].ewm(span=length_long, adjust=False).mean() / df['volume'].ewm(span=length_long, adjust=False).mean()

        # Calculate EVWMA for MACD-style indicator
        length_fast = max(1, round(length_short / 2))
        length_slow = max(1, round(length_long * 0.75))

        df['evwma_fast'] = df['close_vol'].ewm(span=length_fast, adjust=False).mean() / df['volume'].ewm(span=length_fast, adjust=False).mean()
        df['evwma_slow'] = df['close_vol'].ewm(span=length_slow, adjust=False).mean() / df['volume'].ewm(span=length_slow, adjust=False).mean()

        df['evwma_oscillator'] = df['evwma_fast'] - df['evwma_slow']
        df['evwma_signal'] = df['evwma_oscillator'].ewm(span=9, adjust=False).mean() # Standard 9-period EMA for signal line
        df['evwma_hist'] = df['evwma_oscillator'] - df['evwma_signal']
        
        # Drop the temporary 'close_vol' column
        df = df.drop(columns=['close_vol'])

        # --- ADDED RSI CALCULATION HERE ---
        df['rsi_14'] = ta.rsi(df['close'], length=14) # Standard 14-period RSI
        # --- END ADDED RSI CALCULATION ---

        # Generate buy/sell signals for single EVWMA (for potential use elsewhere or for logic)
        df['single_signal'] = 0
        df.loc[df['close'] > df['evwma_short'], 'single_signal'] = 1
        df.loc[df['close'] < df['evwma_short'], 'single_signal'] = -1

        # Generate buy/sell signals for double EVWMA crossover (for potential use elsewhere or for logic)
        df['double_signal'] = 0
        df.loc[(df['evwma_short'].shift(1) < df['evwma_long'].shift(1)) & (df['evwma_short'] > df['evwma_long']), 'double_signal'] = 1
        df.loc[(df['evwma_short'].shift(1) > df['evwma_long'].shift(1)) & (df['evwma_short'] < df['evwma_long']), 'double_signal'] = -1
        
        return df

    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_filepath}")
        return None
    except KeyError as e:
        print(f"An error occurred during data loading or calculation: Missing expected column: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during indicator calculation: {e}")
        return None


def generate_single_evwma_chart(df, title="Price & EVWMA Crossovers (Modified Sell Signal)"):
    """
    Generates a candlestick chart of Close Price and a single EVWMA, with RSI.
    Uses mplfinance for plotting.
    """
    required_cols = ['open', 'high', 'low', 'close', 'volume', 'evwma_short', 'rsi_14']
    if not all(col in df.columns for col in required_cols):
        print(f"Error: DataFrame must contain '{', '.join(required_cols)}' columns for charting.")
        return

    # Prepare DataFrame for mplfinance (renaming columns to expected case)
    mpf_df = df.copy()
    mpf_df.columns = [col.capitalize() if col in ['open', 'high', 'low', 'close', 'volume'] else col for col in mpf_df.columns]
    
    # Ensure index is datetime
    if not isinstance(mpf_df.index, pd.DatetimeIndex):
        print("Warning: Index is not DatetimeIndex. Attempting to convert.")
        mpf_df.index = pd.to_datetime(mpf_df.index)

    # --- Signal Logic (remains largely the same, but prepare for addplot) ---
    buy_conditions = (mpf_df['Close'].shift(1) < mpf_df['evwma_short'].shift(1)) & \
                     (mpf_df['Close'] >= mpf_df['evwma_short'])
    buy_signals = mpf_df[buy_conditions].dropna()

    sell_conditions = (mpf_df['Close'].shift(1) > mpf_df['evwma_short'].shift(1)) & \
                      (mpf_df['Close'] <= mpf_df['evwma_short']) & \
                      (mpf_df['Close'] < mpf_df['Close'].shift(3))
    sell_signals = mpf_df[sell_conditions].dropna()

    bottom_conditions = (mpf_df['Close'].shift(1) < mpf_df['evwma_short'].shift(1)) & \
                        (mpf_df['Close'] >= mpf_df['evwma_short']) & \
                        (mpf_df['rsi_14'] < 30)
    bottom_signals = mpf_df[bottom_conditions].dropna()

    # Create addplots for indicators and signals
    apds = [
        mpf.make_addplot(mpf_df['evwma_short'], color='red', panel=0, width=1.5,
                         type='line', linestyle='-', label='EVWMA (Short)'),
        # Moved RSI to panel=2 to ensure it's below volume, making 3 distinct panels
        mpf.make_addplot(mpf_df['rsi_14'], color='purple', panel=2, ylabel='RSI (14)'),
        mpf.make_addplot(pd.Series(70, index=mpf_df.index), panel=2, color='red', linestyle='--', width=0.7, alpha=0.7),
        mpf.make_addplot(pd.Series(30, index=mpf_df.index), panel=2, color='green', linestyle='--', width=0.7, alpha=0.7),
    ]

    # Add buy signals to addplots (scatter on main panel)
    if not buy_signals.empty:
        # Create a series with NaNs except at signal points for scatter plot
        buy_plot_data = pd.Series(index=mpf_df.index, dtype=float)
        buy_plot_data.loc[buy_signals.index] = mpf_df.loc[buy_signals.index, 'Low'] * 0.98 # Plot slightly below candle for clarity
        apds.append(mpf.make_addplot(buy_plot_data, type='scatter', marker='^', color='green', markersize=100, panel=0, label='Buy Signal'))
    
    # Add sell signals to addplots (scatter on main panel)
    if not sell_signals.empty:
        # Create a series with NaNs except at signal points for scatter plot
        sell_plot_data = pd.Series(index=mpf_df.index, dtype=float)
        sell_plot_data.loc[sell_signals.index] = mpf_df.loc[sell_signals.index, 'High'] * 1.02 # Plot slightly above candle for clarity
        apds.append(mpf.make_addplot(sell_plot_data, type='scatter', marker='v', color='red', markersize=100, panel=0, label='Sell Signal'))

    # Add bottom signals to addplots (scatter on main panel)
    if not bottom_signals.empty:
        # Create a series with NaNs except at signal points for scatter plot
        bottom_plot_data = pd.Series(index=mpf_df.index, dtype=float)
        bottom_plot_data.loc[bottom_signals.index] = mpf_df.loc[bottom_signals.index, 'Low'] * 0.96 # Plot further below for emphasis
        apds.append(mpf.make_addplot(bottom_plot_data, type='scatter', marker='*', color='blue', markersize=200, panel=0, label='Potential Bottom'))
    
    # Plotting with mplfinance
    mpf.plot(mpf_df,
             type='candle',
             style='yahoo',
             volume=True,   # Include volume subplot below price
             addplot=apds,
             panel_ratios=(3, 1, 1), # Ratio of height for price, volume, RSI. Now explicitly 3 panels.
             figscale=1.5,       # Adjust figure size (e.g., 1.5x default)
             title=title,
             ylabel='Price',
             ylabel_lower='Volume',
            )
    plt.show()

def generate_double_evwma_chart(df, title="Double EVWMA Crossover Signals"):
    """
    Generates a candlestick chart of Close Price and two EVWMAs, showing signals based on
    the short EVWMA crossing the long EVWMA AND price crossing above the long EVWMA.
    Uses mplfinance for plotting.
    """
    required_cols = ['open', 'high', 'low', 'close', 'volume', 'evwma_short', 'evwma_long']
    if not all(col in df.columns for col in required_cols):
        print(f"Error: DataFrame must contain '{', '.join(required_cols)}' columns for charting.")
        return

    # Prepare DataFrame for mplfinance
    mpf_df = df.copy()
    mpf_df.columns = [col.capitalize() if col in ['open', 'high', 'low', 'close', 'volume'] else col for col in mpf_df.columns]
    
    if not isinstance(mpf_df.index, pd.DatetimeIndex):
        print("Warning: Index is not DatetimeIndex. Attempting to convert.")
        mpf_df.index = pd.to_datetime(mpf_df.index)

    # --- Signal Logic ---
    crossover_buy_conditions = (mpf_df['evwma_short'].shift(1) < mpf_df['evwma_long'].shift(1)) & \
                               (mpf_df['evwma_short'] >= mpf_df['evwma_long'])
    
    price_cross_long_buy_conditions = (mpf_df['Close'].shift(1) < mpf_df['evwma_long'].shift(1)) & \
                                      (mpf_df['Close'] >= mpf_df['evwma_long'])

    # Combine both buy conditions
    buy_signals_df = mpf_df[crossover_buy_conditions | price_cross_long_buy_conditions].dropna()

    sell_conditions = (mpf_df['evwma_short'].shift(1) > mpf_df['evwma_long'].shift(1)) & \
                      (mpf_df['evwma_short'] <= mpf_df['evwma_long'])
    sell_signals_df = mpf_df[sell_conditions].dropna()

    # Create addplots for indicators and signals
    apds = [
        mpf.make_addplot(mpf_df['evwma_short'], color='red', width=1.5, type='line', linestyle='-', label='EVWMA (Short)'),
        mpf.make_addplot(mpf_df['evwma_long'], color='purple', width=1.5, type='line', linestyle='-', label='EVWMA (Long)'),
    ]

    if not buy_signals_df.empty:
        buy_plot_data = pd.Series(index=mpf_df.index, dtype=float)
        buy_plot_data.loc[buy_signals_df.index] = mpf_df.loc[buy_signals_df.index, 'Low'] * 0.98
        apds.append(mpf.make_addplot(buy_plot_data, type='scatter', marker='^', color='green', markersize=100, label='Buy Signal'))
    
    if not sell_signals_df.empty:
        sell_plot_data = pd.Series(index=mpf_df.index, dtype=float)
        sell_plot_data.loc[sell_signals_df.index] = mpf_df.loc[sell_signals_df.index, 'High'] * 1.02
        apds.append(mpf.make_addplot(sell_plot_data, type='scatter', marker='v', color='red', markersize=100, label='Sell Signal'))

    # Plotting with mplfinance
    mpf.plot(mpf_df,
             type='candle',
             style='yahoo',
             volume=True,
             addplot=apds,
             figscale=1.5,
             title=title,
             ylabel='Price',
             ylabel_lower='Volume',
            )
    plt.show()

def generate_evwma_macd_style_chart(df, title="EVWMA Oscillator (MACD Style) Signals"):
    """
    Generates a candlestick chart with EVWMAs in the top panel,
    and EVWMA Oscillator, Signal Line, and Histogram in a lower panel,
    showing signals based on Oscillator/Signal Line crossovers.
    Uses mplfinance for plotting.
    """
    required_cols = ['open', 'high', 'low', 'close', 'volume', 'evwma_short', 'evwma_long', 
                     'evwma_oscillator', 'evwma_signal', 'evwma_hist']
    if not all(col in df.columns for col in required_cols):
        print(f"Error: DataFrame must contain all required EVWMA-based columns for this chart (e.g., '{', '.join(required_cols)}').")
        return

    # Prepare DataFrame for mplfinance
    mpf_df = df.copy()
    mpf_df.columns = [col.capitalize() if col in ['open', 'high', 'low', 'close', 'volume'] else col for col in mpf_df.columns]
    
    if not isinstance(mpf_df.index, pd.DatetimeIndex):
        print("Warning: Index is not DatetimeIndex. Attempting to convert.")
        mpf_df.index = pd.to_datetime(mpf_df.index)

    # --- Signal Logic ---
    buy_conditions_osc = (mpf_df['evwma_oscillator'].shift(1) < mpf_df['evwma_signal'].shift(1)) & \
                         (mpf_df['evwma_oscillator'] >= mpf_df['evwma_signal'])
    buy_signals_osc = mpf_df[buy_conditions_osc].dropna()
    
    sell_conditions_osc = (mpf_df['evwma_oscillator'].shift(1) > mpf_df['evwma_signal'].shift(1)) & \
                          (mpf_df['evwma_oscillator'] <= mpf_df['evwma_signal'])
    sell_signals_osc = mpf_df[sell_conditions_osc].dropna()

    # Create addplots for the main panel (EVWMAs and Price/Oscillator signals)
    apds = [
        mpf.make_addplot(mpf_df['evwma_short'], color='red', panel=0, width=1.5, type='line', linestyle='-', label='EVWMA (Short)'),
        mpf.make_addplot(mpf_df['evwma_long'], color='purple', panel=0, width=1.5, type='line', linestyle='-', label='EVWMA (Long)'),
    ]

    if not buy_signals_osc.empty:
        buy_plot_data = pd.Series(index=mpf_df.index, dtype=float)
        buy_plot_data.loc[buy_signals_osc.index] = mpf_df.loc[buy_signals_osc.index, 'Low'] * 0.98
        apds.append(mpf.make_addplot(buy_plot_data, type='scatter', marker='^', color='lime', markersize=150, panel=0, label='Oscillator Buy'))
    
    if not sell_signals_osc.empty:
        sell_plot_data = pd.Series(index=mpf_df.index, dtype=float)
        sell_plot_data.loc[sell_signals_osc.index] = mpf_df.loc[sell_signals_osc.index, 'High'] * 1.02
        apds.append(mpf.make_addplot(sell_plot_data, type='scatter', marker='v', color='darkred', markersize=150, panel=0, label='Oscillator Sell'))

    # Addplots for the lower panel (Oscillator, Signal, Histogram)
    # Moved to panel=2 to ensure it's below volume, making 3 distinct panels
    apds.extend([
        mpf.make_addplot(mpf_df['evwma_oscillator'], color='darkorange', panel=2, ylabel='EVWMA Oscillator'),
        mpf.make_addplot(mpf_df['evwma_signal'], color='green', panel=2, linestyle='--', width=1.5),
        # Histogram bars need to be colored based on their value (positive/negative)
        mpf.make_addplot(mpf_df['evwma_hist'], type='bar', panel=2,
                         color=['green' if x >= 0 else 'red' for x in mpf_df['evwma_hist']],
                         width=0.7),
    ])

    mpf.plot(mpf_df,
             type='candle',
             style='yahoo',
             volume=True,
             addplot=apds,
             panel_ratios=(3, 1, 1), # Ratio of height for price, volume, oscillator. Explicitly 3 panels.
             figscale=1.5,
             title=title,
             ylabel='Price',
             ylabel_lower='Volume',
            )
    plt.show()


if __name__ == "__main__":
    print("--- Stock Data Downloader & Indicator Charting ---")

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
        
        today_date = datetime.now().date() # Get the actual current date for comparisons
        
        # Validate that the start date is not in the future
        if parsed_start_date > today_date:
            print(f"Error: Start date ({start_date_str}) cannot be in the future.")
            exit()
            
        # Validate that start date is strictly before end date
        if parsed_start_date >= parsed_end_date:
            print(f"Error: Start date ({start_date_str}) must be strictly before end date ({end_date_str}).")
            exit()

        # Determine the effective end date for yfinance download
        # yfinance 'end' parameter is exclusive (it downloads up to the day *before* the 'end' date).
        # So, to include the user's specified (or defaulted) end_date, we need to add one day.
        # We must also ensure we don't request data beyond today for historical purposes from yfinance.
        if parsed_end_date >= today_date:
            # If user wants data up to today or a future date, download up to tomorrow's date.
            # This ensures today's data is included if available.
            effective_download_end_date = today_date + timedelta(days=1)
            print(f"Warning: End date ({end_date_str}) is today or in the future. Data will be downloaded up to today's available data ({today_date.strftime('%Y-%m-%d')}).")
        else:
            # If user wants data for a past period, add one day to the parsed_end_date
            # to make it inclusive for yfinance download.
            effective_download_end_date = parsed_end_date + timedelta(days=1)

        # Convert the determined dates back to string format for the download function
        # download_historical_data expects string dates.
        download_start_date_str = parsed_start_date.strftime('%Y-%m-%d')
        download_end_date_str = effective_download_end_date.strftime('%Y-%m-%d')


    except ValueError:
        print("Error: Invalid date format. Please use YYYY-MM-DD.")
        exit()

    csv_file = f"{ticker_symbol}_historical_data.csv"

    downloaded_csv_path = download_historical_data(ticker_symbol, download_start_date_str, download_end_date_str, csv_file)

    if downloaded_csv_path:
        # --- Define your desired volume spans here ---
        my_volume_span_short = 60_000_000 # Your preferred value
        my_volume_span_long = 145_500_000 # Example: 3x your short span, or whatever you find works best

        print(f"\nUsing custom volume spans: Short={my_volume_span_short:,}, Long={my_volume_span_long:,}")
        
        df_indicators_from_csv = calculate_indicators_from_csv(downloaded_csv_path, my_volume_span_short, my_volume_span_long)

        if df_indicators_from_csv is not None and not df_indicators_from_csv.empty:
            avg_volume = df_indicators_from_csv['volume'].mean() # Use lowercase 'volume'
            print(f"\n--- Average Daily Volume for this data: {avg_volume:,.0f} shares ---")
            print("Use this value to help adjust 'volume_span_short' and 'volume_span_long' for desired responsiveness.")
            print("  e.g., A volume_span of 10x ADV will be for ~10 trading days.")
            print("  Smaller volume_span values = more responsive EVWMA = more signals (and potentially more noise).")
            print("  Larger volume_span values = smoother EVWMA = fewer signals (and potentially less noise).\n")

            print("\n--- Calculated Indicators from CSV (first 5 rows) ---")
            print(df_indicators_from_csv.head())

            print("\n--- Calculated Indicators from CSV (last 5 rows) ---")
            print(df_indicators_from_csv.tail())

            output_filename = f"{ticker_symbol}_indicators_output.csv"
            df_indicators_from_csv.to_csv(output_filename)
            print(f"\nIndicators saved to {output_filename}")

            print("\nGenerating Single EVWMA Chart (Modified Sell Signal & Bottom Signal)...")
            generate_single_evwma_chart(df_indicators_from_csv, title=f"{ticker_symbol} Price & EVWMA Crossovers (Sell & Bottom Signals)")

            print("\nGenerating Double EVWMA Crossover Chart...")
            generate_double_evwma_chart(df_indicators_from_csv, title=f"{ticker_symbol} Double EVWMA Crossover Strategy")

            print("\nGenerating EVWMA Oscillator (MACD Style) Chart...")
            generate_evwma_macd_style_chart(df_indicators_from_csv, title=f"{ticker_symbol} EVWMA Oscillator (MACD Style) Signals")

        else:
            print("Failed to calculate indicators from downloaded CSV data.")
    else:
        print("Data download failed. Cannot proceed with chart generation.")