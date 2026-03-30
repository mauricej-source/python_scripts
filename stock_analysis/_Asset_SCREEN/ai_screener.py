import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# --- 1. Define Dual Screening Criteria ---

# Conservative Screen: Focus on Quality, Value, and Stability
CONSERVATIVE_CRITERIA = {
    '1Y_MOMENTUM_MIN': 0.15,      # Solid long-term return (Min 15%)
    'BETA_MAX': 1.25,             # Lower volatility (Max 1.25)
    'PRICE_TO_EARNINGS_MAX': 30,  # Value/Quality (Max 30 P/E)
    'RETURN_ON_EQUITY_MIN': 0.10, # Quality/Profitability (Min 10% ROE)
}

# Speculative Screen: Focus on High Short-Term Momentum and Volatility
SPECULATIVE_CRITERIA = {
    '1M_MOMENTUM_MIN': 0.10,     # Strong 1-Month Price Change (Min 10%)
    '1W_MOMENTUM_MIN': 0.05,     # Strong 1-Week Price Change (Min 5%)
    'PRICE_TO_BOOK_MIN': 1.0,    # Growth/Speculation (Min 1.0 P/B)
    'ATR_MIN': 1.00,             # High Average True Range (Min $1.00) - VOLATILITY FILTER
    'RSI_MIN': 60.0              # High Relative Strength Index (Min 60) - MOMENTUM FILTER
}

# --- 2. Define the Stock List (AI-Related Tickers) ---
TICKER_LIST = ["ANGO","STLA","NMAX","GPRK","GTLB","XPEV","BROS","BMRN","LI","COCP","INSE","TSQ","NIO","HNI","AVNT","WWW","IBRX","HBAN","KD","BIP","GBCI","KDP","BCS"] # Expanded list for better comparison

# --- 3. Core Technical and Fundamental Data Functions ---

def get_technical_data(ticker, period_days):
    """Pulls historical data and calculates momentum, ATR, and Beta."""
    end_date = datetime.today()
    start_date_long = end_date - timedelta(days=380) # For 1Y momentum and Beta
    start_date_short = end_date - timedelta(days=period_days + 5)
    
    try:
        # Long-term data for 1Y Momentum and Beta
        long_data = yf.Ticker(ticker).history(start=start_date_long, end=end_date, interval="1d")
        
        # 1-Year Momentum
        if len(long_data) >= 252:
            mom_1y = (long_data['Close'].iloc[-1] - long_data['Close'].iloc[0]) / long_data['Close'].iloc[0]
        else:
            mom_1y = None

        # Beta (requires market data, using S&P 500 as benchmark)
        beta = yf.Ticker(ticker).info.get('beta')
        
        # Short-term data for ATR, 1W/1M Momentum
        short_data = yf.Ticker(ticker).history(start=start_date_short, end=end_date, interval="1d")
        
        # Momentum for the specified short period
        mom_short = None
        if not short_data.empty and len(short_data) >= 2:
            mom_short = (short_data['Close'].iloc[-1] - short_data['Close'].iloc[0]) / short_data['Close'].iloc[0]

        # Calculate True Range (TR) and Average True Range (ATR)
        if not long_data.empty:
            long_data['TR1'] = long_data['High'] - long_data['Low']
            long_data['TR2'] = abs(long_data['High'] - long_data['Close'].shift(1))
            long_data['TR3'] = abs(long_data['Low'] - long_data['Close'].shift(1))
            long_data['TR'] = long_data[['TR1', 'TR2', 'TR3']].max(axis=1)
            atr = long_data['TR'].iloc[-14:].mean() if len(long_data) >= 14 else long_data['TR'].mean()
        else:
            atr = None
            
        return {'1Y_MOMENTUM': mom_1y, 'BETA': beta, 'MOMENTUM_SHORT': mom_short, 'ATR': atr}

    except Exception:
        return {'1Y_MOMENTUM': None, 'BETA': None, 'MOMENTUM_SHORT': None, 'ATR': None}


