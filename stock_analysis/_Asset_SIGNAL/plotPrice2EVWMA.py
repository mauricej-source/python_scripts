import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
from datetime import datetime, timedelta

def calculate_ema(data, span):
    """
    Calculates the Exponential Moving Average (EMA) manually.
    
    Args:
        data (pd.Series): The input data series (e.g., 'close' prices).
        span (int): The span for the EMA calculation.

    Returns:
        pd.Series: The EMA series.
    """
    return data.ewm(span=span, adjust=False).mean()

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
    Ensures consistent lowercase column naming.

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
        # Download data with auto_adjust=True for adjusted prices directly in 'Close'
        data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)

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
        data.columns = [col.replace(' ', '_').lower() for col in data.columns]
        
        # 'adj_close' often appears if auto_adjust=False, but with True, 'close' is already adjusted.
        # If 'adj_close' somehow still exists and 'close' is also there, prefer 'close'.
        # If only 'adj_close' exists, rename it to 'close'.
        if 'adj_close' in data.columns and 'close' in data.columns:
            data = data.drop(columns=['adj_close'])
        elif 'adj_close' in data.columns and 'close' not in data.columns:
            data = data.rename(columns={'adj_close': 'close'})

        # Define expected required columns in lowercase based on standard yfinance output
        required_columns_lower = ['open', 'high', 'low', 'close', 'volume']
        
        # Check if required columns are present after standardization
        if not all(col in data.columns for col in required_columns_lower):
            missing_cols = [col for col in required_columns_lower if col not in data.columns]
            print(f"Error: Downloaded data for {ticker} is missing required columns after processing: {', '.join(missing_cols)}")
            print("Please ensure the ticker symbol is correct and has complete historical data.")
            return None

        # Set index name to 'date' (lowercase) before saving
        data.index.name = 'date'
        data.to_csv(output_filename, index=True, header=True)
        print(f"Historical data for {ticker} saved to {output_filename}")
        
        # We are skipping the clean_csv_header call here as it's not designed for yfinance output
        # and was causing issues with column renaming/case.
        # If you truly need custom cleaning for other data sources, call it elsewhere.
        # print(f"Clean Historical Data CSV Header for {ticker}")
        # clean_csv_header(output_filename, ticker) 
        
        return output_filename

    except Exception as e:
        print(f"An error occurred during data download for {ticker}: {e}")
        return None
        
