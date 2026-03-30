import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
from datetime import datetime, timedelta, date
import itertools

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
    # print(f"Attempting to download historical data for {ticker} from {start_date} to {end_date}...")
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
        # print(f"Historical data for {ticker} saved to {output_filename}")
        
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
        # print(f"Reading historical data from: {csv_filepath}...")
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

        # print(f"Data loaded from CSV. Shape: {data.shape}")

        # 1. Calculate VWAP (Volume Weighted Average Price)
        # CRUCIAL FIX: Use lowercase column names
        data['typical_price'] = (data['high'] + data['low'] + data['close']) / 3
        data['cumulative_tp_volume'] = (data['typical_price'] * data['volume']).cumsum()
        data['cumulative_volume'] = data['volume'].cumsum()
        data['vwap'] = data.apply(lambda row: row['cumulative_tp_volume'] / row['cumulative_volume'] if row['cumulative_volume'] != 0 else np.nan, axis=1)
        data = data.drop(columns=['typical_price', 'cumulative_tp_volume', 'cumulative_volume'])
        # print("VWAP calculated.")

        # 2. Calculate MACD (Moving Average Convergence Divergence) - Manual Implementation
        # Calculate fast (12-period) and slow (26-period) EMAs
        ema_fast = calculate_ema(data['close'], 12)
        ema_slow = calculate_ema(data['close'], 26)
        
        # Calculate MACD line and Signal line
        data['macd_line'] = ema_fast - ema_slow
        data['macd_signal_line'] = calculate_ema(data['macd_line'], 9)
        
        # Calculate Histogram
        data['macd_histogram'] = data['macd_line'] - data['macd_signal_line']
        
        # print("Standard MACD calculated manually.")

        # 3. Calculate EVWMA (Elastic Volume Weighted Moving Average) - Short Term
        # --- ADJUST THESE VOLUME SPAN VALUES FOR MORE/LESS SIGNALS ---
        volume_span_short = 40_500_000
        
        # print(f"Calculating Short-term EVWMA with volume span: {volume_span_short:,.0f}.")
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
            # print("Short-term EVWMA calculated.")

        # 4. Calculate EVWMA (Elastic Volume Weighted Moving Average) - Long Term
        volume_span_long = 120_000_000 # Corrected the typo '_000_000_000'
        
        # print(f"Calculating Long-term EVWMA with volume span: {volume_span_long:,.0f}.")
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
            # print("Long-term EVWMA calculated.")

        # 5. Calculate EVWMA-based Oscillator, Signal, and Histogram (for smoothing)
        # CRUCIAL FIX: Use lowercase EVWMA column names
        data['evwma_oscillator'] = data['evwma_short'] - data['evwma_long']
        
        # Signal Smoothing 1: EMA of the EVWMA_Oscillator (Manually)
        signal_smoothing_period = 9
        data['evwma_signal'] = calculate_ema(data['evwma_oscillator'], signal_smoothing_period)
        
        # print(f"EVWMA Signal (Smoothing 1) calculated with period: {signal_smoothing_period}.")

        # Signal Smoothing 2 (represented visually by the histogram)
        # CRUCIAL FIX: Use lowercase EVWMA column name
        data['evwma_histogram'] = data['evwma_oscillator'] - data['evwma_signal']
        # print("EVWMA Histogram (Smoothing 2) calculated.")

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

def evaluate_single_evwma_signals(df):
    """
    Evaluates buy/sell signals for the single EVWMA strategy.
    Returns boolean for current triggered status and last triggered date.
    """
    if df.shape[0] < 2 or 'close' not in df.columns or 'evwma_short' not in df.columns:
        return False, 'N/A', False, 'N/A'
    
    buy_signals = df[
        (df['close'].shift(1) < df['evwma_short'].shift(1)) &
        (df['close'] >= df['evwma_short'])
    ]
    
    sell_signals = df[
        (df['close'].shift(1) > df['evwma_short'].shift(1)) &
        (df['close'] <= df['evwma_short'])
    ]
    
    last_buy_date = buy_signals.index[-1].strftime('%Y-%m-%d') if not buy_signals.empty else 'N/A'
    last_sell_date = sell_signals.index[-1].strftime('%Y-%m-%d') if not sell_signals.empty else 'N/A'
    
    buy_triggered = False
    sell_triggered = False
    
    if not df.empty:
        # Check if the last data point meets the crossover condition
        if (df['close'].iloc[-1] >= df['evwma_short'].iloc[-1]) and \
           (df['close'].iloc[-2] < df['evwma_short'].iloc[-2]):
            buy_triggered = True
    
        if (df['close'].iloc[-1] <= df['evwma_short'].iloc[-1]) and \
           (df['close'].iloc[-2] > df['evwma_short'].iloc[-2]):
            sell_triggered = True
            
    return buy_triggered, last_buy_date, sell_triggered, last_sell_date

