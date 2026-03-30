import yfinance as yf
import statistics
import sys
import math

# ==============================================================================
# 📈 STRATEGY PARAMETERS
# ==============================================================================

# Lookback period for standard Bollinger Bands (Mean and Standard Deviation)
LOOKBACK_PERIOD = 10 
STD_DEV = 2           # Standard deviation multiplier
VOLATILITY_THRESHOLD = 0.8 # Squeeze trigger: B_WIDTH must be below (B_WIDTH_AVG * 0.8)

# Lookback period for the long-term volatility average (Bandwidth Average)
B_WIDTH_AVG_PERIOD = 30 # Reduced from 100 for better data availability

# ==============================================================================
# ⚙️ HELPER FUNCTIONS (PURE PYTHON)
# ==============================================================================

def calculate_sma(data, window):
    """Calculates Simple Moving Average (SMA) for a list of closing prices.
    Includes robust filtering for non-numeric types."""
    
    if len(data) < window:
        return None

    recent_data_slice = data[-window:]
    
    # CRITICAL FIX: Ensure all elements are clean floats and filter out bad data.
    numeric_data = [float(x) for x in recent_data_slice if isinstance(x, (int, float))]
    
    if len(numeric_data) < window:
        # Prevents summing if data was filtered out
        return None

    return sum(numeric_data) / window


def calculate_stdev(data, window):
    """Calculates Standard Deviation for a list of closing prices.
    Includes robust filtering for non-numeric types."""
    
    if len(data) < window:
        return None
        
    recent_data_slice = data[-window:]
    
    # CRITICAL FIX: Ensure all elements are clean floats and filter out bad data.
    numeric_data = [float(x) for x in recent_data_slice if isinstance(x, (int, float))]
    
    if len(numeric_data) < window:
        return None

    # Use the built-in statistics module for robust standard deviation
    return statistics.stdev(numeric_data)

# ------------------------------------------------------------------------------

def get_stock_data(ticker, period='max'):
    """Fetches historical stock data from yfinance and returns a list of closing prices."""
    print(f"Fetching data for {ticker}...")
    
    try:
        # Fetch data using the specified period (default 'max')
        data = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        if data.empty:
            print(f"Error: Could not find data for ticker symbol '{ticker}'.")
            sys.exit(1)
            
        print(data)
        # FIX: Ensure 'Close' is extracted as a simple Python list of floats
        return data['Close'].values.tolist()
            
    except Exception as e:
        print(f"An error occurred while downloading data: {e}")
        sys.exit(1)

# ==============================================================================
# 🧠 CORE TRADING LOGIC
# ==============================================================================