def calculate_indicators_from_csv(csv_filepath):
    """
    Reads historical data from a CSV file and calculates EVWMA, VWAP, MACD,
    two EVWMAs (short/long), and EVWMA-based Oscillator, Signal, and Histogram.
    Uses lowercase column names for consistency.
    """
    try:
        print(f"Reading historical data from: {csv_filepath}...")
        # CRUCIAL FIX: Use 'date' (lowercase) for index_col
        data = pd.read_csv(csv_filepath, index_col='date', parse_dates=True)

        if data.empty:
            print(f"No data found in {csv_filepath}.")
            return None

        # CRUCIAL FIX: Use lowercase column names
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        
        # Ensure column names are already lowercase in the DataFrame as expected
        # (This was handled in download_historical_data)
        if not all(col in data.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in data.columns]
            print(f"Error: Missing required columns in CSV: {', '.join(missing_cols)}")
            print("Please ensure your CSV has 'open', 'high', 'low', 'close', 'volume' columns (all lowercase).")
            return None

        for col in required_columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
            
        data = data.dropna(subset=required_columns)

        if data.empty:
            print("No valid numeric data remaining after processing.")
            return None

        print(f"Data loaded from CSV. Shape: {data.shape}")

        # 1. Calculate VWAP (Volume Weighted Average Price)
        # CRUCIAL FIX: Use lowercase column names
        data['typical_price'] = (data['high'] + data['low'] + data['close']) / 3
        data['cumulative_tp_volume'] = (data['typical_price'] * data['volume']).cumsum()
        data['cumulative_volume'] = data['volume'].cumsum()
        data['vwap'] = data.apply(lambda row: row['cumulative_tp_volume'] / row['cumulative_volume'] if row['cumulative_volume'] != 0 else np.nan, axis=1)
        data = data.drop(columns=['typical_price', 'cumulative_tp_volume', 'cumulative_volume'])
        print("VWAP calculated.")

        # 2. Calculate MACD (Moving Average Convergence Divergence) - Manual Implementation
        # Calculate fast (12-period) and slow (26-period) EMAs
        ema_fast = calculate_ema(data['close'], 12)
        ema_slow = calculate_ema(data['close'], 26)
        
        # Calculate MACD line and Signal line
        data['macd_line'] = ema_fast - ema_slow
        data['macd_signal_line'] = calculate_ema(data['macd_line'], 9)
        
        # Calculate Histogram
        data['macd_histogram'] = data['macd_line'] - data['macd_signal_line']
        
        print("Standard MACD calculated manually.")

        # 3. Calculate EVWMA (Elastic Volume Weighted Moving Average) - Short Term
        # --- ADJUST THESE VOLUME SPAN VALUES FOR MORE/LESS SIGNALS ---
        volume_span_short = 40_500_000
        print(f"Calculating Short-term EVWMA with volume span: {volume_span_short:,.0f}.")
        data['evwma_short'] = np.nan
        # CRUCIAL FIX: Use lowercase 'volume' and 'close'
        if data['volume'].sum() == 0:
            print("Warning: Total volume is zero for Short-term EVWMA, cannot be calculated.")
        else:
            if not data.empty:
                data.loc[data.index[0], 'evwma_short'] = data.loc[data.index[0], 'close']
                for i in range(1, len(data)):
                    prev_evwma = data.loc[data.index[i-1], 'evwma_short']
                    current_price = data.loc[data.index[i], 'close']
                    current_volume = data.loc[data.index[i], 'volume']
                    alpha = min(current_volume / volume_span_short, 1.0)
                    data.loc[data.index[i], 'evwma_short'] = alpha * current_price + (1 - alpha) * prev_evwma
            print("Short-term EVWMA calculated.")

        # 4. Calculate EVWMA (Elastic Volume Weighted Moving Average) - Long Term
        volume_span_long = 120_000_000 # Corrected the typo '_000_000_000'
        print(f"Calculating Long-term EVWMA with volume span: {volume_span_long:,.0f}.")
        data['evwma_long'] = np.nan
        # CRUCIAL FIX: Use lowercase 'volume' and 'close'
        if data['volume'].sum() == 0:
            print("Warning: Total volume is zero for Long-term EVWMA, cannot be calculated.")
        else:
            if not data.empty:
                data.loc[data.index[0], 'evwma_long'] = data.loc[data.index[0], 'close']
                for i in range(1, len(data)):
                    prev_evwma = data.loc[data.index[i-1], 'evwma_long']
                    current_price = data.loc[data.index[i], 'close']
                    current_volume = data.loc[data.index[i], 'volume']
                    alpha = min(current_volume / volume_span_long, 1.0)
                    data.loc[data.index[i], 'evwma_long'] = alpha * current_price + (1 - alpha) * prev_evwma
            print("Long-term EVWMA calculated.")

        # 5. Calculate EVWMA-based Oscillator, Signal, and Histogram (for smoothing)
        # CRUCIAL FIX: Use lowercase EVWMA column names
        data['evwma_oscillator'] = data['evwma_short'] - data['evwma_long']
        
        # Signal Smoothing 1: EMA of the EVWMA_Oscillator (Manually)
        signal_smoothing_period = 9
        data['evwma_signal'] = calculate_ema(data['evwma_oscillator'], signal_smoothing_period)
        
        print(f"EVWMA Signal (Smoothing 1) calculated with period: {signal_smoothing_period}.")

        # Signal Smoothing 2 (represented visually by the histogram)
        # CRUCIAL FIX: Use lowercase EVWMA column name
        data['evwma_histogram'] = data['evwma_oscillator'] - data['evwma_signal']
        print("EVWMA Histogram (Smoothing 2) calculated.")

        # CRUCIAL FIX: Update final_cols to reflect lowercase names
        final_cols = ['open', 'high', 'low', 'close', 'volume',
                      'vwap', 'macd_line', 'macd_signal_line', 'macd_histogram',
                      'evwma_short', 'evwma_long',
                      'evwma_oscillator', 'evwma_signal', 'evwma_histogram']
            
        existing_final_cols = [col for col in final_cols if col in data.columns]
        output_data = data[existing_final_cols]
            
        for col in final_cols:
            if col not in output_data.columns:
                output_data[col] = np.nan

        return output_data

    except FileNotFoundError:
        print(f"Error: The file '{csv_filepath}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred during data loading or calculation: {e}")
        return None

