import os
import sys
from datetime import datetime

# Get the path to the 'utils' folder
utils = os.path.join(os.path.dirname(__file__), '_UTILS')

# Add the folders to the system path
sys.path.append(utils)

# Now you can import the script as a module
import momentum

def process_consolidated_report(reporttype: str, all_tickers: dict):
    """
    Generates a single, consolidated HTML report and prints the report details
    to the console.

    Args:
        all_tickers (dict): A dictionary where keys are the screener titles
                            and values are lists of stock ticker symbols.
    """
    # Define file path and name
    report_output_dir = "E:/_scripts_PYTHON/_personal/_REPORT"
    today_date_str = datetime.now().strftime('%Y%m%d')
    report_filename = f"{today_date_str}_Process_Screener_{reporttype}_Report.html"
    report_path = os.path.join(report_output_dir, report_filename)
    
    # Ensure the directory exists
    os.makedirs(report_output_dir, exist_ok=True)

    finviz_URL_Screener_Prefix = "https://elite.finviz.com/screener.ashx?v=341&o=-change&t="

    # Start writing the HTML report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("<!DOCTYPE html>\n")
        f.write("<html>\n")
        f.write("<head>\n")
        f.write("<title>FINVIZ Consolidated Stock Screener Report</title>\n")
        f.write("<style>\n")
        f.write("body { font-family: Arial, sans-serif; margin: 20px; }\n")
        f.write("h1 { color: #333; }\n")
        f.write("h2 { color: #555; border-bottom: 2px solid #ddd; padding-bottom: 5px; }\n")
        f.write("ul { list-style-type: none; padding: 0; }\n")
        f.write("li { margin-bottom: 5px; }\n")
        f.write("a { color: #007bff; text-decoration: none; }\n")
        f.write("a:hover { text-decoration: underline; }\n")
        f.write("</style>\n")
        f.write("</head>\n")
        f.write("<body>\n")
        f.write(f"<h2>FINVIZ Consolidated Stock Screener Report - Generated - {datetime.now().strftime('%B %d, %Y')}</h2>\n")
        f.write("<br>")

        print(f">>  ##############################################")
        print(f">>  # CONSOLIDATED FINVIZ STOCK SCREENER REPORT #")
        print(f">>  ##############################################")
        print(f">>  ")

        for reportsection, tickers in all_tickers.items():
            f.write(f"<h3>{reportsection}</h3>\n")
            
            # Print to console
            print(f">>  ##########")
            print(f">>  {reportsection}")
            
            if not tickers:
                f.write("<p>No tickers found.</p>\n")
                print(f">>  No tickers found.")
                print(f">> ")
                continue

            # Concatenate tickers into a single, comma-separated string
            ticker_string = ",".join(tickers)
            
            # Construct the final URL
            finviz_URL_Screener = finviz_URL_Screener_Prefix + ticker_string
            
            # Write to HTML
            f.write(f"<p><strong>Tickers:</strong> {ticker_string}</p>\n")
            f.write(f"<p><strong>URL:</strong> <a href=\"{finviz_URL_Screener}\" target=\"_blank\">View Stocks on FinViz</a></p>")

            # Print to console
            print(f">>  Tickers: {ticker_string}")
            print(f">>  URL: \n>>  {finviz_URL_Screener}")
            print(f">> ")
            
            # Print to console
            print(f">>  Analyze StockList Momentum: ")
            print(f">> ") 
           
            # Convert the string to a list of strings
            ticker_string_array = ticker_string.split(',')

            ticker_momentum_analysis_section = momentum.run_stock_screener_report(ticker_string_array)
            f.write(ticker_momentum_analysis_section)
            
            print(f">>  StockList Momentum Analysis Complete ...")
            print(f">> ") 
            
        f.write("""<p style="font-size: small; color: #666;">Data provided by FINVIZ Services and Yahoo Finance (yfinance).</p>\n""")
        f.write("</body>\n")
        f.write("</html>\n")

    print(f">> Report saved to: {report_path}")