#def analyze_boom_bust_cycle(closes, ticker):
#    """Calculates indicators and generates trading signals using pure Python lists."""
#    
#    signals = []
#    b_widths = []
#    
#    # FIX: Initialize B_WIDTH_AVG as an empty list to match the length of `closes`
#    b_width_avgs = [] 
#    upper_bands = []
#    lower_bands = []
#
#    # Iterate through the prices, maintaining a history list
#    for i in range(len(closes)):
#        current_closes = closes[:i+1]
#        
#        # 1. Calculate Bands
#        sma = calculate_sma(current_closes, LOOKBACK_PERIOD)
#        stdev = calculate_stdev(current_closes, LOOKBACK_PERIOD)
#        
#        current_b_width = None
#        current_upper = None
#        current_lower = None
#
#        if sma is not None and stdev is not None:
#            current_upper = sma + (stdev * STD_DEV)
#            current_lower = sma - (stdev * STD_DEV)
#            # Bollinger Bandwidth
#            current_b_width = (current_upper - current_lower) / sma
#        
#        upper_bands.append(current_upper)
#        lower_bands.append(current_lower)
#        b_widths.append(current_b_width)
#
#        # 2. Calculate Bandwidth Average (Long-term volatility)
#        current_b_width_avg = None
#        
#        if i >= B_WIDTH_AVG_PERIOD - 1:
#            # Get the recent window of B_WIDTH values
#            recent_b_widths = [bw for bw in b_widths if bw is not None][-B_WIDTH_AVG_PERIOD:]
#            
#            if len(recent_b_widths) == B_WIDTH_AVG_PERIOD:
#                current_b_width_avg = sum(recent_b_widths) / B_WIDTH_AVG_PERIOD
#        
#        b_width_avgs.append(current_b_width_avg)
#        
#        # --- Signal Generation ---
#        signal = 0
#
#        # We need data from yesterday (i-1) to generate today's signal (i)
#        if i > 0 and lower_bands[i-1] is not None and b_width_avgs[i-1] is not None:
#            
#            close_yesterday = closes[i-1]
#            bbl_yesterday = lower_bands[i-1]
#            bbu_yesterday = upper_bands[i-1]
#            bw_yesterday = b_widths[i-1]
#            bw_avg_yesterday = b_width_avgs[i-1]
#            
#            # 1. ACCUMULATION (Buy the Base/Bust)
#            # Must meet Squeeze AND Oversold
#            squeeze_condition = bw_yesterday < (bw_avg_yesterday * VOLATILITY_THRESHOLD)
#            oversold_condition = close_yesterday <= bbl_yesterday
#            
#            if squeeze_condition and oversold_condition:
#                signal = 1
#                
#            # 2. SELL/EXIT (Profit-Take/Boom)
#            overbought_condition = close_yesterday >= bbu_yesterday
#            
#            if overbought_condition:
#                signal = -1
#                
#        signals.append(signal)
#
#    # --- Output Assembly ---
#    results = []
#    
#    # FIX: Ensure all lists are aligned and have the same length for zipping.
#    # b_width_avgs is now the same length as closes, so no slicing is needed.
#    for c, u, l, bw, bwa, s in zip(closes, upper_bands, lower_bands, b_widths, b_width_avgs, signals):
#        results.append({
#            'Close': c,
#            'BBU': u,
#            'BBL': l,
#            'B_WIDTH': bw,
#            'B_WIDTH_AVG': bwa,
#            'Signal': s
#        })
#
#    # Filter out initial None values where the B_WIDTH_AVG could not be calculated
#    results = [r for r in results if r['B_WIDTH_AVG'] is not None]
#
#    return results

#def analyze_boom_bust_cycle(closes, ticker):
#    """Calculates indicators and generates trading signals using pure Python lists."""
#    
#    signals = []
#    
#    # Lists to store calculated indicator values
#    b_widths = []
#    # FIX: Initialize B_WIDTH_AVG as an empty list to align with the length of `closes`
#    b_width_avgs = [] 
#    upper_bands = []
#    lower_bands = []
#
#    # Iterate through the prices, maintaining a history list
#    for i in range(len(closes)):
#        current_closes = closes[:i+1]
#        
#        # 1. Calculate Bands
#        sma = calculate_sma(current_closes, LOOKBACK_PERIOD)
#        stdev = calculate_stdev(current_closes, LOOKBACK_PERIOD)
#        
#        current_b_width = None
#        current_upper = None
#        current_lower = None
#
#        if sma is not None and stdev is not None:
#            current_upper = sma + (stdev * STD_DEV)
#            current_lower = sma - (stdev * STD_DEV)
#            current_b_width = (current_upper - current_lower) / sma
#        
#        upper_bands.append(current_upper)
#        lower_bands.append(current_lower)
#        b_widths.append(current_b_width)
#
#        # 2. Calculate Bandwidth Average (B_WIDTH_AVG_PERIOD simple moving average of B_WIDTH)
#        current_b_width_avg = None
#        
#        # Check if enough B_WIDTH history is available (30 days)
#        if i >= B_WIDTH_AVG_PERIOD - 1:
#            # Get the recent window of B_WIDTH values
#            recent_b_widths = [bw for bw in b_widths if bw is not None][-B_WIDTH_AVG_PERIOD:]
#            
#            if len(recent_b_widths) == B_WIDTH_AVG_PERIOD:
#                current_b_width_avg = sum(recent_b_widths) / B_WIDTH_AVG_PERIOD
#        
#        b_width_avgs.append(current_b_width_avg)
#        
#        # --- Signal Generation ---
#        signal = 0
#
#        # FIX: Critical Lagging Check
#        # The signal should only be calculated once the lagged BWA (BWA from yesterday) exists.
#        # This occurs starting on the B_WIDTH_AVG_PERIOD day (i = 30, index 29).
#        if i >= B_WIDTH_AVG_PERIOD: 
#            
#            # All required lagged values are at index i-1
#            close_yesterday = closes[i-1]
#            bbl_yesterday = lower_bands[i-1]
#            bbu_yesterday = upper_bands[i-1]
#            bw_yesterday = b_widths[i-1]
#            bw_avg_yesterday = b_width_avgs[i-1] # BWA from yesterday is guaranteed not None
#            
#            # The BWA and BBL from yesterday are guaranteed to be calculated due to the 'if i >= B_WIDTH_AVG_PERIOD' check
#
#            # 1. Accumulation (Buy) Condition (Squeeze AND Oversold)
#            
#            # Condition 1: Low Volatility (Squeeze)
#            squeeze_condition = bw_yesterday < (bw_avg_yesterday * VOLATILITY_THRESHOLD)
#            
#            # Condition 2: Price hits oversold level (Lower Band)
#            oversold_condition = close_yesterday <= bbl_yesterday
#            
#            if squeeze_condition and oversold_condition:
#                signal = 1
#                
#            # 2. Sell/Exit Condition (Overbought)
#            overbought_condition = close_yesterday >= bbu_yesterday
#            
#            if overbought_condition:
#                signal = -1
#                
#        signals.append(signal)
#
#    # --- Output Assembly ---
#    results = []
#    
#    # FIX: Remove the slice [1:] on b_width_avgs, as it's now properly aligned
#    for c, u, l, bw, bwa, s in zip(closes, upper_bands, lower_bands, b_widths, b_width_avgs, signals):
#        results.append({
#            'Close': c,
#            'BBU': u,
#            'BBL': l,
#            'B_WIDTH': bw,
#            'B_WIDTH_AVG': bwa,
#            'Signal': s
#        })
#
#    # Filter out initial None values where the B_WIDTH_AVG could not be calculated
#    results = [r for r in results if r['B_WIDTH_AVG'] is not None]
#
#    return results
    