def generate_single_evwma_chart(df, title="Price Crossovers with Single EVWMA (Standard Logic)"):
    """
    Generates a chart of Close Price and a single EVWMA, showing standard crossover signals.
    X-axis labels are shown only at signal points.
    Uses lowercase column names.
    """
    # CRUCIAL FIX: Use lowercase column names
    if 'close' not in df.columns or 'evwma_short' not in df.columns:
        print("Error: DataFrame must contain 'close' and 'evwma_short' columns for charting.")
        return

    fig, ax = plt.subplots(figsize=(14, 7))

    ax.plot(df.index, df['close'], label='Close Price', color='blue', linewidth=1.5, alpha=0.7)
    ax.plot(df.index, df['evwma_short'], label=f'EVWMA (Short)', color='red', linewidth=1.5)

    # --- STANDARD BUY SIGNAL: Price crosses ABOVE EVWMA (EVWMA goes below Price) ---
    buy_signals = df[
        (df['close'].shift(1) < df['evwma_short'].shift(1)) & # Price was below EVWMA
        (df['close'] >= df['evwma_short'])                      # Price is now above or equal to EVWMA
    ]
    
    # --- STANDARD SELL SIGNAL: Price crosses BELOW EVWMA (EVWMA goes above Price) ---
    sell_signals = df[
        (df['close'].shift(1) > df['evwma_short'].shift(1)) & # Price was above EVWMA
        (df['close'] <= df['evwma_short'])                      # Price is now below or equal to EVWMA
    ]

    # Plot Signals
    ax.scatter(buy_signals.index, buy_signals['close'], marker='^', color='green', s=100, label='Price Crosses Above EVWMA (Buy)', zorder=5)
    ax.scatter(sell_signals.index, sell_signals['close'], marker='v', color='red', s=100, label='Price Crosses Below EVWMA (Sell)', zorder=5)

    # Customize X-axis
    signal_dates = sorted(list(buy_signals.index) + list(sell_signals.index))
    if signal_dates:
        if len(signal_dates) > 15:
            indices = np.linspace(0, len(signal_dates) - 1, 15).astype(int)
            display_signal_dates = [signal_dates[i] for i in indices]
        else:
            display_signal_dates = signal_dates
            
        signal_labels = [d.strftime('%Y-%m-%d') for d in display_signal_dates]
        ax.set_xticks(display_signal_dates)
        ax.set_xticklabels(signal_labels, rotation=45, ha='right')
    
    if not df.empty:
        ax.set_xlim(df.index.min(), df.index.max())
        ax.set_xlabel('Date', fontsize=12)

    ax.set_title(title, fontsize=16)
    ax.set_ylabel('Price', fontsize=12)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

