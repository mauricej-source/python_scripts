import csv
from collections import Counter, defaultdict
import os
from datetime import datetime, timedelta

def find_frequent_ticker_subcategory_counts_grouped(filename="news_screener.dict"):
    """
    Reads a file, filters rows by date (last 45 days), counts the occurrences 
    of each unique (Ticker, Subcategory) pair, and prints the result to 
    the console and generates an HTML table with a consolidated screener link.
    """
    # 1. Test if the file exists
    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found. Cannot proceed.")
        return

    # --- Date Range Calculation ---
    current_date = datetime.now().date()
    past_cutoff_date = current_date - timedelta(days=45)
    current_date_str = current_date.strftime("%Y%m%d")
    past_cutoff_date_str = past_cutoff_date.strftime("%Y%m%d")

    print(f"Filtering data between {past_cutoff_date_str} and {current_date_str} (Last 45 Days).")
    
    # --- Data Processing ---
    ticker_subcategory_pairs = []
    try:
        with open(filename, 'r', newline='') as file:
            reader = csv.reader(file)
            try:
                next(reader) # Skip header
            except StopIteration:
                print(f"File '{filename}' is empty.")
                return

            for row in reader:
                if len(row) >= 4:
                    file_date_str = row[0].strip()
                    
                    # Apply the date filter
                    if file_date_str >= past_cutoff_date_str and file_date_str <= current_date_str:
                        subcategory = row[2].strip()
                        tickers_in_row = [ticker.strip() for ticker in row[3:] if ticker.strip()]

                        for ticker in tickers_in_row:
                            ticker_subcategory_pairs.append((ticker, subcategory))
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return

    # --- Count and Filter Tickers ---
    pair_counts = Counter(ticker_subcategory_pairs)
    frequent_pairs = []
    max_ticker_occurrence = defaultdict(int)

    # Filter for counts > 2 and track max occurrence per ticker
    for (ticker, subcategory), count in pair_counts.items():
        if count > 2:
            item = {'Ticker': ticker, 'SubCategory': subcategory, 'Occurrences': count}
            frequent_pairs.append(item)
            
            if count > max_ticker_occurrence[ticker]:
                max_ticker_occurrence[ticker] = count
    
    if not frequent_pairs:
        print("\nNo unique Ticker/SubCategory combinations were found with more than 2 occurrences in the specified date range. No output generated.")
        return

    # --- Sorting ---
    frequent_pairs.sort(key=lambda item: (
        -max_ticker_occurrence[item['Ticker']], 
        item['Ticker'],                           
        -item['Occurrences']                      
    ))

    # ----------------------------------------------------
    # --- Console Output (Unchanged) ---
    # ----------------------------------------------------
    print("\n--- Stock Tickers (by SubCategory) with more than 2 total occurrences ---\n")

    TICKER_WIDTH = 10
    SUBCAT_WIDTH = 25
    COUNT_WIDTH = 15
    TOTAL_WIDTH = TICKER_WIDTH + SUBCAT_WIDTH + COUNT_WIDTH

    print(f"{'Ticker':<{TICKER_WIDTH}}{'SubCategory':<{SUBCAT_WIDTH}}{'Occurrences':<{COUNT_WIDTH}}")
    print("-" * TOTAL_WIDTH)

    current_ticker = None
    for item in frequent_pairs:
        if item['Ticker'] != current_ticker and current_ticker is not None:
            print("-" * TOTAL_WIDTH)
        
        print(f"{item['Ticker']:<{TICKER_WIDTH}}{item['SubCategory']:<{SUBCAT_WIDTH}}{item['Occurrences']:<{COUNT_WIDTH}}")
        current_ticker = item['Ticker']
    
    print("-" * TOTAL_WIDTH)


    # ----------------------------------------------------
    # --- HTML Generation (Refactored) ---
    # ----------------------------------------------------

    # 1. Extract and format unique tickers for the screener link
    unique_tickers = sorted(list(set(item['Ticker'] for item in frequent_pairs)))
    ticker_screener_list = ",".join(unique_tickers)
    BASE_SCREENER_URL = "https://elite.finviz.com/screener.ashx?v=111&t="
    screener_url = f"{BASE_SCREENER_URL}{ticker_screener_list}"
    screener_link_html = f'<p><strong>Consolidated Screener:</strong> <a href="{screener_url}" target="_blank">View All {len(unique_tickers)} Tickers on FinViz</a></p>'


    # HTML file details
    current_date_prefix = datetime.now().strftime("%Y%m%d")
    html_filename = f"{current_date_prefix}_MostFrequent_News.html"
    BASE_FINVIZ_URL = "https://elite.finviz.com/quote.ashx?t="

    html_content = []
    html_content.append("<!DOCTYPE html>")
    html_content.append("<html lang='en'>")
    html_content.append("<head>")
    html_content.append("    <meta charset='UTF-8'>")
    html_content.append(f"    <title>Most Frequent Tickers by News SubCategory ({past_cutoff_date_str} to {current_date_str})</title>")
    html_content.append("    <style>")
    html_content.append("        body { font-family: Arial, sans-serif; margin: 20px; }")
    html_content.append("        h1 { color: #333; }")
    html_content.append("        table { width: 50%; border-collapse: collapse; margin-top: 20px; }")
    html_content.append("        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }")
    html_content.append("        th { background-color: #f2f2f2; }")
    html_content.append("        tr.ticker-group-separator td { border-top: 3px solid #000; background-color: #fff; height: 5px; padding: 0; }")
    html_content.append("        td:nth-child(3) { text-align: center; } /* Center Occurrences */")
    html_content.append("    </style>")
    html_content.append("</head>")
    html_content.append("<body>")
    html_content.append(f"<h1>Most Frequent Tickers by SubCategory (Occurrences > 2)</h1>")
    html_content.append(f"<h2>Data Filtered: {past_cutoff_date_str} to {current_date_str}</h2>")
    
    # NEW: Insert the consolidated screener link
    html_content.append(screener_link_html) 
    
    html_content.append("<table>")
    
    # Table Header
    html_content.append("    <thead>")
    html_content.append("        <tr>")
    html_content.append("            <th>Ticker</th>")
    html_content.append("            <th>SubCategory</th>")
    html_content.append("            <th>Occurrences</th>")
    html_content.append("        </tr>")
    html_content.append("    </thead>")
    html_content.append("    <tbody>")

    # Table Data
    current_ticker = None
    for item in frequent_pairs:
        if item['Ticker'] != current_ticker and current_ticker is not None:
            html_content.append("        <tr class='ticker-group-separator'><td colspan='3'></td></tr>")
        
        ticker = item['Ticker']
        # FinViz quote link for individual tickers
        ticker_link = f'<a href="{BASE_FINVIZ_URL}{ticker}" target="_blank">{ticker}</a>'
        
        html_content.append("        <tr>")
        html_content.append(f"            <td>{ticker_link}</td>")
        html_content.append(f"            <td>{item['SubCategory']}</td>")
        html_content.append(f"            <td style='text-align: center;'>{item['Occurrences']}</td>")
        html_content.append("        </tr>")
        current_ticker = item['Ticker']
        
    html_content.append("    </tbody>")
    html_content.append("</table>")
    html_content.append("</body>")
    html_content.append("</html>")

    # Write the content to the file
    try:
        with open(html_filename, 'w') as f:
            f.write('\n'.join(html_content))
        print(f"\n✅ Successfully generated HTML file: {html_filename}")
    except Exception as e:
        print(f"An error occurred while writing the HTML file: {e}")

# Execute the function
find_frequent_ticker_subcategory_counts_grouped()