def analyze_boom_bust_cycle(closes, ticker):
    """Calculates indicators and generates trading signals using pure Python lists."""
    
    signals = []
    
    # Lists to store calculated indicator values
    b_widths = []
    # FIX: Initialize B_WIDTH_AVG as an empty list to align with the length of `closes`
    b_width_avgs = [] 
    upper_bands = []
    lower_bands = []

    # Iterate through the prices, maintaining a history list
    for i in range(len(closes)):
        current_closes = closes[:i+1]
        
        # 1. Calculate Bands
        sma = calculate_sma(current_closes, LOOKBACK_PERIOD)
        stdev = calculate_stdev(current_closes, LOOKBACK_PERIOD)
        
        current_b_width = None
        current_upper = None
        current_lower = None

        if sma is not None and stdev is not None:
            current_upper = sma + (stdev * STD_DEV)
            current_lower = sma - (stdev * STD_DEV)
            # Bollinger Bandwidth
            current_b_width = (current_upper - current_lower) / sma
            
            # 🟢 FINAL FLOAT FIX: Use math.isfinite() to explicitly handle NaN or Infinity
            if not math.isfinite(current_b_width):
                current_b_width = None # Discard if non-finite (NaN or +/- inf)
                
        upper_bands.append(current_upper)
        lower_bands.append(current_lower)
        b_widths.append(current_b_width)

        # 2. Calculate Bandwidth Average (B_WIDTH_AVG_PERIOD simple moving average of B_WIDTH)
        current_b_width_avg = None
        
        # Check if enough B_WIDTH history is available (30 days)
        if i >= B_WIDTH_AVG_PERIOD - 1:
            # Get the recent window of B_WIDTH values
            recent_b_widths = [bw for bw in b_widths if bw is not None][-B_WIDTH_AVG_PERIOD:]
            
            if len(recent_b_widths) == B_WIDTH_AVG_PERIOD:
                current_b_width_avg = sum(recent_b_widths) / B_WIDTH_AVG_PERIOD
        
        b_width_avgs.append(current_b_width_avg)
        
        # --- Signal Generation ---
        signal = 0

        # FIX: Critical Lagging Check
        # The signal should only be calculated once the lagged BWA (BWA from yesterday) exists,
        # which is guaranteed when i >= B_WIDTH_AVG_PERIOD (30).
        if i >= B_WIDTH_AVG_PERIOD: 
            
            # All required lagged values are at index i-1
            close_yesterday = closes[i-1]
            bbl_yesterday = lower_bands[i-1]
            bbu_yesterday = upper_bands[i-1]
            bw_yesterday = b_widths[i-1]
            bw_avg_yesterday = b_width_avgs[i-1] 
            
            # FINAL BUG FIX: Explicitly check for None on all key indicators to prevent the TypeError
            if (bw_avg_yesterday is not None and 
                bw_yesterday is not None and 
                bbl_yesterday is not None and 
                bbu_yesterday is not None):
                
                # 1. Accumulation (Buy) Condition (Squeeze AND Oversold)
                
                # Condition 1: Low Volatility (Squeeze)
                squeeze_condition = bw_yesterday < (bw_avg_yesterday * VOLATILITY_THRESHOLD)
                
                # Condition 2: Price hits oversold level (Lower Band)
                oversold_condition = close_yesterday <= bbl_yesterday
                
                if squeeze_condition and oversold_condition:
                    signal = 1
                    
                # 2. Sell/Exit Condition (Overbought)
                overbought_condition = close_yesterday >= bbu_yesterday
                
                if overbought_condition:
                    signal = -1
                
        signals.append(signal)

    # --- Output Assembly ---
    results = []
    
    # FIX: Remove the slice [1:] on b_width_avgs, as it's now properly aligned
    for c, u, l, bw, bwa, s in zip(closes, upper_bands, lower_bands, b_widths, b_width_avgs, signals):
        results.append({
            'Close': c,
            'BBU': u,
            'BBL': l,
            'B_WIDTH': bw,
            'B_WIDTH_AVG': bwa,
            'Signal': s
        })

    # Filter out initial None values where the B_WIDTH_AVG could not be calculated (first 30 days)
    results = [r for r in results if r['B_WIDTH_AVG'] is not None]

    return results
    