def generate_double_evwma_chart(df, title="Double EVWMA Crossover Signals"):
    """
    Generates a chart of Close Price and two EVWMAs, showing signals based on
    the short EVWMA crossing the long EVWMA.
    X-axis labels are shown only at signal points.
    Uses lowercase column names.
    """
    # CRUCIAL FIX: Use lowercase column names
    if 'close' not in df.columns or 'evwma_short' not in df.columns or 'evwma_long' not in df.columns:
        print("Error: DataFrame must contain 'close', 'evwma_short', and 'evwma_long' columns for charting.")
        return

    fig, ax = plt.subplots(figsize=(14, 7))

    ax.plot(df.index, df['close'], label='Close Price', color='blue', linewidth=1.5, alpha=0.7)
    ax.plot(df.index, df['evwma_short'], label=f'EVWMA (Short)', color='red', linewidth=1.5)
    ax.plot(df.index, df['evwma_long'], label=f'EVWMA (Long)', color='purple', linewidth=1.5)

    # --- Double EVWMA Crossover Signal Logic ---
    # Buy Signal: Short EVWMA crosses ABOVE Long EVWMA
    # CRUCIAL FIX: Use lowercase EVWMA column names
    buy_signals = df[df['evwma_short'].shift(1) < df['evwma_long'].shift(1)] \
                      [df['evwma_short'] >= df['evwma_long']]
    
    # Sell Signal: Short EVWMA crosses BELOW Long EVWMA
    # CRUCIAL FIX: Use lowercase EVWMA column names
    sell_signals = df[df['evwma_short'].shift(1) > df['evwma_long'].shift(1)] \
                       [df['evwma_short'] <= df['evwma_long']]

    # Plot Signals (on the Short EVWMA line for visual clarity)
    # CRUCIAL FIX: Use lowercase EVWMA column name
    ax.scatter(buy_signals.index, buy_signals['evwma_short'], marker='^', color='green', s=100, label='Short EVWMA Crosses Above Long (Buy)', zorder=5)
    ax.scatter(sell_signals.index, sell_signals['evwma_short'], marker='v', color='red', s=100, label='Short EVWMA Crosses Below Long (Sell)', zorder=5)

    # Customize X-axis
    signal_dates = sorted(list(buy_signals.index) + list(sell_signals.index))
    if signal_dates:
        if len(signal_dates) > 15:
            indices = np.linspace(0, len(signal_dates) - 1, 15).astype(int)
            display_signal_dates = [signal_dates[i] for i in indices]
        else:
            display_signal_dates = signal_dates
            
        signal_labels = [d.strftime('%Y-%m-%d') for d in display_signal_dates]
        ax.set_xticks(display_signal_dates)
        ax.set_xticklabels(signal_labels, rotation=45, ha='right')
    
    if not df.empty:
        ax.set_xlim(df.index.min(), df.index.max())
        ax.set_xlabel('Date', fontsize=12)

    ax.set_title(title, fontsize=16)
    ax.set_ylabel('Price', fontsize=12)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

