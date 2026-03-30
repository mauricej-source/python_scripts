import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os 

# --- 1. Define Dual Screening Criteria (GLOBAL CONSTANTS) ---
CONSERVATIVE_CRITERIA = {
    '1Y_MOMENTUM_MIN': 0.15,
    'BETA_MAX': 1.25,
    'PRICE_TO_EARNINGS_MAX': 30,
    'RETURN_ON_EQUITY_MIN': 0.10,
}
SPECULATIVE_CRITERIA = {
    '1M_MOMENTUM_MIN': 0.10,
    '1W_MOMENTUM_MIN': 0.05,
    'PRICE_TO_BOOK_MIN': 1.0,
    'ATR_MIN': 1.00,
    'RSI_MIN': 60.0
}

# --- 2. Core Technical and Fundamental Data Functions (Unchanged) ---
def get_technical_data(ticker, period_days):
    """Pulls historical data and calculates momentum, ATR, and Beta."""
    end_date = datetime.today()
    start_date_long = end_date - timedelta(days=380)
    start_date_short = end_date - timedelta(days=period_days + 5)
    
    try:
        long_data = yf.Ticker(ticker).history(start=start_date_long, end=end_date, interval="1d")
        if len(long_data) >= 252:
            mom_1y = (long_data['Close'].iloc[-1] - long_data['Close'].iloc[0]) / long_data['Close'].iloc[0]
        else:
            mom_1y = None
        beta = yf.Ticker(ticker).info.get('beta')
        short_data = yf.Ticker(ticker).history(start=start_date_short, end=end_date, interval="1d")
        mom_short = None
        if not short_data.empty and len(short_data) >= 2:
            mom_short = (short_data['Close'].iloc[-1] - short_data['Close'].iloc[0]) / short_data['Close'].iloc[0]

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
    end_date = datetime.today()
    start_date = end_date - timedelta(days=40)
    try:
        data = yf.Ticker(ticker).history(start=start_date, end=end_date, interval="1d")['Close']
        if data.empty or len(data) < 28: return None
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    except Exception:
        return None

def get_fundamentals(ticker):
    try:
        info = yf.Ticker(ticker).info
        return {
            'PRICE_TO_EARNINGS': info.get('trailingPE'), 
            'PRICE_TO_BOOK': info.get('priceToBook'), 
            'RETURN_ON_EQUITY': info.get('returnOnEquity')
        }
    except Exception:
        return {
            'PRICE_TO_EARNINGS': None, 
            'PRICE_TO_BOOK': None, 
            'RETURN_ON_EQUITY': None
        }