def evaluate_oscillator_evwma_signals(df):
    """
    Evaluates buy/sell signals for the EVWMA Oscillator strategy.
    Returns boolean for current triggered status and last triggered date.
    """
    if df.shape[0] < 2 or 'evwma_oscillator' not in df.columns or 'evwma_signal' not in df.columns:
        return False, 'N/A', False, 'N/A'
    
    buy_signals = df[
        (df['evwma_oscillator'].shift(1) < df['evwma_signal'].shift(1)) &
        (df['evwma_oscillator'] >= df['evwma_signal'])
    ]
    
    sell_signals = df[
        (df['evwma_oscillator'].shift(1) > df['evwma_signal'].shift(1)) &
        (df['evwma_oscillator'] <= df['evwma_signal'])
    ]
    
    last_buy_date = buy_signals.index[-1].strftime('%Y-%m-%d') if not buy_signals.empty else 'N/A'
    last_sell_date = sell_signals.index[-1].strftime('%Y-%m-%d') if not sell_signals.empty else 'N/A'
    
    buy_triggered = False
    sell_triggered = False
    
    if not df.empty:
        if (df['evwma_oscillator'].iloc[-1] >= df['evwma_signal'].iloc[-1]) and \
           (df['evwma_oscillator'].iloc[-2] < df['evwma_signal'].iloc[-2]):
            buy_triggered = True
            
        if (df['evwma_oscillator'].iloc[-1] <= df['evwma_signal'].iloc[-1]) and \
           (df['evwma_oscillator'].iloc[-2] > df['evwma_signal'].iloc[-2]):
            sell_triggered = True
            
    return buy_triggered, last_buy_date, sell_triggered, last_sell_date
    
def evaluate_double_evwma_signals(df):
    """
    Evaluates buy/sell signals for the double EVWMA crossover strategy.
    Returns boolean for current triggered status and last triggered date.
    """
    if df.shape[0] < 2 or 'evwma_short' not in df.columns or 'evwma_long' not in df.columns:
        return False, 'N/A', False, 'N/A'
    
    buy_signals = df[
        (df['evwma_short'].shift(1) < df['evwma_long'].shift(1)) &
        (df['evwma_short'] >= df['evwma_long'])
    ]
    
    sell_signals = df[
        (df['evwma_short'].shift(1) > df['evwma_long'].shift(1)) &
        (df['evwma_short'] <= df['evwma_long'])
    ]
    
    last_buy_date = buy_signals.index[-1].strftime('%Y-%m-%d') if not buy_signals.empty else 'N/A'
    last_sell_date = sell_signals.index[-1].strftime('%Y-%m-%d') if not sell_signals.empty else 'N/A'

    buy_triggered = False
    sell_triggered = False

    if not df.empty:
        if (df['evwma_short'].iloc[-1] >= df['evwma_long'].iloc[-1]) and \
           (df['evwma_short'].iloc[-2] < df['evwma_long'].iloc[-2]):
            buy_triggered = True
    
        if (df['evwma_short'].iloc[-1] <= df['evwma_long'].iloc[-1]) and \
           (df['evwma_short'].iloc[-2] > df['evwma_long'].iloc[-2]):
            sell_triggered = True

    return buy_triggered, last_buy_date, sell_triggered, last_sell_date
        