def generate_evwma_macd_style_chart(df, title="EVWMA Oscillator (MACD Style) Signals"):
    """
    Generates a chart with Close Price & EVWMAs in the top panel,
    and EVWMA Oscillator, Signal Line, and Histogram in a lower panel,
    showing signals based on Oscillator/Signal Line crossovers.
    Uses lowercase column names.
    """
    # CRUCIAL FIX: Use lowercase column names
    if not all(col in df.columns for col in ['close', 'evwma_short', 'evwma_long', 
                                             'evwma_oscillator', 'evwma_signal', 'evwma_histogram']):
        print("Error: DataFrame must contain all required EVWMA-based columns for this chart.")
        return

    # Create subplots: 2 rows, 1 column. Share x-axis (dates)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

    # --- Top Panel: Price and EVWMAs ---
    # CRUCIAL FIX: Use lowercase column names
    ax1.plot(df.index, df['close'], label='Close Price', color='blue', linewidth=1.5, alpha=0.7)
    ax1.plot(df.index, df['evwma_short'], label=f'EVWMA (Short)', color='red', linewidth=1.5)
    ax1.plot(df.index, df['evwma_long'], label=f'EVWMA (Long)', color='purple', linewidth=1.5)
    
    ax1.set_title(title, fontsize=16)
    ax1.set_ylabel('Price', fontsize=12)
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, linestyle='--', alpha=0.6)

    # --- Bottom Panel: EVWMA Oscillator, Signal, and Histogram ---
    # CRUCIAL FIX: Use lowercase column names
    ax2.plot(df.index, df['evwma_oscillator'], label='EVWMA Oscillator', color='darkorange', linewidth=1.5)
    ax2.plot(df.index, df['evwma_signal'], label='EVWMA Signal', color='green', linestyle='--', linewidth=1.5)
    
    # Plot histogram
    # CRUCIAL FIX: Use lowercase column name
    colors = ['green' if val >= 0 else 'red' for val in df['evwma_histogram']]
    ax2.bar(df.index, df['evwma_histogram'], color=colors, alpha=0.6, width=1)
    
    ax2.axhline(0, color='gray', linestyle=':', linewidth=0.8)
    ax2.set_ylabel('Oscillator Value', fontsize=12)
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, linestyle='--', alpha=0.6)

    # --- Signals based on EVWMA Oscillator crossing EVWMA Signal ---
    # CRUCIAL FIX: Use lowercase column names
    buy_signals_osc = df[df['evwma_oscillator'].shift(1) < df['evwma_signal'].shift(1)] \
                          [df['evwma_oscillator'] >= df['evwma_signal']]
    
    sell_signals_osc = df[df['evwma_oscillator'].shift(1) > df['evwma_signal'].shift(1)] \
                           [df['evwma_oscillator'] <= df['evwma_signal']]

    # Plot signals in the main price panel, using the Close Price for placement
    # CRUCIAL FIX: Use lowercase column name
    ax1.scatter(buy_signals_osc.index, df.loc[buy_signals_osc.index, 'close'], marker='^', color='lime', s=150, label='Oscillator Buy Signal', zorder=5)
    ax1.scatter(sell_signals_osc.index, df.loc[sell_signals_osc.index, 'close'], marker='v', color='darkred', s=150, label='Oscillator Sell Signal', zorder=5)


    # Customize X-axis for both plots (since sharex=True)
    all_signal_dates = sorted(list(buy_signals_osc.index) + list(sell_signals_osc.index))
    if all_signal_dates:
        if len(all_signal_dates) > 15:
            indices = np.linspace(0, len(all_signal_dates) - 1, 15).astype(int)
            display_signal_dates = [all_signal_dates[i] for i in indices]
        else:
            display_signal_dates = all_signal_dates
            
        signal_labels = [d.strftime('%Y-%m-%d') for d in display_signal_dates]
        ax2.set_xticks(display_signal_dates)
        ax2.set_xticklabels(signal_labels, rotation=45, ha='right')
    
    if not df.empty:
        ax1.set_xlim(df.index.min(), df.index.max())
        ax2.set_xlabel('Date', fontsize=12)

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.05)
    plt.show()