# ==============================================================================
# 🚀 EXECUTION AND OUTPUT
# ==============================================================================

if __name__ == '__main__':
    
    TICKER = input("Enter the stock ticker symbol (e.g., TSLA, AAPL, SPY): ").upper()

    # 1. Get data (using 'max' to ensure sufficient history for B_WIDTH_AVG)
    stock_closes = get_stock_data(TICKER, period='max') 

    # 2. Analyze data
    analyzed_data = analyze_boom_bust_cycle(stock_closes, TICKER)

    # --- Output Summary ---
    print(f"\n--- {TICKER} Boom-Bust Cycle Trading Signals (Last 10 Days) ---")

    # Critical check: Ensure valid data exists
    #if not analyzed_data:
    #    print("\n⚠️ **ERROR:** The indicator calculation produced no valid signals after filtering. Check data quality or increase the B_WIDTH_AVG_PERIOD.")
    #    sys.exit(0)

    # Print the last 10 entries cleanly (This is where the script should jump to)
    print(f"{'Close':<10} {'BBU':<10} {'BBL':<10} {'B_WIDTH':<10} {'B_W_AVG':<10} {'Signal':<10}")
    print("-" * 60)
    for entry in analyzed_data[-10:]:
        # Ensure all printed values are not None before formatting
        print(
            f"{entry['Close']:<10.2f} "
            f"{entry['BBU']:<10.2f} "
            f"{entry['BBL']:<10.2f} "
            f"{entry['B_WIDTH']:<10.4f} "
            f"{entry['B_WIDTH_AVG']:<10.4f} "
            f"{entry['Signal']:<10}"
        )

    print("\n--- Trading Interpretation ---")
    last_entry = analyzed_data[-1]
    last_signal = last_entry['Signal']
    last_close = last_entry['Close']

    if last_signal == 1:
        print(f"**ACCUMULATE SIGNAL:** Price touched the Lower Band during a volatility 'Squeeze'.")
        print(f"Current Close: **${last_close:.2f}**. This suggests the **'Bust'** phase is near its end.")
    elif last_signal == -1:
        print(f"**SELL/EXIT SIGNAL:** Price touched the Upper Band, indicating **'Boom'** exhaustion.")
        print(f"Current Close: **${last_close:.2f}**. Consider locking in profits.")
    else:
        print(f"HOLD/WAIT: No high-conviction signal on the last day. Current Close: **${last_close:.2f}**.")
        print("Price is likely consolidating within the Bollinger Bands.")