def get_rsi(ticker):
    """Calculates a simple 14-day RSI."""
    end_date = datetime.today()
    start_date = end_date - timedelta(days=40)
    
    try:
        data = yf.Ticker(ticker).history(start=start_date, end=end_date, interval="1d")['Close']
        if data.empty or len(data) < 28:
            return None

        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]

    except Exception:
        return None

def get_fundamentals(ticker):
    """Pulls fundamental data (P/E, P/B, ROE) from yfinance Ticker object."""
    try:
        info = yf.Ticker(ticker).info
        p_e = info.get('trailingPE')
        p_b = info.get('priceToBook')
        roe = info.get('returnOnEquity')
        return {
            'PRICE_TO_EARNINGS': p_e, 
            'PRICE_TO_BOOK': p_b, 
            'RETURN_ON_EQUITY': roe
        }
    except Exception:
        return {
            'PRICE_TO_EARNINGS': None, 
            'PRICE_TO_BOOK': None, 
            'RETURN_ON_EQUITY': None
        }

# ----------------------------------------------------------------------
# --- 4. Main Screener Logic ---
# ----------------------------------------------------------------------

def run_dual_screener(tickers, conservative_criteria, speculative_criteria):
    
    # --- 4a. Fetch All Raw Data First ---
    raw_data = {}
    for ticker in tickers:
        tech_30 = get_technical_data(ticker, 30)
        tech_7 = get_technical_data(ticker, 7)
        
        raw_data[ticker] = {
            '1Y_MOMENTUM': tech_30['1Y_MOMENTUM'],
            '1M_MOMENTUM': tech_30['MOMENTUM_SHORT'],
            '1W_MOMENTUM': tech_7['MOMENTUM_SHORT'],
            'ATR': tech_30['ATR'],
            'BETA': tech_30['BETA'],
            'RSI': get_rsi(ticker),
            **get_fundamentals(ticker)
        }

    # --- 4b. Conservative Screen Evaluation ---
    conservative_passes = {}
    for ticker, data in raw_data.items():
        pass_fail = {}
        
        # 1Y Momentum Check
        mom_1y_val = data['1Y_MOMENTUM']
        pass_fail['1Y_MOMENTUM'] = (mom_1y_val is not None) and (mom_1y_val >= conservative_criteria['1Y_MOMENTUM_MIN'])

        # Beta Check (Low Volatility)
        beta_val = data['BETA']
        pass_fail['BETA'] = (beta_val is not None) and (beta_val <= conservative_criteria['BETA_MAX'])

        # P/E Check (Value/Quality)
        pe_val = data['PRICE_TO_EARNINGS']
        pass_fail['PRICE_TO_EARNINGS'] = (pe_val is not None) and (pe_val <= conservative_criteria['PRICE_TO_EARNINGS_MAX'])

        # ROE Check (Profitability/Quality)
        roe_val = data['RETURN_ON_EQUITY']
        pass_fail['RETURN_ON_EQUITY'] = (roe_val is not None) and (roe_val >= conservative_criteria['RETURN_ON_EQUITY_MIN'])

        total_passes = sum(pass_fail.values())
        if total_passes == len(conservative_criteria):
            conservative_passes[ticker] = {'metrics': data, 'pass_fail': pass_fail, 'total_passes': total_passes}

    # --- 4c. Speculative Screen Evaluation ---
    speculative_passes = {}
    for ticker, data in raw_data.items():
        pass_fail = {}

        # 1M Momentum Check
        m1_val = data['1M_MOMENTUM']
        pass_fail['1M_MOMENTUM'] = (m1_val is not None) and (m1_val >= speculative_criteria['1M_MOMENTUM_MIN'])

        # 1W Momentum Check
        m1w_val = data['1W_MOMENTUM']
        pass_fail['1W_MOMENTUM'] = (m1w_val is not None) and (m1w_val >= speculative_criteria['1W_MOMENTUM_MIN'])

        # ATR Check (High Volatility)
        atr_val = data['ATR']
        pass_fail['ATR'] = (atr_val is not None) and (atr_val >= speculative_criteria['ATR_MIN'])

        # RSI Check (Strong Momentum)
        rsi_val = data['RSI']
        pass_fail['RSI'] = (rsi_val is not None) and (rsi_val >= speculative_criteria['RSI_MIN'])

        # P/B Check (Growth/Speculation)
        pb_val = data['PRICE_TO_BOOK']
        pass_fail['PRICE_TO_BOOK'] = (pb_val is not None) and (pb_val >= speculative_criteria['PRICE_TO_BOOK_MIN'])
        
        total_passes = sum(pass_fail.values())
        if total_passes == len(speculative_criteria):
            speculative_passes[ticker] = {'metrics': data, 'pass_fail': pass_fail, 'total_passes': total_passes}


    # --- 5. Display Results ---

    def format_output(results, criteria, title, emoji):
        print("\n" + emoji * 70)
        print(f"--- {title} ---")
        
        if title.startswith("CONSERVATIVE"):
             print(f"      Criteria: 1Y Mom > {criteria['1Y_MOMENTUM_MIN']:.0%}, Beta < {criteria['BETA_MAX']:.2f}, P/E < {criteria['PRICE_TO_EARNINGS_MAX']:.0f}, ROE > {criteria['RETURN_ON_EQUITY_MIN']:.0%}")
        else:
             print(f"      Criteria: 1M Mom > {criteria['1M_MOMENTUM_MIN']:.0%}, 1W Mom > {criteria['1W_MOMENTUM_MIN']:.0%}, ATR > ${criteria['ATR_MIN']:.2f}, RSI > {criteria['RSI_MIN']:.0f}, P/B > {criteria['PRICE_TO_BOOK_MIN']:.1f}")

        print(emoji * 70)
        
        if not results:
            print("❌ NO STOCKS PASSED THIS SCREEN.")
            return

        for ticker, result_data in results.items():
            metrics = result_data['metrics']
            pass_fail = result_data['pass_fail']

            print(f" ")
            print(f"  --- Ticker: {ticker} (✅ PASSED ALL {len(criteria)} CRITERIA) ---")
            
            for metric_key, passed in pass_fail.items():
                value = metrics.get(metric_key)
                
                if value is None:
                    value_str = "N/A (Data Err)"
                elif 'MOMENTUM' in metric_key:
                    value_str = f"{value:.2%}"
                elif metric_key == 'ATR':
                    value_str = f"${value:.2f}"
                elif metric_key == 'RSI':
                    value_str = f"{value:.1f}"
                elif metric_key == 'BETA' or metric_key == 'RETURN_ON_EQUITY' or metric_key == 'PRICE_TO_BOOK':
                    value_str = f"{value:.2f}"
                elif metric_key == 'PRICE_TO_EARNINGS':
                    value_str = f"{value:.1f}"
                else:
                    value_str = str(value)

                print(f"  {metric_key:<20} | Value: {value_str:<10} | Result: ✅ PASS")
            print("  " + "-" * 30)

    # Display Conservative first, then Speculative
    format_output(conservative_passes, CONSERVATIVE_CRITERIA, "CONSERVATIVE AI SCREEN (Value/Quality Focus)", "#️")
    print("=" * 70) # Separator for clear distinction
    format_output(speculative_passes, SPECULATIVE_CRITERIA, "SPECULATIVE AI SCREEN (Volatility/Momentum Focus)", "#")


# --- 6. Execute the Script ---
if __name__ == "__main__":
    print(f"BEGINNING DUAL SCREENING PROCESS for {len(TICKER_LIST)} Tickers...")
    run_dual_screener(TICKER_LIST, CONSERVATIVE_CRITERIA, SPECULATIVE_CRITERIA)