# --- 3. Dual Output Helper Function (Unchanged) ---
def format_output(results, criteria, title, color, emoji):
    """
    Generates both console output and HTML content for a single screen type.
    Returns the HTML segment.
    """
    
    # 1. CONSOLE OUTPUT SETUP
    print(f">>  ")
    subsection_divider = '#' * 70
    print(f">>  " + subsection_divider)
    print(f">>  --- {title} ---")
    
    if title.startswith("  CONSERVATIVE"):
         crit_str_console = f"Criteria: 1Y Mom ≥ {criteria['1Y_MOMENTUM_MIN']:.0%}, Beta ≤ {criteria['BETA_MAX']:.2f}, P/E ≤ {criteria['PRICE_TO_EARNINGS_MAX']:.0f}, ROE ≥ {criteria['RETURN_ON_EQUITY_MIN']:.0%}"
    elif title.startswith("  SPECULATIVE"):
         crit_str_console = f"Criteria: 1M Mom ≥ {criteria['1M_MOMENTUM_MIN']:.0%}, 1W Mom ≥ {criteria['1W_MOMENTUM_MIN']:.0%}, ATR ≥ ${criteria['ATR_MIN']:.2f}, RSI ≥ {criteria['RSI_MIN']:.0f}, P/B ≥ {criteria['PRICE_TO_BOOK_MIN']:.1f}"
    else:
         crit_str_console = "Error: Unknown criteria set."
    
    print(f">>  " + crit_str_console)
    print(f">>  " + subsection_divider)
    
    # 2. HTML CONTENT GENERATION SETUP
    html = ''
    html += f'<div style="border: 2px solid {color}; padding: 4px; margin-bottom: 4px; border-radius: 8px;">'
    html += f'<h4 style="color: {color}; border-bottom: 2px solid {color}; padding-bottom: 4px;">{title}</h4>'
    html += f'<p style="font-style: italic;">**Filtering Criteria:** {crit_str_console.replace("Criteria: ", "")}</p>'

    if not results:
        print(f">>  ❌ NO STOCKS PASSED THIS SCREEN.")
        html += '<p style="color: #e57f7f; font-weight: bold;">❌ NO STOCKS PASSED THIS SCREEN.</p>'
        html += '</div>'
        return html

    for ticker, result_data in results.items():
        metrics = result_data['metrics']
        pass_fail = result_data['pass_fail']

        # Console Output for passing stock
        print(f">>  ")
        print(f">>  --- Ticker: {ticker} (✅ PASSED ALL {len(criteria)} CRITERIA) ---")

        # HTML Output for passing stock
        html += f'<h4 style="color: #333; margin-top: 8px;">--- Ticker: {ticker} (✅ PASSED ALL CRITERIA) ---</h4>'
        html += '<table style="width: 100%; border-collapse: collapse; margin-bottom: 8px;">'
        html += '<tr style="background-color: #f0f0f0;"><th>Metric</th><th>Value</th><th>Required</th></tr>'
        
        for metric_key, passed in pass_fail.items():
            value = metrics.get(metric_key)
            
            # VALUE STRING DEFINITION
            if value is None:
                value_str = "N/A"
            elif 'MOMENTUM' in metric_key or 'ROE' in metric_key:
                value_str = f"{value:.2%}"
            elif metric_key == 'ATR':
                value_str = f"${value:.2f}"
            elif metric_key == 'RSI' or metric_key == 'PRICE_TO_EARNINGS':
                value_str = f"{value:.1f}"
            else: # BETA, P/B
                value_str = f"{value:.2f}"
            
            # CRITERIA KEY LOOKUP 
            if metric_key == 'BETA':
                criteria_key = 'BETA_MAX'
                op = 'Max'
            elif metric_key == 'PRICE_TO_EARNINGS':
                criteria_key = 'PRICE_TO_EARNINGS_MAX'
                op = 'Max'
            else:
                criteria_key = f'{metric_key}_MIN'
                op = 'Min'

            required_val = criteria[criteria_key]

            # FORMATTING FOR REQUIRED VALUE
            if 'MOMENTUM' in criteria_key or criteria_key == 'RETURN_ON_EQUITY_MIN':
                crit_str_req = f'{required_val:.2%}'
            elif criteria_key == 'ATR_MIN':
                crit_str_req = f'${required_val:.2f}'
            elif criteria_key == 'RSI_MIN' or criteria_key == 'PRICE_TO_EARNINGS_MAX':
                crit_str_req = f'{required_val:.1f}'
            else:
                crit_str_req = f'{required_val:.2f}'
            
            # CONSOLE OUTPUT (Individual Metric)
            print(f">>  {metric_key:<20} | Value: {value_str:<10} | Result: ✅ PASS")

            # HTML OUTPUT (Table Row)
            html += f'<tr>'
            html += f'<td style="border: 1px solid #ddd; padding: 4px;">{metric_key}</td>'
            html += f'<td style="border: 1px solid #ddd; padding: 4px;">{value_str}</td>' 
            html += f'<td style="border: 1px solid #ddd; padding: 4px; font-weight: bold;">{op} {crit_str_req}</td>'
            html += f'</tr>'

        print(f">>  " + "-" * 30) # Console separator
        print(f">>  ")
        
        html += '</table>'
    
    html += '</div>'
    return html