if __name__ == "__main__":
    print(f">> ")
    print(f">> --------------------------------------------------------------------")
    print(f">> BEGIN Processing - Evaluate Price to EVWMA ...")
    print(f">> --------------------------------------------------------------------")
    print(f">> ")

    # Define the output directory and ensure it exists
    output_dir = "E:/_scripts_PYTHON/_personal/_OUTPUT"
    os.makedirs(output_dir, exist_ok=True)
    print(f">>    Output directory '{output_dir}' checked/created.")

    # Get today's date in YYYYMMDD format
    today_date_str = datetime.now().strftime('%Y%m%d')

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
        print(f">>    Start date defaulted to: {start_date_str}")

    # Determine end_date based on input or default
    if end_date_input:
        end_date_str = end_date_input
    else:
        # Default to the current date
        end_date_str = datetime.now().strftime('%Y-%m-%d')
        print(f">>    End date defaulted to: {end_date_str}")
    # --- MODIFIED DATE INPUT AND DEFAULTING LOGIC ENDS HERE ---

    try:
        # Convert string dates to datetime.date objects for easier comparison
        parsed_start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        parsed_end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        today_date = datetime.now().date() # Get the actual current date for comparisons
        
        # Validate that the start date is not in the future
        if parsed_start_date > today_date:
            print(f">>    Error: Start date ({start_date_str}) cannot be in the future.")
            exit()
            
        # Validate that start date is strictly before end date
        if parsed_start_date >= parsed_end_date:
            print(f">>    Error: Start date ({start_date_str}) must be strictly before end date ({end_date_str}).")
            exit()

        # Determine the effective end date for yfinance download
        # yfinance 'end' parameter is exclusive (it downloads up to the day *before* the 'end' date).
        # So, to include the user's specified (or defaulted) end_date, we need to add one day.
        # We must also ensure we don't request data beyond today for historical purposes from yfinance.
        if parsed_end_date >= today_date:
            # If user wants data up to today or a future date, download up to tomorrow's date.
            # This ensures today's data is included if available.
            effective_download_end_date = today_date + timedelta(days=1)
            print(f">>    Warning: End date ({end_date_str}) is today or in the future. Data will be downloaded up to today's available data ({today_date.strftime('%Y-%m-%d')}).")
        else:
            # If user wants data for a past period, add one day to the parsed_end_date
            # to make it inclusive for yfinance download.
            effective_download_end_date = parsed_end_date + timedelta(days=1)

        # Convert the determined dates back to string format for the download function
        # download_historical_data expects string dates.
        download_start_date_str = parsed_start_date.strftime('%Y-%m-%d')
        download_end_date_str = effective_download_end_date.strftime('%Y-%m-%d')


    except ValueError:
        print(">>    Error: Invalid date format. Please use YYYY-MM-DD.")
        exit()

    # CRITICAL CHANGE: Prefix with today's date and place in the correct directory.
    csv_file = os.path.join(output_dir, f"{today_date_str}_{ticker_symbol}_historical_data.csv")
    print(f">>    Historical data will be saved to: {csv_file}")

    csv_file_name = download_historical_data(ticker_symbol, download_start_date_str, download_end_date_str, csv_file)
    
    if csv_file_name: # Proceed only if data was downloaded successfully
        df_indicators_from_csv = calculate_indicators_from_csv(csv_file_name)

        if df_indicators_from_csv is not None and not df_indicators_from_csv.empty:
            # Calculate and print Average Daily Volume
            # CRUCIAL FIX: Use lowercase 'volume'
            avg_volume = df_indicators_from_csv['volume'].mean()
            print(f"\n>>    --- Average Daily Volume for this data: {avg_volume:,.0f} shares ---")
            print(">>    Use this value to help adjust 'volume_span_short' and 'volume_span_long' for desired responsiveness.")
            print(">>    e.g., A volume_span of 10x ADV will be for ~10 trading days.")
            print(">>    Smaller volume_span values = more responsive EVWMA = more signals (and potentially more noise).")
            print(">>    Larger volume_span values = smoother EVWMA = fewer signals (and potentially less noise).\n")


            print("\n>>    --- Calculated Indicators from CSV (first 5 rows) ---")
            print(df_indicators_from_csv.head())

            print("\n>>    --- Calculated Indicators from CSV (last 5 rows) ---")
            print(df_indicators_from_csv.tail())

            # CRITICAL CHANGE: Prefix with today's date and place in the correct directory.
            output_filename = os.path.join(output_dir, f"{today_date_str}_{ticker_symbol}_indicators_from_csv_output.csv")
            df_indicators_from_csv.to_csv(output_filename)
            print(f"\n>>    Indicators saved to {output_filename}")

            print("\n>>    Generating Single EVWMA Chart (Standard Crossover)...")
            generate_single_evwma_chart(df_indicators_from_csv, title=f"LEADING - Single EVWMA Crossover - {ticker_symbol}")

            print("\n>>    Generating EVWMA Oscillator (MACD Style) Chart...")
            generate_evwma_macd_style_chart(df_indicators_from_csv, title=f"INBETWEEN - EVWMA Oscillator - {ticker_symbol}")
            
            print("\n>>    Generating Double EVWMA Crossover Chart...")
            generate_double_evwma_chart(df_indicators_from_csv, title=f"LAGGING - Double EVWMA Crossover - {ticker_symbol}")            

        else:
            print(">>    Failed to calculate indicators from CSV.")
    else:
        print(">>    Data download failed, unable to proceed with indicator calculation and charting.")
        
    print(f">> ") 
    print(f">> --------------------------------------------------------------------")    
    print(f">> END Processing - Evaluate Price to EVWMA for - {ticker_symbol} ...")
    print(f">> --------------------------------------------------------------------")
    print(f">> ")           