def generate_html_report(ticker_symbol, single_results, double_results, oscillator_results, leaning_status, overall_status):
    """
    Generates an HTML string for the EVWMA report.
    """
    single_buy_triggered, single_last_buy, single_sell_triggered, single_last_sell = single_results
    double_buy_triggered, double_last_buy, double_sell_triggered, double_last_sell = double_results
    oscillator_buy_triggered, oscillator_last_buy, oscillator_sell_triggered, oscillator_last_sell = oscillator_results

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EVWMA Signal Report - {ticker_symbol}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 0;
                background-color: #f4f4f4;
                color: #333;
            }}
            .container {{
                max-width: 800px;
                margin: auto;
                background: #fff;
                padding: 20px 40px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            h1, h2, h3 {{
                color: #0056b3;
                border-bottom: 2px solid #ddd;
                padding-bottom: 5px;
            }}
            .section {{
                margin-bottom: 20px;
            }}
            .signal-item {{
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }}
            .signal-item:last-child {{
                border-bottom: none;
            }}
            .signal-result {{
                font-weight: bold;
                color: #28a745;
            }}
            .signal-result.no {{
                color: #dc3545;
            }}
            .last-date {{
                font-style: italic;
                color: #6c757d;
            }}
            .overall {{
                text-align: center;
                margin-top: 30px;
                padding: 20px;
                background-color: #e9ecef;
                border-radius: 8px;
            }}
            .overall h2 {{
                border-bottom: none;
                margin-top: 0;
            }}
            .overall-buy {{
                font-size: 1.5em;
                font-weight: bold;
                color: #28a745;
            }}
            .overall-sell {{
                font-size: 1.5em;
                font-weight: bold;
                color: #dc3545;
            }}
            .overall-none {{
                font-size: 1.5em;
                font-weight: bold;
                color: #6c757d;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>EVWMA Signal Report</h1>
            <h2>Stock Ticker: {ticker_symbol}</h2>

            <div class="section">
                <h3>LEADING - Single EVWMA Signals</h3>
                <ul>
                    <li class="signal-item">
                        <b>Buy Signal Triggered:</b> <span class="signal-result {'no' if not single_buy_triggered else ''}">{single_buy_triggered}</span>
                    </li>
                    <li class="signal-item">
                        <b>Last Buy Signal:</b> <span class="last-date">{single_last_buy}</span>
                    </li>
                    <li class="signal-item">
                        <b>Sell Signal Triggered:</b> <span class="signal-result {'no' if not single_sell_triggered else ''}">{single_sell_triggered}</span>
                    </li>
                    <li class="signal-item">
                        <b>Last Sell Signal:</b> <span class="last-date">{single_last_sell}</span>
                    </li>
                </ul>
            </div>
            
            <div class="section">
                <h3>INBETWEEN - Oscillator EVWMA Signals</h3>
                <ul>
                    <li class="signal-item">
                        <b>Buy Signal Triggered:</b> <span class="signal-result {'no' if not oscillator_buy_triggered else ''}">{oscillator_buy_triggered}</span>
                    </li>
                    <li class="signal-item">
                        <b>Last Buy Signal:</b> <span class="last-date">{oscillator_last_buy}</span>
                    </li>
                    <li class="signal-item">
                        <b>Sell Signal Triggered:</b> <span class="signal-result {'no' if not oscillator_sell_triggered else ''}">{oscillator_sell_triggered}</span>
                    </li>
                    <li class="signal-item">
                        <b>Last Sell Signal:</b> <span class="last-date">{oscillator_last_sell}</span>
                    </li>
                </ul>
            </div>
            
            <div class="section">
                <h3>LAGGING - Double EVWMA Crossover Signals</h3>
                <ul>
                    <li class="signal-item">
                        <b>Buy Signal Triggered:</b> <span class="signal-result {'no' if not double_buy_triggered else ''}">{double_buy_triggered}</span>
                    </li>
                    <li class="signal-item">
                        <b>Last Buy Signal:</b> <span class="last-date">{double_last_buy}</span>
                    </li>
                    <li class="signal-item">
                        <b>Sell Signal Triggered:</b> <span class="signal-result {'no' if not double_sell_triggered else ''}">{double_sell_triggered}</span>
                    </li>
                    <li class="signal-item">
                        <b>Last Sell Signal:</b> <span class="last-date">{double_last_sell}</span>
                    </li>
                </ul>
            </div>
            
            <div class="section">
                <h3>Leaning towards Buy OR Sell</h3>
                <p><b>{leaning_status}</b></p>
            </div>

            <div class="overall">
                <h2>EVWMA Signal Conclusion</h2>
                <p class="{overall_status}">
                    {overall_status.upper()}
                </p>
            </div>

        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    print(f">> ")
    print(f">> --------------------------------------------------------------------")
    print(f">> BEGIN Processing - Evaluate Price to EVWMA ...")
    print(f">> --------------------------------------------------------------------")
    print(f">> ")
    
    # Define the output directory and ensure it exists
    output_dir = "E:/_scripts_PYTHON/_personal/_OUTPUT"
    report_dir = "E:/_scripts_PYTHON/_personal/_REPORT"
    
    os.makedirs(output_dir, exist_ok=True)
    # print(f"Output directory '{output_dir}' checked/created.")
    
    os.makedirs(report_dir, exist_ok=True)
    # print(f"Report directory '{report_dir}' checked/created.")
    
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
        # print(f"Start date defaulted to: {start_date_str}")

    # Determine end_date based on input or default
    if end_date_input:
        end_date_str = end_date_input
    else:
        # Default to the current date
        end_date_str = datetime.now().strftime('%Y-%m-%d')
        # print(f"End date defaulted to: {end_date_str}")
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

    # CRITICAL CHANGE: Prefix with today's date and place in the correct directory.
    csv_file = os.path.join(output_dir, f"{today_date_str}_{ticker_symbol}_historical_data.csv")
    # print(f"Historical data will be saved to: {csv_file}")

    csv_file_name = download_historical_data(ticker_symbol, download_start_date_str, download_end_date_str, csv_file)
    
    if csv_file_name: # Proceed only if data was downloaded successfully
        df_indicators_from_csv = calculate_indicators_from_csv(csv_file_name)

        if df_indicators_from_csv is not None and not df_indicators_from_csv.empty:
            # Calculate and print Average Daily Volume
            # CRUCIAL FIX: Use lowercase 'volume'
            avg_volume = df_indicators_from_csv['volume'].mean()
            
            # print(f"\n>>  --- Average Daily Volume for this data: {avg_volume:,.0f} shares ---")
            # print(">>    Use this value to help adjust 'volume_span_short' and 'volume_span_long' for desired responsiveness.")
            # print(">>    e.g., A volume_span of 10x ADV will be for ~10 trading days.")
            # print(">>    Smaller volume_span values = more responsive EVWMA = more signals (and potentially more noise).")
            # print(">>    Larger volume_span values = smoother EVWMA = fewer signals (and potentially less noise).\n")

            # print(">>  --- Calculated Indicators from CSV (first 5 rows) ---")
            # print(df_indicators_from_csv.head())

            # print(">>  --- Calculated Indicators from CSV (last 5 rows) ---")
            # print(df_indicators_from_csv.tail())

            # CRITICAL CHANGE: Prefix with today's date and place in the correct directory.
            output_filename = os.path.join(output_dir, f"{today_date_str}_{ticker_symbol}_indicators_from_csv_output.csv")
            df_indicators_from_csv.to_csv(output_filename)
            # print(f">>  Indicators saved to {output_filename}")
            
            # --- NEW SIGNAL EVALUATION AND PRINTING SECTION ---
            print(f">> --------------------------------------------------------------------")
            print(f">>  EVWMA Reported Results - {ticker_symbol} ...")
            print(f">> --------------------------------------------------------------------")
            print(f">> ")
            single_buy_triggered, single_last_buy, single_sell_triggered, single_last_sell = evaluate_single_evwma_signals(df_indicators_from_csv)
            print(f">>  LEADING - Single EVWMA for Stock Ticker - {ticker_symbol}")
            print(f">>    Buy Signal Triggered - {single_buy_triggered}")
            print(f">>    Buy Signal Last Triggered - {single_last_buy}")
            print(f">>    Sell Signal Triggered - {single_sell_triggered}")
            print(f">>    Sell Signal Last Triggered - {single_last_sell}")
            print(f">> ")
            oscillator_buy_triggered, oscillator_last_buy, oscillator_sell_triggered, oscillator_last_sell = evaluate_oscillator_evwma_signals(df_indicators_from_csv)
            print(f">>  INBETWEEN - Evaluating Oscillator EVWMA for Stock Ticker - {ticker_symbol}")
            print(f">>    Buy Signal Triggered - {oscillator_buy_triggered}")
            print(f">>    Buy Signal Last Triggered - {oscillator_last_buy}")
            print(f">>    Sell Signal Triggered - {oscillator_sell_triggered}")
            print(f">>    Sell Signal Last Triggered - {oscillator_last_sell}")		
            print(f">> ")            
            double_buy_triggered, double_last_buy, double_sell_triggered, double_last_sell = evaluate_double_evwma_signals(df_indicators_from_csv)
            print(f">>  LAGGING - Double EVWMA Crossover for Stock Ticker - {ticker_symbol}")
            print(f">>    Buy Signal Triggered - {double_buy_triggered}")
            print(f">>    Buy Signal Last Triggered - {double_last_buy}")
            print(f">>    Sell Signal Triggered - {double_sell_triggered}")
            print(f">>    Sell Signal Last Triggered - {double_last_sell}")
            print(f">> ")

            # # #################################################################################
            # # Check for Leaning Buy Signal conditions
            # # #################################################################################
            # # Initialize the leaning signals to False
            # leaning_buy = False
            # leaning_sell = False
            # 
            # # Get the current date
            # current_date = date.today()
            # 
            # # Convert the string to a datetime object
            # single_last_buy_date_object = datetime.strptime(single_last_buy, '%Y-%m-%d')
            # oscillator_last_buy_date_object = datetime.strptime(oscillator_last_buy, '%Y-%m-%d')
            # 
            # single_last_sell_date_object = datetime.strptime(single_last_sell, '%Y-%m-%d')
            # oscillator_last_sell_date_object = datetime.strptime(oscillator_last_sell, '%Y-%m-%d')
            # 
            # # Convert the datetime object to a date object
            # single_last_buy_date = single_last_buy_date_object.date()
            # oscillator_last_buy_date = oscillator_last_buy_date_object.date()
            # 
            # single_last_sell_date = single_last_sell_date_object.date()
            # oscillator_last_sell_date = oscillator_last_sell_date_object.date()
            # 
            # # Condition 1: Check for leaning buy signal
            # buy_Condition = (single_last_buy_date - oscillator_last_buy_date).days
            # sell_Condition = (single_last_sell_date - oscillator_last_sell_date).days
            # 
            # # Calculate the time difference - Only considering 60 days out to be valuable data.
            # buy_Time_difference = current_date - single_last_buy_date
            # oscillator_Time_difference = current_date - oscillator_last_buy_date
            # 
            # # if (buy_Time_difference.days <= 60) and (oscillator_Time_difference.days <= 60):
            # #     if (buy_Condition < sell_Condition) and (single_last_buy_date > single_last_sell_date):
            # #         leaning_buy = True
            # # 
            # #     # Condition 2: Check for leaning sell signal
            # #     if (buy_Condition > sell_Condition) and (single_last_sell_date > single_last_buy_date):              
            # #         leaning_sell = True
            # # 
            # #     # Condition 3: Conflict resolution for leaning signals
            # #     if (buy_Condition == sell_Condition) or (single_last_buy_date == single_last_sell_date):
            # #         leaning_buy = False
            # #         leaning_sell = False
            # #
            # # Condition 1: Check same date variances
            # if single_last_buy_date == oscillator_last_buy_date:
            #     leaning_buy = True
            # elif single_last_sell_date == oscillator_last_sell_date:
            #     leaning_sell = True
            # elif (buy_Time_difference.days <= 60) and (oscillator_Time_difference.days <= 60):
            #     if (buy_Condition < sell_Condition) and (single_last_buy_date > single_last_sell_date):
            #         leaning_buy = True
            #     elif (buy_Condition > sell_Condition) and (single_last_sell_date > single_last_buy_date):
            #         leaning_sell = True
            #     else: # This covers the case where buy_Condition == sell_Condition or dates are the same
            #         leaning_buy = False
            #         leaning_sell = False
            # else:
            #     # All other cases, if you want to handle them
            #     leaning_buy = False
            #     leaning_sell = False
            # 
            # # #################################################################################
            # 
            # # #################################################################################
            # # Check for Overall Buy Signal conditions
            # # #################################################################################
            # # Initialize the overall signals to False
            # all_buy_currently_triggered = False
            # all_sell_currently_triggered = False
            # 
            # # Convert the string to a datetime object
            # double_last_buy_date_object = datetime.strptime(double_last_buy, '%Y-%m-%d')
            # double_last_sell_date_object = datetime.strptime(double_last_sell, '%Y-%m-%d')
            # 
            # # Convert the datetime object to a date object
            # double_last_buy_date = double_last_buy_date_object.date()
            # double_last_sell_date = double_last_sell_date_object.date()
            # 
            # # Condition 1: Check for overall buy signal
            # # An overall buy signal is triggered if a leaning buy signal is active AND
            # # the oscillator last buy date is within 15 days of the double last buy date.
            # overall_Buy_Condition = (double_last_buy_date - oscillator_last_buy_date).days
            # overall_Sell_Condition = (double_last_sell_date - oscillator_last_sell_date).days
            # 
            # if leaning_buy and (overall_Buy_Condition < overall_Sell_Condition) and (oscillator_last_buy_date > oscillator_last_sell_date):
            #     all_buy_currently_triggered = True
            # 
            # # Condition 2: Check for leaning sell signal
            # if leaning_sell and (overall_Buy_Condition > overall_Sell_Condition) and (oscillator_last_sell_date > oscillator_last_buy_date):              
            #     all_sell_currently_triggered = True
            # 
            # # Condition 3: Conflict resolution for leaning signals
            # if (overall_Buy_Condition == overall_Sell_Condition) or (oscillator_last_sell_date == oscillator_last_buy_date):
            #     all_buy_currently_triggered = False
            #     all_sell_currently_triggered = False
            #     
            # # #################################################################################
            # 

            # #################################################################################
            # Refactored Logic for Leaning and Overall Signals
            # #################################################################################
            leaning_buy = False
            leaning_sell = False
            all_buy_currently_triggered = False
            all_sell_currently_triggered = False
            
            today = date.today()

            try:
                single_buy_date_obj = datetime.strptime(single_last_buy, '%Y-%m-%d').date()
                oscillator_buy_date_obj = datetime.strptime(oscillator_last_buy, '%Y-%m-%d').date()
                single_sell_date_obj = datetime.strptime(single_last_sell, '%Y-%m-%d').date()
                oscillator_sell_date_obj = datetime.strptime(oscillator_last_sell, '%Y-%m-%d').date()
                
                double_buy_date_obj = datetime.strptime(double_last_buy, '%Y-%m-%d').date()
                double_sell_date_obj = datetime.strptime(double_last_sell, '%Y-%m-%d').date()

                # Calculate time differences in days
                single_buy_days_diff = (today - single_buy_date_obj).days
                oscillator_buy_days_diff = (today - oscillator_buy_date_obj).days
                single_sell_days_diff = (today - single_sell_date_obj).days
                oscillator_sell_days_diff = (today - oscillator_sell_date_obj).days
                double_buy_days_diff = (today - double_buy_date_obj).days
                double_sell_days_diff = (today - double_sell_date_obj).days

                # This should be Leaning Sell
                # CVX	    Buy: False (2025-09-10) Sell: False (2025-09-03)
                #           Buy: False (2025-08-21) Sell: False (2025-09-05)
                #           Buy: False (2025-06-06) Sell: False (2025-05-21)
                # 
                # This should be a Overall Sell
                # AMZN	    Buy: False (2025-09-08) Sell: False (2025-09-10)	
                #           Buy: False (2025-09-04) Sell: False (2025-09-10)
                #           Buy: False (2025-09-04) Sell: False (2025-09-10)
                # 
                # DIS	    Buy: False (2025-08-13) Sell: False (2025-09-09)	
                #           Buy: False (2025-08-18) Sell: False (2025-09-11)	
                #           Buy: False (2025-08-29) Sell: True (2025-09-12)

                # This should be Leaning Buy
                # JPM	 Buy: False (2025-09-09) Sell: False (2025-09-05)	
                #        Buy: False (2025-09-11) Sell: False (2025-09-08)
                #        Buy: False (2025-04-11) Sell: False (2025-04-03)
                # 
                # MMM	 Buy: False (2025-09-11) Sell: False (2025-09-09)	
                #        Buy: False (2025-09-11) Sell: False (2025-09-03)	
                #        Buy: False (2025-05-14) Sell: False (2025-04-04)
                # 
                # UNH	 Buy: False (2025-09-11) Sell: False (2025-09-09)
                #        Buy: False (2025-09-05) Sell: False (2025-08-26)
                #        Buy: False (2025-08-13) Sell: False (2025-07-09)
                # 
                # WMT	 Buy: False (2025-09-11) Sell: False (2025-09-10)
                #        Buy: False (2025-09-02) Sell: False (2025-08-13)
                #        Buy: False (2025-09-03) Sell: False (2025-08-21)

                # This should be an Overall Sell
                # NKE	 Buy: False (2025-08-22) Sell: False (2025-08-29)
                #        Buy: False (2025-08-13) Sell: False (2025-08-29)
                #        Buy: False (2025-08-13) Sell: False (2025-09-03)
                        
                # New Conditional Logic
                if (single_buy_days_diff <= 60 and oscillator_buy_days_diff <= 60 and single_sell_days_diff <= 60 and oscillator_sell_days_diff <= 60 and double_buy_days_diff <= 225 and double_sell_days_diff <= 225):
                    
                    # Buy conditions
                    if (single_buy_days_diff <= 30 and oscillator_buy_days_diff <= 30 and double_buy_days_diff <= 15):
                        if single_buy_date_obj == oscillator_buy_date_obj and oscillator_buy_date_obj == double_buy_date_obj:
                            all_buy_currently_triggered = True
                        elif (oscillator_buy_date_obj > single_buy_date_obj) and (double_buy_date_obj == oscillator_buy_date_obj):
                            all_buy_currently_triggered = True                                    
                        elif (oscillator_buy_date_obj > single_buy_date_obj) and (double_buy_date_obj > oscillator_buy_date_obj) and (double_buy_date_obj > double_sell_date_obj):
                            all_buy_currently_triggered = True
                        elif (single_buy_date_obj == oscillator_buy_date_obj) and (oscillator_buy_date_obj > double_buy_date_obj):
                            leaning_buy = True
                        elif (oscillator_buy_date_obj > single_buy_date_obj) and (oscillator_buy_date_obj > double_buy_date_obj):
                            leaning_buy = True
                        elif (oscillator_buy_date_obj < single_buy_date_obj) and (oscillator_buy_date_obj < double_buy_date_obj) and (single_buy_date_obj > single_sell_date_obj) and (oscillator_buy_date_obj > oscillator_sell_date_obj) and (double_buy_date_obj > double_sell_date_obj):
                            leaning_buy = True
                        elif (single_sell_date_obj > single_buy_date_obj) and (oscillator_sell_date_obj > oscillator_buy_date_obj) and (double_sell_date_obj > double_buy_date_obj):
                            all_sell_currently_triggered = True
                            
                    # Sell conditions
                    elif (single_sell_days_diff <= 30 and oscillator_sell_days_diff <= 30 and double_sell_days_diff <= 15):
                        if single_sell_date_obj == oscillator_sell_date_obj and oscillator_sell_date_obj == double_sell_date_obj:
                            all_sell_currently_triggered = True
                        elif (oscillator_sell_date_obj > single_sell_date_obj) and (double_sell_date_obj == oscillator_sell_date_obj):
                            all_sell_currently_triggered = True                                     
                        elif (oscillator_sell_date_obj > single_sell_date_obj) and (double_sell_date_obj > oscillator_sell_date_obj) and (double_sell_date_obj > double_buy_date_obj):
                            all_sell_currently_triggered = True
                        elif (single_sell_date_obj > single_buy_date_obj) and (oscillator_sell_date_obj > oscillator_buy_date_obj) and (double_sell_date_obj > double_buy_date_obj):
                            all_sell_currently_triggered = True  
                        elif (single_sell_date_obj == oscillator_sell_date_obj) and (oscillator_sell_date_obj > double_sell_date_obj):
                            leaning_sell = True
                        elif (oscillator_sell_date_obj > single_sell_date_obj) and (oscillator_sell_date_obj > double_sell_date_obj):
                            leaning_sell = True
                            
                    # Mixed conditions
                    elif (single_buy_days_diff <= 30 and oscillator_buy_days_diff <= 30 and (double_buy_days_diff >= 30 and double_buy_days_diff <= 225)):
                        if (single_buy_date_obj > single_sell_date_obj) and (oscillator_buy_date_obj > oscillator_sell_date_obj) and (double_buy_date_obj > double_sell_date_obj):
                            leaning_buy = True
                        elif (single_buy_date_obj > single_sell_date_obj) and (oscillator_buy_date_obj < oscillator_sell_date_obj) and (double_buy_date_obj > double_sell_date_obj):
                            leaning_sell = True                         
                    elif (single_sell_days_diff <= 30 and oscillator_sell_days_diff <= 30 and (double_sell_days_diff >= 30 and double_sell_days_diff <= 225)):
                        if (single_sell_date_obj < single_buy_date_obj) and (oscillator_sell_date_obj > oscillator_buy_date_obj) and (double_buy_date_obj > double_sell_date_obj):
                            leaning_sell = True                                
                            
            except ValueError:
                print(f"Warning: Could not parse date for {ticker_symbol}. Signal evaluation skipped.")

            # #################################################################################
            
            print(f">> --------------------------------------------------------------------")
            print(f">>  Reported Conclusion - {ticker_symbol} ...")
            print(f">> --------------------------------------------------------------------")
            print(f">> ")
            
            # 
            # leaning_status = ""
            # if leaning_buy:
            #     leaning_status = f">>    LEANING - EVWMA FORECAST - BUY Signals within last 33 Days !!! "
            # elif leaning_sell:
            #     leaning_status = f">>    LEANING - EVWMA FORECAST - SELL Signals within last 33 Days !!! "
            # else:
            #     leaning_status = f">>    LEANING - EVWMA FORECAST - NOT enough evidence to draw a conclusion !!! "
            #     
            # print(leaning_status)
            # 
            # overall_status = ""
            # if all_buy_currently_triggered:
            #     overall_status = f">>    OVERALL - EVWMA FORECAST - BUY Signal Triggered !!!"
            # elif all_sell_currently_triggered:
            #     overall_status = f">>    OVERALL - EVWMA FORECAST - SELL Signal Triggered !!!"
            # else:
            #     overall_status = f">>    OVERALL - EVWMA FORECAST - NOT enough evidence to draw a conclusion !!!"
            # 
            # print(overall_status)
            
            leaning_status = "Undetermined"
            overall_status = "Overall Undetermined"
            
            if all_buy_currently_triggered:
                overall_status = f">>    OVERALL - EVWMA FORECAST - BUY Signal Triggered !!!"
                print(f">>    OVERALL - EVWMA FORECAST - BUY Signal Triggered !!!")
            elif all_sell_currently_triggered:
                overall_status = f">>    OVERALL - EVWMA FORECAST - SELL Signal Triggered !!!"
                print(f">>    OVERALL - EVWMA FORECAST - SELL Signal Triggered !!!")
            elif leaning_buy:
                leaning_status = f">>    LEANING - EVWMA FORECAST - BUY Signals within last 33 Days !!! "
                print(f">>    LEANING - EVWMA FORECAST - BUY Signals within last 33 Days !!! ")
            elif leaning_sell:
                leaning_status = f">>    LEANING - EVWMA FORECAST - SELL Signals within last 33 Days !!! "
                print(f">>    LEANING - EVWMA FORECAST - SELL Signals within last 33 Days !!! ")
            else:
                overall_status = f">>    OVERALL - EVWMA FORECAST - NOT enough evidence to draw a conclusion !!!"
                leaning_status = f">>    LEANING - EVWMA FORECAST - NOT enough evidence to draw a conclusion !!! "
                print(f">>    UNDETERMINED - EVWMA FORECAST - NOT enough evidence to draw a conclusion !!!")
                        
            # Generate and save the HTML report
            html_report_content = generate_html_report(
                ticker_symbol,
                (single_buy_triggered, single_last_buy, single_sell_triggered, single_last_sell),
                (double_buy_triggered, double_last_buy, double_sell_triggered, double_last_sell),
                (oscillator_buy_triggered, oscillator_last_buy, oscillator_sell_triggered, oscillator_last_sell),
                leaning_status,
                overall_status
            )
            
            # Get today's date in YYYYMMDD format
            today_date_str = datetime.now().strftime('%Y%m%d')
            
            output_filename = f"{ticker_symbol}_price2EVWMA_Report.html"
        
            html_file_path = os.path.join(report_dir, f"{today_date_str}_{output_filename}")
            try:
                with open(html_file_path, 'w') as f:
                    f.write(html_report_content)
                print(f">>    !!! Successfully generated HTML report at:\n {html_file_path}")
            except Exception as e:
                print(f"Error writing HTML report: {e}")                               
        else:
            print(">>  Failed to calculate indicators from CSV.")
    else:
        print(">>  Data download failed, unable to proceed with indicator calculation and charting.")
        
    print(f">> ")  
    print(f">> --------------------------------------------------------------------")    
    print(f">> END Processing - Evaluate Price to EVWMA for - {ticker_symbol} ...")
    print(f">> --------------------------------------------------------------------")
    print(f">> ")