# ----------------------------------------------------------------------
# --- 4. NEW CORE SCREENER FUNCTION ---
# ----------------------------------------------------------------------
def safe_float_conversion(value):
    """
    Attempts to convert a value to a float. Returns None on failure 
    (e.g., if the string is 'N/A' or empty).
    """
    if isinstance(value, (int, float)):
        return value
    try:
        # Strip any surrounding whitespace and convert to float
        return float(str(value).strip())
    except (ValueError, TypeError):
        return None
        
def run_stock_screener_report(ticker_list, folder_path=r"E:\_scripts_PYTHON\_personal\_REPORT"):
    """
    Executes the dual-strategy stock screening process, prints results to the console,
    and generates a dated HTML report file.
    
    :param ticker_list: A list of stock ticker symbols (e.g., ["AAPL", "GOOGL"]).
    :param folder_path: The directory where the HTML report should be saved.
    """
    
    # --- 4a. Fetch All Raw Data ---
    raw_data = {}
    print(f">>  BEGINNING DUAL SCREENING PROCESS for {len(ticker_list)} Tickers...")
    for ticker in ticker_list:
        print(f">>  Fetching data for {ticker}...")
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
        #mom_1y_val = data['1Y_MOMENTUM']; pass_fail['1Y_MOMENTUM'] = (mom_1y_val is not None) and (mom_1y_val >= CONSERVATIVE_CRITERIA['1Y_MOMENTUM_MIN'])
        #beta_val = data['BETA']; pass_fail['BETA'] = (beta_val is not None) and (beta_val <= CONSERVATIVE_CRITERIA['BETA_MAX'])
        #pe_val = data['PRICE_TO_EARNINGS']; pass_fail['PRICE_TO_EARNINGS'] = (pe_val is not None) and (pe_val <= CONSERVATIVE_CRITERIA['PRICE_TO_EARNINGS_MAX'])
        #roe_val = data['RETURN_ON_EQUITY']; pass_fail['RETURN_ON_EQUITY'] = (roe_val is not None) and (roe_val >= CONSERVATIVE_CRITERIA['RETURN_ON_EQUITY_MIN'])
        
        # 1Y_MOMENTUM
        mom_1y_val = safe_float_conversion(data.get('1Y_MOMENTUM'))
        pass_fail['1Y_MOMENTUM'] = (mom_1y_val is not None) and (mom_1y_val >= CONSERVATIVE_CRITERIA['1Y_MOMENTUM_MIN'])
        
        # BETA
        beta_val = safe_float_conversion(data.get('BETA'))
        pass_fail['BETA'] = (beta_val is not None) and (beta_val <= CONSERVATIVE_CRITERIA['BETA_MAX'])
    
        # PRICE_TO_EARNINGS (The problematic field)
        pe_val = safe_float_conversion(data.get('PRICE_TO_EARNINGS'))
        pass_fail['PRICE_TO_EARNINGS'] = (pe_val is not None) and (pe_val <= CONSERVATIVE_CRITERIA['PRICE_TO_EARNINGS_MAX'])
    
        # RETURN_ON_EQUITY
        roe_val = safe_float_conversion(data.get('RETURN_ON_EQUITY'))
        pass_fail['RETURN_ON_EQUITY'] = (roe_val is not None) and (roe_val >= CONSERVATIVE_CRITERIA['RETURN_ON_EQUITY_MIN'])
    
        if sum(pass_fail.values()) == len(CONSERVATIVE_CRITERIA):
            conservative_passes[ticker] = {'metrics': data, 'pass_fail': pass_fail}

    # --- 4c. Speculative Screen Evaluation ---
    speculative_passes = {}
    for ticker, data in raw_data.items():
        pass_fail = {}
        m1_val = data['1M_MOMENTUM']; pass_fail['1M_MOMENTUM'] = (m1_val is not None) and (m1_val >= SPECULATIVE_CRITERIA['1M_MOMENTUM_MIN'])
        m1w_val = data['1W_MOMENTUM']; pass_fail['1W_MOMENTUM'] = (m1w_val is not None) and (m1w_val >= SPECULATIVE_CRITERIA['1W_MOMENTUM_MIN'])
        atr_val = data['ATR']; pass_fail['ATR'] = (atr_val is not None) and (atr_val >= SPECULATIVE_CRITERIA['ATR_MIN'])
        rsi_val = data['RSI']; pass_fail['RSI'] = (rsi_val is not None) and (rsi_val >= SPECULATIVE_CRITERIA['RSI_MIN'])
        pb_val = data['PRICE_TO_BOOK']; pass_fail['PRICE_TO_BOOK'] = (pb_val is not None) and (pb_val >= SPECULATIVE_CRITERIA['PRICE_TO_BOOK_MIN'])
        
        if sum(pass_fail.values()) == len(SPECULATIVE_CRITERIA):
            speculative_passes[ticker] = {'metrics': data, 'pass_fail': pass_fail}


    # --- 4d. EXECUTE DUAL OUTPUT (Console & HTML) ---
    report_content = ""
    report_content += format_output(conservative_passes, CONSERVATIVE_CRITERIA, "  CONSERVATIVE SCREEN (Value/Quality Focus)", "#007bff", "#️")

    report_content += format_output(speculative_passes, SPECULATIVE_CRITERIA, "  SPECULATIVE SCREEN (Volatility/Momentum Focus)", "#dc3545", "#")

    # 4e. SAVE TO FILE
    CURRENT_DATE = datetime.now().strftime("%Y%m%d")
    FILE_NAME = f"{CURRENT_DATE}_Momentum.html"
    FULL_PATH = os.path.join(folder_path, FILE_NAME)

    # 4f. Create Full HTML Structure
    html_report = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{CURRENT_DATE} - Momentum Stock Screener Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f9; }}
        h1 {{ color: #333; border-bottom: 3px solid #000; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ border: 1px solid #ddd; padding: 4px; text-align: left; }}
        th {{ background-color: #e9ecef; color: #333; }}
        .conservative {{ border-color: #007bff !important; }}
        .speculative {{ border-color: #dc3545 !important; }}
    </style>
</head>
<body>
    <h2>Momentum Stock Screener Report - {datetime.now().strftime("%Y-%m-%d")}</h2>
    <p>Report Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    
    {report_content}

    <hr style="margin-top: 8px;"/>
</body>
</html>
"""

    # 4f.a. Create a HTML Section to Integrate into another report
    html_section = f"""{report_content}</br><hr style="margin-top: 3px;"/>"""    
    
    # 4g. Write to File with UTF-8 encoding
    try:
        # DEVNOTE:  Turn off the Generation of a Separate Report for now
        # os.makedirs(folder_path, exist_ok=True) 
        # with open(FULL_PATH, 'w', encoding='utf-8') as f:
        #     f.write(html_report)
        
        print(">>  ")
        print(">>  " + "=" * 70)
        print(">>  ✅ SUCCESS! HTML Momentum Section Integrated into overall Generated Report ...")
        # print(f">>  File Path: {FULL_PATH}")
        print(">>  " + "=" * 70)

    except Exception as e:
        print(">>  ")
        print(">>  " + "!" * 70)
        print(f">>  ❌ ERROR: Could not save the file to {folder_path}")
        print(f">>  Reason: {e}")
        print(">>  " + "!" * 70)
        
    return html_section

# ----------------------------------------------------------------------
# --- 5. EXECUTION BLOCK ---
# ----------------------------------------------------------------------
# if __name__ == "__main__":
#     
#     # 1. Define the original stock list
#     TICKER_LIST_AI = ["ANGO","STLA","NMAX","GPRK","GTLB","XPEV","BROS","BMRN","LI","COCP","INSE","TSQ","NIO","HNI","AVNT","WWW","IBRX","HBAN","KD","BIP","GBCI","KDP","BCS"]
# 
#     # 2. Example: Run the full screening process using the new function
#     print("--- STARTING SCRIPT EXECUTION VIA FUNCTION CALL ---")
#     final_report_path = run_stock_screener_report(TICKER_LIST_AI)
#     
#     # Example of calling the function with a different list:
#     # TICKER_LIST_TECH = ["AAPL", "MSFT", "NVDA", "ADBE"]
#     # run_stock_screener_report(TICKER_LIST_TECH)